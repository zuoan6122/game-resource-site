# 左岸资源分享站

一个无需登录注册、打开即进入主页的手机游戏资源分享网站，覆盖**安卓 / NS / PC** 三大平台共 **2125 款游戏**。前端部署在 GitHub Pages，数据通过 jsDelivr 国内节点加速加载，热门统计由腾讯云 CloudBase 云函数提供。

## 在线地址

- GitHub Pages：`https://zuoan6122.github.io/game-resource-site/`
- 数据源：jsDelivr 国内节点（`testingcf.jsdelivr.net`），8 秒超时自动回退到 GitHub Pages 同源 `games.json`

## 功能特点

- ✅ **三大平台**：安卓 / NS / PC 游戏分类浏览
- ✅ **14 个游戏分类**：策略、动作、冒险、角色扮演、模拟、竞速、街机、射击、卡牌、体育、音乐、益智、生存、格斗
- ✅ **热门统计**：基于腾讯云 CloudBase 云函数，统计每款游戏的点击量 / 下载量
- ✅ **热度榜**：点击搜索框弹出热门游戏榜单
- ✅ **留言板**：右侧浮动按钮展开，访客可留言求游戏；自动识别省市、脏话过滤、30 秒限流
- ✅ **排序**：支持默认 / 热度 / 下载量三种排序方式
- ✅ **搜索**：平台下拉框 + 关键词组合搜索（点击搜索按钮或回车触发）
- ✅ **深色 / 浅色主题切换**：浅色主题背景 `#f9f9f9`
- ✅ **响应式卡片网格**：桌面 5 列、平板 4 列、手机 3 列、小屏手机 2 列
- ✅ **轮播推荐位**：顶部展示平台推荐
- ✅ **现代图标**：全部使用内联 SVG 图标
- ✅ **完全静态 + 云函数**：前端纯 HTML/CSS/JS，热门统计由 CloudBase 云函数提供

## 项目结构

```
game-resource-site/
├── index.html          # 主页面
├── styles.css          # 样式文件（主题变量、卡片、筛选栏、弹窗）
├── script.js           # 逻辑（数据加载、筛选、搜索、统计、主题、轮播）
├── data/
│   ├── games.json      # 游戏数据（同源回退）
│   └── games-data.js   # 游戏数据（jsDelivr CDN 加载，暴露 window.GAMES_DATA）
├── cloudbase/          # CloudBase 云函数源码（热门统计 + 留言板后端）
│   ├── index.js        # 云函数主逻辑
│   └── package.json    # 依赖（wx-server-sdk）
└── README.md           # 说明文档
```

## 后端架构（CloudBase 云函数 `game-counter-v2`）

- **数据库**：
  - `counters` 集合 — 按游戏名记录 `views` / `downloads`
  - `messages` 集合 — 留言记录（`name` / `content` / `region` / `time`）
  - `msg_rate` 集合 — 留言频率限制（按 IP 记录上次发送时间）
- **接口**：
  - `GET /top?limit=N` — 热门游戏排行
  - `GET /all` — 全部点击量
  - `GET /all-downloads` — 全部下载量
  - `POST /click` — 点击计数
  - `POST /download` — 下载计数
  - `GET /messages?limit=N` — 获取留言列表（按时间倒序）
  - `POST /messages` — 提交留言
- **前端**：`script.js` 中 `ENABLE_CLOUD_STATS` 开关控制；浏览器 localStorage 去重（同一浏览器每款游戏只计一次）

## 留言板规则

- **入口**：页面右侧浮动留言按钮（橙色圆形），悬停显示提示气泡，点击展开留言面板
- **提交**：输入内容（最多 50 字）点击发送，成功后按钮显示"留言成功，X秒后可继续留言"倒计时
- **地区**：后端根据访客 IP 自动识别省市（如"广东深圳"，直辖市显示"北京"），通过 `ip9.com.cn` 免费接口，失败存"未知"
- **脏话过滤**：前后端双重过滤，敏感词替换为 `**`
- **限流**：同一 IP 每 30 秒最多一条
- **管理**：CloudBase 控制台 → 数据库 → `messages` 集合，可手动删除不当留言

## 如何添加游戏

1. 编辑 `data/games.json` 添加游戏记录
2. 同步更新 `data/games-data.js`（两者数据必须一致）
3. 递增 `script.js` 中的 `GAMES_DATA_VERSION` 常量，以刷新 CDN 和浏览器缓存

游戏数据结构：

```json
{
    "title": "游戏名称",
    "category": "strategy",
    "platform": "android",
    "tags": ["标签1", "标签2"],
    "coverImage": "图片URL（留空则显示占位符）",
    "downloadUrl": "夸克网盘链接"
}
```

**分类值（category）**：`strategy` / `action` / `adventure` / `rpg` / `simulation` / `racing` / `arcade` / `shooter` / `card` / `sports` / `music` / `puzzle` / `survival` / `fighting`

**平台值（platform）**：`android` / `ns` / `pc`

## 部署

1. 将代码推送到 GitHub 仓库 `zuoan6122/game-resource-site`
2. 仓库 **Settings → Pages**，选择 `main` 分支 / `/ (root)` 目录
3. 等待 1-2 分钟自动部署
4. 修改 `script.js` 后，需递增 `index.html` 中 script 标签的版本号（如 `script.js?v=42`）以绕过浏览器缓存

## 常见问题

### Q: 数据加载慢怎么办？

A: 数据通过 jsDelivr 国内节点（`testingcf.jsdelivr.net`）加载，加载失败或 8 秒超时自动回退到 GitHub Pages 同源 `games.json`。

### Q: 热度榜为什么是空的？

A: 热度榜数据来自 CloudBase 数据库，需要真实访客点击 / 下载游戏后才会积累数据。数据库为空时热度榜不显示，属正常现象。

### Q: 如何重置某款游戏的计数？

A: 在 CloudBase 控制台的 `counters` 集合中删除对应游戏名的文档即可。

## 许可证

本项目仅供学习交流使用。
