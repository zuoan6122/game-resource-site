// 游戏资源站后端（腾讯云开发 CloudBase 云函数）
// 通过 HTTP 网关暴露：
//   统计：/click、/download、/top、/all、/all-downloads
//   留言：GET /messages、POST /messages
const cloud = require('wx-server-sdk')
const https = require('https')
cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV })
const db = cloud.database()

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type'
}

function ok(data) {
  return {
    statusCode: 200,
    headers: Object.assign({ 'Content-Type': 'application/json' }, CORS_HEADERS),
    body: JSON.stringify(data)
  }
}

// 敏感词过滤（后端二次过滤，与前端词库保持一致）
const BAD_WORDS = ['操', 'fuck', 'shit', 'sb', '傻逼', '草泥马', '鸡巴', '妈的', '狗日', '去死', '王八蛋', '屁眼', '婊子', 'whore', 'dick', 'asshole', 'bastard', 'crap', 'damn']
function filterProfanity(text) {
  let result = text
  BAD_WORDS.forEach(word => {
    const re = new RegExp(word, 'gi')
    result = result.replace(re, '**')
  })
  return result
}

// 集合不存在时自动创建（已存在则忽略）
async function ensureCollection(name) {
  try {
    await db.createCollection(name)
  } catch (e) {
    // 已存在或权限不足，忽略
  }
}

// 获取客户端 IP（用于频率限制）
function getClientIp(event) {
  if (event.requestContext && event.requestContext.sourceIp) return event.requestContext.sourceIp
  const h = event.headers || {}
  const fwd = h['x-forwarded-for'] || h['X-Forwarded-For'] || ''
  if (fwd) return fwd.split(',')[0].trim()
  return 'unknown'
}

// 简单 HTTPS GET，返回 JSON（失败或超时返回 null）
function httpGetJson(url, timeout = 3000) {
  return new Promise((resolve) => {
    const req = https.get(url, (res) => {
      let data = ''
      res.on('data', (chunk) => { data += chunk })
      res.on('end', () => {
        try { resolve(JSON.parse(data)) } catch (e) { resolve(null) }
      })
    })
    req.on('error', () => resolve(null))
    req.setTimeout(timeout, () => { req.destroy(); resolve(null) })
  })
}

// 根据 IP 识别省市（格式：省市，如"广东深圳"；直辖市如"北京"）
async function getRegion(ip) {
  try {
    const data = await httpGetJson('https://ip9.com.cn/get?ip=' + encodeURIComponent(ip))
    if (data && data.ret === 200 && data.data && data.data.prov) {
      const prov = data.data.prov
      const city = data.data.city
      if (!city || city === prov) return prov
      return prov + city
    }
  } catch (e) {}
  return '未知'
}

// 原子自增；文档不存在时创建
// 注意：doc().update() 在文档不存在时是静默空操作（不报错也不创建），
// 所以必须先 add 创建，_id 冲突（文档已存在）时再 update 自增
async function increment(game, field) {
  const col = db.collection('counters')
  try {
    await col.add({
      data: {
        _id: game,
        views: field === 'views' ? 1 : 0,
        downloads: field === 'downloads' ? 1 : 0
      }
    })
  } catch (e) {
    await col.doc(game).update({
      data: { [field]: db.command.inc(1) }
    })
  }
}

// 分页拉取全部文档（单次 get 上限 100 条）
async function getAllDocs() {
  const MAX = 100
  const col = db.collection('counters')
  let all = []
  let skip = 0
  for (;;) {
    const res = await col.skip(skip).limit(MAX).get()
    all = all.concat(res.data)
    if (res.data.length < MAX) break
    skip += MAX
  }
  return all
}

// 留言：提交（脏话过滤 + 50字限制 + 30秒一条 + IP定位省市）
async function postMessage(event) {
  let body = {}
  try {
    body = JSON.parse(event.body || '{}')
  } catch (e) {}

  const content = (body.content || '').trim()
  if (!content) return ok({ code: 1, message: '留言内容不能为空' })
  if (content.length > 50) return ok({ code: 1, message: '留言最多50个字' })

  // 频率限制：按 IP 每30秒一条
  const ip = getClientIp(event)
  const rateCol = db.collection('msg_rate')
  const now = Date.now()
  try {
    await rateCol.add({ data: { _id: ip, lastTime: now } })
  } catch (e) {
    const doc = await rateCol.doc(ip).get()
    const last = (doc.data && doc.data.lastTime) || 0
    if (now - last < 30000) {
      const wait = Math.ceil((30000 - (now - last)) / 1000)
      return ok({ code: 1, message: '发送太频繁，请' + wait + '秒后再试' })
    }
    await rateCol.doc(ip).update({ data: { lastTime: now } })
  }

  const name = (body.name || '').trim().slice(0, 10) || '匿名用户'
  const filtered = filterProfanity(content)
  const region = await getRegion(ip)
  const doc = await db.collection('messages').add({
    data: {
      name: name,
      content: filtered,
      region: region,
      time: new Date().toISOString()
    }
  })
  return ok({ code: 0, data: { id: doc._id, region: region } })
}

// 留言：获取列表（按时间倒序）
async function getMessages(event) {
  const limit = parseInt((event.queryStringParameters && event.queryStringParameters.limit) || '20', 10)
  const res = await db.collection('messages')
    .orderBy('time', 'desc')
    .limit(Math.min(limit, 50))
    .get()
  return ok({ code: 0, data: res.data })
}

ensureCollection('messages')
ensureCollection('msg_rate')

exports.main = async (event) => {
  const { httpMethod, path, queryStringParameters } = event

  if (httpMethod === 'OPTIONS') {
    return { statusCode: 200, headers: CORS_HEADERS, body: '' }
  }

  try {
    if (path === '/click' && httpMethod === 'POST') {
      const game = queryStringParameters && queryStringParameters.game
      if (!game) return ok({ error: 'missing game' })
      await increment(game, 'views')
      return ok({ ok: true })
    }

    if (path === '/download' && httpMethod === 'POST') {
      const game = queryStringParameters && queryStringParameters.game
      if (!game) return ok({ error: 'missing game' })
      await increment(game, 'downloads')
      return ok({ ok: true })
    }

    if (path === '/top' && httpMethod === 'GET') {
      const limit = parseInt((queryStringParameters && queryStringParameters.limit) || '10', 10)
      const res = await db.collection('counters')
        .orderBy('views', 'desc')
        .limit(Math.min(limit, 100))
        .get()
      return ok(res.data.map(d => ({ name: d._id, count: d.views || 0 })))
    }

    if (path === '/all' && httpMethod === 'GET') {
      const docs = await getAllDocs()
      return ok(docs.map(d => ({ name: d._id, count: d.views || 0 })))
    }

    if (path === '/all-downloads' && httpMethod === 'GET') {
      const docs = await getAllDocs()
      return ok(docs.map(d => ({ name: d._id, count: d.downloads || 0 })))
    }

    if (path === '/messages' && httpMethod === 'GET') {
      return await getMessages(event)
    }

    if (path === '/messages' && httpMethod === 'POST') {
      return await postMessage(event)
    }

    return { statusCode: 404, headers: CORS_HEADERS, body: JSON.stringify({ error: 'Not Found' }) }
  } catch (e) {
    return { statusCode: 500, headers: CORS_HEADERS, body: JSON.stringify({ error: String(e) }) }
  }
}
