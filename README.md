# 游戏资源分享站 - GitHub Pages Demo

一个无需登录注册、打开即进入主页的手机游戏资源分享网站。采用**橙色调 + 深灰/浅灰底白卡片**的现代游戏仪表盘风格，可在 GitHub Pages 免费部署。

## 功能特点

- ✅ **14个游戏分类筛选**：策略、动作、冒险、角色扮演、模拟、竞速、街机、射击、卡牌、体育、音乐、益智、生存、格斗
- ✅ **顶部横排筛选栏**：分类标签直接平铺在页面上方（非下拉框），整齐两行排列，点击某分类立即筛选对应游戏
- ✅ **深色 / 浅色主题切换**：点击右侧浮动按钮即可切换（🌙 月亮 / ☀️ 太阳），标题栏浅色下为纯白
- ✅ **实时搜索**：支持按游戏名称和标签搜索
- ✅ **右侧悬浮按钮**：主题切换 + 返回顶部（滚动超过 300px 后出现）
- ✅ **轮播推荐位**：顶部展示热门推荐、新上架、编辑精选
- ✅ **圆角卡片网格**：灰底白卡片、明显圆角、卡片间隙透出背景色，封面图驱动
- ✅ **现代图标**：全部使用内联 SVG 图标（logo、搜索、占位手柄、主题、返回箭头）
- ✅ **响应式设计**：适配桌面、平板、手机
- ✅ **完全静态**：无需后端，纯 HTML/CSS/JS，可在 GitHub Pages 免费托管

## 如何在 GitHub Pages 上托管

### 方法1：使用 GitHub 仓库的 Pages 功能（推荐）

1. **创建 GitHub 仓库**
   - 在 GitHub 上创建一个新仓库（例如：`game-resource-site`）
   - 将本项目的所有文件上传到仓库

2. **启用 GitHub Pages**
   - 进入仓库的 **Settings** → **Pages**
   - 在 **Build and deployment** → **Branch** 中选择：
     - Branch: `main` 或 `master`
     - Folder: `/ (root)`
   - 点击 **Save**

3. **访问网站**
   - 等待 1-2 分钟，GitHub 会自动部署
   - 访问：`https://你的用户名.github.io/你的仓库名/`

### 方法2：使用个人域名

1. **购买域名**（可选）
   - 在阿里云、腾讯云等购买域名

2. **配置 DNS**
   - 在域名管理中添加 CNAME 记录：
     - 主机记录：`@`
     - 记录值：`你的用户名.github.io`
   - 或者添加 A 记录指向 GitHub Pages 的 IP

3. **在仓库中配置**
   - 在仓库根目录创建 `CNAME` 文件
   - 文件内容为你的域名（例如：`www.yourdomain.com`）

## 项目结构

```
game-resource-site/
├── index.html          # 主页面
├── styles.css          # 样式文件（主题变量、卡片、筛选栏、浮动按钮）
├── script.js           # JavaScript逻辑（数据、筛选、搜索、主题、返回顶部、轮播）
├── data/
│   └── games.json      # 游戏数据
└── README.md           # 说明文档
```

## 如何添加游戏

### 方法1：直接修改 `data/games.json`

编辑 `data/games.json` 文件，添加游戏数据：

```json
{
    "id": 31,
    "title": "游戏名称",
    "category": "rpg",
    "tags": ["标签1", "标签2", "标签3"],
    "coverImage": "图片URL（留空则显示占位符）",
    "downloadUrl": "下载链接"
}
```

**分类值（category）**：
- `strategy` - 策略
- `action` - 动作
- `adventure` - 冒险
- `rpg` - 角色扮演
- `simulation` - 模拟
- `racing` - 竞速
- `arcade` - 街机
- `shooter` - 射击
- `card` - 卡牌
- `sports` - 体育
- `music` - 音乐
- `puzzle` - 益智
- `survival` - 生存
- `fighting` - 格斗

### 方法2：修改 `script.js` 内置数据

当前 demo 的 30 个示例游戏直接写在 `script.js` 开头的 `gamesData` 数组中，你也可以直接在这里增删游戏。

### 方法3：启用从 JSON 文件加载数据

1. 在 `script.js` 文件末尾，取消注释以下代码：

```javascript
async function init() {
    const games = await loadGamesFromJSON();
    if (games.length > 0) {
        gamesData = games;
        renderGames();
    }
}
init();
```

