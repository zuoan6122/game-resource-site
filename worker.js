export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type'
    };

    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    // 记录查看量（点击弹窗）
    if (request.method === 'POST' && path === '/click') {
      const game = url.searchParams.get('game');
      if (!game) return new Response('missing game', { status: 400, headers: corsHeaders });
      const count = parseInt(await env.GAME_CLICKS.get(game)) || 0;
      await env.GAME_CLICKS.put(game, String(count + 1));
      return new Response('ok', { headers: corsHeaders });
    }

    // 记录下载量（点击夸克网盘跳转）
    if (request.method === 'POST' && path === '/download') {
      const game = url.searchParams.get('game');
      if (!game) return new Response('missing game', { status: 400, headers: corsHeaders });
      const key = 'dl:' + game;
      const count = parseInt(await env.GAME_CLICKS.get(key)) || 0;
      await env.GAME_CLICKS.put(key, String(count + 1));
      return new Response('ok', { headers: corsHeaders });
    }

    // 热门排行（按查看量）
    if (path === '/top') {
      const limit = parseInt(url.searchParams.get('limit')) || 10;
      const items = await listViews(env);
      items.sort((a, b) => b.count - a.count);
      return new Response(JSON.stringify(items.slice(0, limit)), { headers: { 'Content-Type': 'application/json', ...corsHeaders } });
    }

    // 全部查看量
    if (path === '/all') {
      const items = await listViews(env);
      return new Response(JSON.stringify(items), { headers: { 'Content-Type': 'application/json', ...corsHeaders } });
    }

    // 全部下载量
    if (path === '/all-downloads') {
      const items = await listDownloads(env);
      return new Response(JSON.stringify(items), { headers: { 'Content-Type': 'application/json', ...corsHeaders } });
    }

    return new Response('not found', { status: 404, headers: corsHeaders });
  }
}

async function listViews(env) {
  const list = await env.GAME_CLICKS.list();
  const items = [];
  for (const key of list.keys) {
    if (key.name.startsWith('dl:')) continue;
    const count = parseInt(await env.GAME_CLICKS.get(key.name)) || 0;
    items.push({ name: key.name, count });
  }
  return items;
}

async function listDownloads(env) {
  const list = await env.GAME_CLICKS.list();
  const items = [];
  for (const key of list.keys) {
    if (!key.name.startsWith('dl:')) continue;
    const count = parseInt(await env.GAME_CLICKS.get(key.name)) || 0;
    items.push({ name: key.name.slice(3), count });
  }
  return items;
}