2. 确保在 `script.js` 开头将 `gamesData` 声明为 `let` 而不是 `const`：

```javascript
let gamesData = [];
```

## 如何添加封面图

### 方案1：使用图床

1. 将游戏封面图上传到图床服务（如阿里云OSS、腾讯云COS、Gitee等）
2. 获取图片的外链URL
3. 在 `games.json` 中填写 `coverImage` 字段

示例：
```json
{
    "id": 1,
    "title": "原神",
    "category": "rpg",
    "tags": ["角色扮演", "开放世界", "冒险"],
    "coverImage": "https://your-cdn.com/images/genshin-impact.jpg",
    "downloadUrl": "#"
}
```

### 方案2：使用 GitHub 图床

1. 在 GitHub 仓库中创建 `images` 文件夹
2. 上传封面图片到 `images` 文件夹
3. 使用 GitHub 的 raw 链接

示例链接格式：
```
https://raw.githubusercontent.com/你的用户名/你的仓库名/main/images/游戏名称.jpg
```

**注意**：GitHub 的 raw 链接在国内访问可能较慢或不稳定。

### 方案3：使用占位图

如果不填写 `coverImage` 字段或留空，卡片会显示跟随主题自适应的手柄图标占位符（深色浅色都会自动匹配背景色）。

## 自定义样式

### 修改主题颜色

配色集中在 `styles.css` 顶部的两个主题变量块中：

```css
:root {               /* 深色主题 */
    --accent-color: #e8590c;   /* 主色调 - 橙色 */
    --accent-hover: #c74a0a;   /* 悬停颜色 */
    --bg-primary: #1a1d21;     /* 主背景 */
    --bg-tertiary: #2a2f35;    /* 卡片背景 */
    --header-bg: #1f2428;      /* 标题栏背景 */
}

body.light-theme {    /* 浅色主题 */
    --accent-color: #e8590c;
    --bg-tertiary: #ffffff;    /* 卡片纯白 */
    --header-bg: #ffffff;      /* 标题栏纯白 */
}
```

### 修改圆角大小

`styles.css` 顶部定义了统一的圆角变量：

```css
--radius-sm: 10px;   /* 按钮等小幅圆角 */
--radius-md: 14px;
--radius-lg: 18px;   /* 卡片、容器大圆角 */
```

### 修改卡片尺寸

在 `styles.css` 的 `.game-grid` 部分：

```css
.game-grid {
    grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
    /* 修改 230px 为你想要的卡片宽度 */
}
```

### 修改筛选栏列数（两行）

筛选栏默认用 8 列 grid 排成两行，如需调整：

```css
.filter-tags {
    grid-template-columns: repeat(8, 1fr);  /* 改为其他列数 */
}
```

## 浏览器兼容性

- ✅ Chrome / Edge (最新版)
- ✅ Firefox (最新版)
- ✅ Safari (最新版)
- ✅ 移动端浏览器

## 性能优化建议

1. **图片优化**
   - 使用 WebP 格式（压缩率更高）
   - 限制图片尺寸（建议 600x800 像素）
   - 使用 CDN 加速

2. **代码优化**
   - 压缩 CSS 和 JS 文件
   - 启用 Gzip 压缩
   - 使用浏览器缓存

## 常见问题

### Q: GitHub Pages 在国内访问慢怎么办？

A: 可以考虑：
- 使用国内图床（如 Gitee、阿里云 OSS）
- 使用 CDN 加速
- 或者部署到 Vercel、Netlify 等支持国内访问的平台

### Q: 如何实现用户上传游戏功能？

A: GitHub Pages 是静态托管，无法直接实现。需要：
- 使用第三方服务（如 Firebase、Supabase）
- 或者自建后端服务
- GitHub Pages 仅作为前端展示

### Q: 如何防止图片链接失效？

A: 建议：
- 使用稳定的云存储（阿里云 OSS、腾讯云 COS）
- 定期检查链接有效性
- 设置图片备用链接

### Q: 游戏数据（上千个）如何管理？

A: GitHub Pages 不支持后端数据库，数据通过 JSON 文件或前端数组维护。对于大规模数据建议：
- 数据量 <500：直接用 `games.json` 或内置数组
- 数据量很大：考虑使用 Firebase / Supabase 等在线数据库，或按分类拆分多个 JSON 文件用 fetch 按需加载

## 许可证

本项目仅供学习交流使用。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题，请通过 GitHub Issues 联系。
