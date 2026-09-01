// ==================== 云端统计开关 ====================
// 腾讯云 CloudBase 云函数（HTTP 网关），国内可达
const ENABLE_CLOUD_STATS = true;
const HOT_GAMES_API = 'https://game-counter-d3gk5xyxj456b476d-1478718251.ap-shanghai.app.tcloudbase.com';

// ==================== 百度统计事件上报（转化分析） ====================
function trackEvent(category, action, label, value) {
    if (typeof _hmt !== 'undefined' && _hmt.push) {
        try {
            _hmt.push(['_trackEvent', category, action, label, value]);
        } catch (e) {}
    }
}

// ==================== 浏览器去重（同一浏览器每个游戏只计一次） ====================
function getLocalSet(key) {
    try {
        return new Set(JSON.parse(localStorage.getItem(key) || '[]'));
    } catch (e) {
        return new Set();
    }
}

function saveLocalSet(key, set) {
    try {
        localStorage.setItem(key, JSON.stringify(Array.from(set)));
    } catch (e) {}
}

function shouldCountClick(gameTitle) {
    const set = getLocalSet('clickedGames');
    if (set.has(gameTitle)) return false;
    set.add(gameTitle);
    saveLocalSet('clickedGames', set);
    return true;
}

function shouldCountDownload(gameTitle) {
    const set = getLocalSet('downloadedGames');
    if (set.has(gameTitle)) return false;
    set.add(gameTitle);
    saveLocalSet('downloadedGames', set);
    return true;
}

// ==================== 状态管理 ====================
let gamesData = [];
let dropdownPlatform = 'all';
let currentPlatform = 'all';
let currentCategory = 'all';
let currentSort = 'default';
let searchQuery = '';
let currentPage = 1;
const pageSize = 20; // 每页显示数量
let allClicksMap = {}; // 游戏名 -> 点击量
let allDownloadsMap = {}; // 游戏名 -> 下载量

const platformLabels = { android: '安卓', ns: 'NS', pc: 'PC' };
const platformOrder = { android: 0, ns: 1, pc: 2 };
const platformIcons = {
    android: '<svg viewBox="0 0 152 89" width="16" height="16"><path fill="currentColor" d="M151.025 85.224q-.071-.464-.147-.92a75.665 75.665 0 0 0-7.546-22.597 76.5 76.5 0 0 0-5.511-8.995 76 76 0 0 0-8.322-9.808 76.034 76.034 0 0 0-13.398-10.626q.042-.074.085-.148 2.286-3.948 4.572-7.897l4.47-7.712a3946 3946 0 0 0 3.208-5.54q.38-.658.604-1.355a6.97 6.97 0 0 0-.652-5.702 6.9 6.9 0 0 0-2.406-2.398 7 7 0 0 0-2.954-.95 7 7 0 0 0-2.376.206 6.93 6.93 0 0 0-4.22 3.227q-1.606 2.77-3.208 5.54l-4.47 7.712c-1.523 2.634-3.05 5.263-4.573 7.897q-.25.43-.5.865c-.232-.092-.46-.184-.692-.272-8.398-3.205-17.511-4.958-27.036-4.958q-.39-.001-.78.004A75.7 75.7 0 0 0 50.977 25q-1.317.46-2.608.968-.234-.404-.467-.806-2.286-3.95-4.573-7.897l-4.47-7.713a4385 4385 0 0 1-3.208-5.54A6.93 6.93 0 0 0 29.055.58a6.9 6.9 0 0 0-2.954.95 6.92 6.92 0 0 0-3.157 4.185 6.96 6.96 0 0 0 .703 5.27l3.208 5.54 4.47 7.713c1.523 2.634 3.05 5.263 4.573 7.897.01.022.025.044.036.066a76.3 76.3 0 0 0-13.527 10.711 76.5 76.5 0 0 0-8.322 9.808 75.4 75.4 0 0 0-5.51 8.995 75.7 75.7 0 0 0-7.546 22.597 76.038 76.038 0 0 0-.581 4.247h151a77 77 0 0 0-.434-3.327z"/><path fill="#4caf50" d="M115.225 67.663c3.022-2.012 3.461-6.668.981-10.4-2.48-3.73-6.939-5.123-9.96-3.11-3.021 2.012-3.46 6.668-.98 10.4 2.479 3.73 6.938 5.123 9.959 3.11M46.762 64.564c2.48-3.73 2.04-8.387-.98-10.4-3.022-2.012-7.481-.619-9.96 3.112s-2.041 8.387.98 10.4 7.48.62 9.96-3.112"/></svg>',
    ns: '<svg viewBox="0 0 24 24" width="12" height="12"><path fill="currentColor" d="M14.176 24h3.674c3.376 0 6.15-2.774 6.15-6.15V6.15C24 2.775 21.226 0 17.85 0H14.1c-.074 0-.15.074-.15.15v23.7c-.001.076.075.15.226.15m4.574-13.199c1.351 0 2.399 1.125 2.399 2.398c0 1.352-1.125 2.4-2.399 2.4c-1.35 0-2.4-1.049-2.4-2.4c-.075-1.349 1.05-2.398 2.4-2.398M11.4 0H6.15C2.775 0 0 2.775 0 6.15v11.7C0 21.226 2.775 24 6.15 24h5.25c.074 0 .15-.074.15-.149V.15c.001-.076-.075-.15-.15-.15M9.676 22.051H6.15a4.194 4.194 0 0 1-4.201-4.201V6.15A4.194 4.194 0 0 1 6.15 1.949H9.6zM3.75 7.199c0 1.275.975 2.25 2.25 2.25s2.25-.975 2.25-2.25c0-1.273-.975-2.25-2.25-2.25s-2.25.977-2.25 2.25"/></svg>',
    pc: '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="12" rx="2"/><path d="M8 20h8M12 16v4"/></svg>'
};

// ==================== DOM元素 ====================
const gameGrid = document.getElementById('gameGrid');
const searchInput = document.getElementById('searchInput');
const searchBtn = document.querySelector('.search-btn');
const themeToggle = document.getElementById('themeToggle');
const themeIcon = document.querySelector('.theme-icon');
const backToTop = document.getElementById('backToTop');
const categoryItems = document.querySelectorAll('.filter-item');
const pagination = document.getElementById('pagination');

// ==================== 分类名称映射 ====================
const categoryNames = {
    'all': '全部游戏',
    'interactive': '真人互动',
    'strategy': '策略',
    'action': '动作',
    'adventure': '冒险',
    'rpg': '角色扮演',
    'simulation': '模拟',
    'racing': '竞速',
    'arcade': '街机',
    'shooter': '射击',
    'card': '卡牌',
    'sports': '体育',
    'music': '音乐',
    'puzzle': '益智',
    'survival': '生存',
    'fighting': '格斗'
};

// 评分描述英文 -> 中文映射
const reviewScoreMap = {
    'Overwhelmingly Positive': '好评如潮',
    'Very Positive': '特别好评',
    'Mostly Positive': '多半好评',
    'Positive': '好评',
    'Mixed': '褒贬不一',
    'Mostly Negative': '多半差评',
    'Negative': '差评',
    'Very Negative': '特别差评',
    'Overwhelmingly Negative': '差评如潮'
};

// 评分等级（0-9分）：good好评/normal中/trash垃圾
function getScoreLevel(score) {
    if (score >= 8) return 'good';
    if (score >= 5) return 'normal';
    return 'trash';
}

function getScoreEmoji(score) {
    if (score >= 8) return '😄';
    if (score >= 5) return '😑';
    return '😞';
}

// ==================== 从数据源加载游戏 ====================
// 数据版本号：games.json 更新后需 +1，以刷新 jsDelivr 与浏览器缓存
const GAMES_DATA_VERSION = 4;
const GAMES_DATA_URLS = [
    `data/games.json?v=${GAMES_DATA_VERSION}`,
    `https://cdn.jsdelivr.net/gh/zuoan6122/game-resource-site@master/data/games.json?v=${GAMES_DATA_VERSION}`
];

async function fetchWithTimeout(url, ms = 8000) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), ms);
    try {
        const response = await fetch(url, { signal: controller.signal });
        if (!response.ok) throw new Error('HTTP ' + response.status);
        return await response.json();
    } finally {
        clearTimeout(timer);
    }
}

async function loadGamesFromJSON() {
    // 优先使用 jsDelivr 加载的 games-data.js（<script> 标签加载，绕过 CORS）
    if (window.GAMES_DATA && Array.isArray(window.GAMES_DATA) && window.GAMES_DATA.length > 0) {
        return window.GAMES_DATA;
    }
    // 备用 CDN 节点（gcore），动态加载并等待完成
    try {
        await new Promise((resolve, reject) => {
            const s = document.createElement('script');
            s.src = 'https://gcore.jsdelivr.net/gh/zuoan6122/game-resource-site@master/games-data.js';
            s.onload = resolve;
            s.onerror = reject;
            document.head.appendChild(s);
        });
        if (window.GAMES_DATA && Array.isArray(window.GAMES_DATA) && window.GAMES_DATA.length > 0) {
            return window.GAMES_DATA;
        }
    } catch (error) {
        console.warn('备用CDN节点加载失败，尝试本地JSON', error);
    }
    // 回退：本地 JSON（GitHub Pages 同源，速度较慢）
    for (const url of GAMES_DATA_URLS) {
        try {
            return await fetchWithTimeout(url);
        } catch (error) {
            console.warn('数据源加载失败，尝试备用:', url, error);
        }
    }
    console.error('所有数据源均加载失败');
    return [];
}

// ==================== 获取过滤后的游戏 ====================
function defaultCompare(a, b, platform) {
    if (platform === 'pc') {
        // PC平台按评分从高到低排
        return (b.reviewScore ?? -1) - (a.reviewScore ?? -1);
    }
    return (platformOrder[a.platform] ?? 99) - (platformOrder[b.platform] ?? 99);
}

function applySort(filtered, platform) {
    if (currentSort === 'hot') {
        // 热度：按点击量降序，无点击量的按默认顺序
        filtered.sort((a, b) => {
            const ca = allClicksMap[a.title] || 0;
            const cb = allClicksMap[b.title] || 0;
            if (ca !== cb) return cb - ca;
            return defaultCompare(a, b, platform);
        });
        return;
    }
    if (currentSort === 'downloads') {
        // 下载量：按下载量降序，无下载量的按默认顺序
        filtered.sort((a, b) => {
            const da = allDownloadsMap[a.title] || 0;
            const db = allDownloadsMap[b.title] || 0;
            if (da !== db) return db - da;
            return defaultCompare(a, b, platform);
        });
        return;
    }
    filtered.sort((a, b) => defaultCompare(a, b, platform));
}

function getFilteredGames() {
    let filtered;
    let platform;
    if (searchQuery) {
        // 搜索时：下拉框平台 + 平台标签 + 游戏类型 + 关键词
        platform = dropdownPlatform;
        filtered = gamesData.filter(game => {
            const matchDropdown = dropdownPlatform === 'all' || game.platform === dropdownPlatform;
            const matchPlatformTab = currentPlatform === 'all' || game.platform === currentPlatform;
            const matchCategory = currentCategory === 'all' || game.category === currentCategory;
            const matchSearch = game.title.toLowerCase().includes(searchQuery.toLowerCase());
            return matchDropdown && matchPlatformTab && matchCategory && matchSearch;
        });
        applySort(filtered, platform);
    } else {
        // 浏览时：平台标签 + 类型
        platform = currentPlatform;
        filtered = gamesData.filter(game => {
            const matchPlatform = currentPlatform === 'all' || game.platform === currentPlatform;
            const matchCategory = currentCategory === 'all' || game.category === currentCategory;
            return matchPlatform && matchCategory;
        });
        applySort(filtered, platform);
    }

    return filtered;
}

// ==================== 渲染游戏卡片 ====================
function renderGames() {
    const filteredGames = getFilteredGames();
    const totalPages = Math.ceil(filteredGames.length / pageSize);

    // 边界保护
    if (currentPage > totalPages && totalPages > 0) {
        currentPage = totalPages;
    }
    if (currentPage < 1) currentPage = 1;

    // 计算当前页数据
    const start = (currentPage - 1) * pageSize;
    const end = start + pageSize;
    const pageGames = filteredGames.slice(start, end);

    // 清空网格
    gameGrid.innerHTML = '';

    // 渲染卡片
    if (filteredGames.length === 0) {
        gameGrid.innerHTML = '<div class="no-results">没有找到相关游戏</div>';
        pagination.innerHTML = '';
        return;
    }

    pageGames.forEach(game => {
        const card = document.createElement('div');
        card.className = 'game-card';
        const placeholderSvg = `<div class="game-cover-placeholder">
                <div class="game-cover-placeholder-inner">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M6 11h4m-2-2v4"/><circle cx="15" cy="11" r="1"/><circle cx="18" cy="13" r="1"/><path d="M17.32 4H6.68a4 4 0 0 0-3.78 2.72L2 11a2 2 0 0 0 0 2l.9 4.28A4 4 0 0 0 6.68 20h10.64a4 4 0 0 0 3.78-2.72L22 13a2 2 0 0 0 0-2l-.9-4.28A4 4 0 0 0 17.32 4z"/></svg>
                    <span class="game-cover-placeholder-text">暂无图片</span>
                </div>
               </div>`;
        const coverHtml = game.coverImage
            ? `<img src="${game.coverImage}" alt="${game.title}" class="game-cover-img" loading="lazy" onerror="this.style.display='none';this.nextElementSibling.style.display='flex'">${placeholderSvg.replace('class="game-cover-placeholder"', 'class="game-cover-placeholder" style="display:none;"')}`
            : placeholderSvg;
        card.innerHTML = `
            <div class="game-cover">
                ${coverHtml}
                ${game.platform === 'pc' && game.reviewScore != null ? `<div class="score-badge score-${getScoreLevel(game.reviewScore)}">
                    <span class="score-emoji">${getScoreEmoji(game.reviewScore)}</span>
                    <span>${game.reviewScore}</span>
                </div>` : ''}
            </div>
            <div class="game-info">
                <h3 class="game-title" title="${game.title}">${game.title}</h3>
                <div class="game-tags">
                    <span class="platform-badge platform-${game.platform}">${platformIcons[game.platform] || ''}<span class="platform-text">${platformLabels[game.platform] || ''}</span></span>
                    <span class="game-tag">${categoryNames[game.category] || '其他'}</span>
                    ${game.releaseDate ? `<span class="game-tag year-tag">${game.releaseDate.match(/\d{4}/)?.[0] || ''}</span>` : ''}
                </div>
            </div>
        `;

        // PC、NS、安卓游戏有详情弹窗，点击封面或标题打开
        if (game.platform === 'pc' || game.platform === 'ns' || game.platform === 'android') {
            const coverEl = card.querySelector('.game-cover');
            const titleEl = card.querySelector('.game-title');
            coverEl.style.cursor = 'pointer';
            titleEl.style.cursor = 'pointer';
            coverEl.addEventListener('click', (e) => {
                e.preventDefault();
                openGameModal(game);
            });
            titleEl.addEventListener('click', (e) => {
                e.preventDefault();
                openGameModal(game);
            });
        }

        gameGrid.appendChild(card);
    });

    // 渲染分页
    renderPagination(totalPages, filteredGames.length);
}

// ==================== 渲染分页 ====================
function renderPagination(totalPages, totalCount) {
    if (totalPages <= 1) {
        pagination.innerHTML = '';
        return;
    }

    let html = '';

    // 上一页
    html += `<button class="page-btn prev ${currentPage === 1 ? 'disabled' : ''}" data-page="${currentPage - 1}" ${currentPage === 1 ? 'disabled' : ''}>
        <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M15 18l-6-6 6-6"/></svg>
    </button>`;

    // 页码按钮（最多显示7个，带省略号）
    const pages = getPageNumbers(currentPage, totalPages);
    pages.forEach(p => {
        if (p === '...') {
            html += `<span class="page-ellipsis">...</span>`;
        } else {
            html += `<button class="page-btn ${p === currentPage ? 'active' : ''}" data-page="${p}">${p}</button>`;
        }
    });

    // 下一页
    html += `<button class="page-btn next ${currentPage === totalPages ? 'disabled' : ''}" data-page="${currentPage + 1}" ${currentPage === totalPages ? 'disabled' : ''}>
        <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18l6-6-6-6"/></svg>
    </button>`;

    // 跳转输入框
    html += `<span class="page-jump">第<input type="number" class="page-input" min="1" max="${totalPages}" value="${currentPage}">页<button class="page-go-btn">跳转</button></span>`;

    // 总条数信息
    html += `<span class="page-info">共 ${totalCount} 个</span>`;

    pagination.innerHTML = html;

    // 绑定分页点击事件
    pagination.querySelectorAll('.page-btn:not(.disabled)').forEach(btn => {
        btn.addEventListener('click', handlePageClick);
    });

    // 绑定跳转输入框事件
    const pageInput = pagination.querySelector('.page-input');
    const pageGoBtn = pagination.querySelector('.page-go-btn');
    if (pageInput) {
        const doJump = () => {
            const page = parseInt(pageInput.value);
            if (page >= 1 && page <= totalPages && page !== currentPage) {
                currentPage = page;
                renderGames();
                window.scrollTo({ top: gameGrid.offsetTop - 80, behavior: 'smooth' });
            }
        };
        pageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                doJump();
            }
        });
        pageInput.addEventListener('blur', () => {
            const page = parseInt(pageInput.value);
            if (isNaN(page) || page < 1 || page > totalPages) {
                pageInput.value = currentPage;
            }
        });
        if (pageGoBtn) {
            pageGoBtn.addEventListener('click', doJump);
        }
    }
}

// 生成分页数字（带省略号）
function getPageNumbers(current, total) {
    const pages = [];
    const maxVisible = 7;

    if (total <= maxVisible) {
        for (let i = 1; i <= total; i++) pages.push(i);
        return pages;
    }

    // 始终显示第1页
    pages.push(1);

    // 计算中间范围
    let start = Math.max(2, current - 2);
    let end = Math.min(total - 1, current + 2);

    // 左边省略号
    if (start > 2) pages.push('...');

    // 中间页码
    for (let i = start; i <= end; i++) pages.push(i);

    // 右边省略号
    if (end < total - 1) pages.push('...');

    // 始终显示最后一页
    pages.push(total);

    return pages;
}

// ==================== 分页点击 ====================
function handlePageClick(e) {
    const page = parseInt(e.currentTarget.dataset.page);
    if (!isNaN(page) && page !== currentPage) {
        currentPage = page;
        renderGames();
        // 滚动到游戏列表顶部
        document.querySelector('.content').scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// ==================== 平台切换（自定义下拉框） ====================
function handlePlatformChange(value) {
    dropdownPlatform = value;

    // 仅更新下拉框UI，不触发渲染
    const selectTrigger = document.querySelector('.custom-select-value');
    const selectedOption = document.querySelector(`.custom-select-option[data-value="${value}"]`);
    if (selectTrigger && selectedOption) {
        selectTrigger.textContent = selectedOption.textContent;
    }
    document.querySelectorAll('.custom-select-option').forEach(opt => {
        opt.classList.toggle('active', opt.dataset.value === value);
    });
}

// ==================== 平台切换（标签按钮） ====================
function handlePlatformClick(e) {
    const platformTab = e.currentTarget;
    currentPlatform = platformTab.dataset.platform;

    // 仅更新平台激活状态，不同步下拉框
    document.querySelectorAll('.platform-tab').forEach(t => t.classList.remove('active'));
    platformTab.classList.add('active');

    currentPage = 1;

    // 真人互动仅在 全部/PC 平台显示
    updateInteractiveFilterVisibility();

    // 始终重新渲染（搜索时也按平台标签过滤）
    renderGames();
}

// 真人互动分类只在 全部/PC 平台可见；切到安卓/NS 时隐藏并重置分类
function updateInteractiveFilterVisibility() {
    const interactiveItem = document.querySelector('.filter-item[data-category="interactive"]');
    if (!interactiveItem) return;
    const show = currentPlatform === 'all' || currentPlatform === 'pc';
    interactiveItem.style.display = show ? '' : 'none';
    if (!show && currentCategory === 'interactive') {
        currentCategory = 'all';
        categoryItems.forEach(item => item.classList.remove('active'));
        const allItem = document.querySelector('.filter-item[data-category="all"]');
        if (allItem) allItem.classList.add('active');
    }
}

// ==================== 分类切换 ====================
function handleCategoryClick(e) {
    e.preventDefault();

    const categoryItem = e.target.closest('.filter-item');
    if (!categoryItem) return;

    // 更新活动状态
    categoryItems.forEach(item => item.classList.remove('active'));
    categoryItem.classList.add('active');

    // 更新当前分类，重置页码
    currentCategory = categoryItem.dataset.category;
    currentPage = 1;

    // 重新渲染
    renderGames();
}

// ==================== 搜索功能 ====================
function handleSearch() {
    searchQuery = searchInput.value.trim();
    currentPage = 1;
    renderGames();
}

// ==================== 初始化页面 ====================
function resetPage() {
    // 重置状态
    currentPlatform = 'all';
    dropdownPlatform = 'all';
    currentCategory = 'all';
    currentSort = 'default';
    searchQuery = '';
    currentPage = 1;

    // 清空搜索框
    searchInput.value = '';

    // 重置平台标签
    document.querySelectorAll('.platform-tab').forEach(t => {
        t.classList.toggle('active', t.dataset.platform === 'all');
    });

    // 重置游戏类型
    categoryItems.forEach(item => item.classList.remove('active'));
    categoryItems[0].classList.add('active');

    // 真人互动可见性（当前平台为 all）
    updateInteractiveFilterVisibility();

    // 重置排序
    document.querySelectorAll('.sort-tab').forEach(t => {
        t.classList.toggle('active', t.dataset.sort === 'default');
    });

    // 重置下拉框
    const selectTrigger = document.querySelector('.custom-select-value');
    if (selectTrigger) selectTrigger.textContent = '所有分类';
    document.querySelectorAll('.custom-select-option').forEach(opt => {
        opt.classList.toggle('active', opt.dataset.value === 'all');
    });

    // 滚动到顶部
    window.scrollTo({ top: 0, behavior: 'smooth' });

    // 重新渲染
    renderGames();
}

// ==================== 主题切换 ====================
function toggleTheme() {
    const body = document.body;
    body.classList.toggle('light-theme');
    body.classList.toggle('dark-theme');

    const isLight = body.classList.contains('light-theme');
    localStorage.setItem('theme', isLight ? 'light' : 'dark');

    if (isLight) {
        themeIcon.innerHTML = '<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><path d="M12 1v2m0 18v2M4.22 4.22l1.42 1.42m12.72 12.72l1.42 1.42M1 12h2m18 0h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>';
    } else {
        themeIcon.innerHTML = '<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';
    }
}

// ==================== 返回顶部 ====================
function toggleBackToTop() {
    if (window.scrollY > 300) {
        backToTop.classList.remove('hidden');
    } else {
        backToTop.classList.add('hidden');
    }
}

function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ==================== 轮播图功能 ====================
let currentSlide = 0;
let slides = [];

function showSlide(index) {
    slides.forEach(slide => slide.classList.remove('active'));
    slides[index].classList.add('active');
}

function nextSlide() {
    currentSlide = (currentSlide + 1) % slides.length;
    showSlide(currentSlide);
}

// ==================== 游戏详情弹窗 ====================
function buildStars(score) {
    // score: 0-9, 2分=1颗星, 奇数分加半星
    const fullStars = Math.floor(score / 2);
    const hasHalf = score % 2 === 1;
    const emptyStars = 5 - fullStars - (hasHalf ? 1 : 0);
    let html = '';
    const starSvg = '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>';
    const halfSvg = '<svg viewBox="0 0 24 24" width="18" height="18"><defs><linearGradient id="halfGrad"><stop offset="50%" stop-color="currentColor"/><stop offset="50%" stop-color="rgba(255,255,255,0.15)"/></linearGradient></defs><path fill="url(#halfGrad)" d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>';
    const emptySvg = '<svg viewBox="0 0 24 24" width="18" height="18" fill="rgba(255,255,255,0.15)" stroke="currentColor" stroke-width="1"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>';
    for (let i = 0; i < fullStars; i++) html += starSvg;
    if (hasHalf) html += halfSvg;
    for (let i = 0; i < emptyStars; i++) html += emptySvg;
    return html;
}

function openGameModal(game) {
    const overlay = document.getElementById('gameModalOverlay');
    const content = document.getElementById('gameModalContent');
    if (!overlay || !content) return;

    // 上报点击量到云端统计（同一浏览器每个游戏只计一次）
    if (ENABLE_CLOUD_STATS && shouldCountClick(game.title)) {
        fetch(`${HOT_GAMES_API}/click?game=${encodeURIComponent(game.title)}`, { method: 'POST' }).catch(() => {});
    }

    const scoreDesc = game.reviewScore != null
        ? (reviewScoreMap[game.reviewScoreDesc] || game.reviewScoreDesc || '')
        : '暂无评分';
    const starsHtml = game.reviewScore != null ? buildStars(game.reviewScore) : buildStars(0);

    // 简介：超过300字截断加省略号
    let desc = game.description || '暂无简介';
    if (desc.length > 300) {
        desc = desc.slice(0, 300) + '…';
    }

    // 封面：无封面显示占位图
    const coverHtml = game.coverImage
        ? `<img src="${game.coverImage}" alt="${game.title}" class="modal-cover" onerror="this.style.display='none'">`
        : `<div class="modal-cover-placeholder"><span>暂无图片</span></div>`;

    // 转存区域
    let transferHtml;
    let stepsHtml;
    if (game.platform === 'pc') {
        // PC：模拟器分类样式链接，点击展开二维码+下载步骤（不跳转）
        const qrHtml = game.qrCode
            ? `<div class="modal-qr-img"><img src="${game.qrCode}" alt="二维码"></div>`
            : `<div class="modal-qr-img"><svg viewBox="0 0 150 150" width="150" height="150">
                <rect x="0" y="0" width="150" height="150" fill="#fff"/>
                <text x="75" y="82" text-anchor="middle" font-size="20" fill="#bbb" font-weight="500">二维码</text>
            </svg></div>`;
        transferHtml = `<a href="#" class="modal-emulator-item modal-pc-toggle">
            <span class="modal-emulator-icon">
                <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg>
            </span>
            <span class="modal-emulator-name">${game.title}</span>
            <span class="modal-emulator-arrow">立即下载
                <svg class="modal-pc-arrow-icon" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9l6 6 6-6"/></svg>
            </span>
        </a>
        <div class="modal-pc-download" style="display:none;">
            <div class="modal-pc-loading">
                <span class="modal-pc-spinner"></span>
                <span>正在加载...</span>
            </div>
            <div class="modal-pc-content" style="display:none;">
                ${qrHtml}
                <div class="modal-qr-steps-title expanded">下载步骤</div>
                <ol class="modal-qr-steps expanded">
                    <li>使用网盘软件或者微信或 QQ 扫描二维码。</li>
                    <li>扫描后，点击"去APP内查看/保存"按钮。</li>
                    <li>跳转到网盘 APP，将资源转存到自己账号（若未安装该 App，请下载）。</li>
                    <li>在电脑端登录网盘账号，找到转存好的游戏文件，即可下载。</li>
                </ol>
            </div>
        </div>`;
        stepsHtml = '';
    } else {
        // NS/安卓：模拟器分类样式链接，点击跳转夸克网盘
        transferHtml = `<a href="${game.downloadUrl}" target="_blank" class="modal-emulator-item">
            <span class="modal-emulator-icon">
                <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg>
            </span>
            <span class="modal-emulator-name">${game.title}</span>
            <span class="modal-emulator-arrow">夸克网盘
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7 17L17 7M7 7h10v10"/></svg>
            </span>
        </a>`;
        stepsHtml = `
        <div class="modal-qr-steps-title expanded">下载步骤</div>
        <ol class="modal-qr-steps expanded">
            <li>点击即可转存到夸克网盘</li>
        </ol>`;
    }

    // 截图：无截图显示暂无图片
    let screenshotsHtml;
    if (game.screenshots) {
        const urls = game.screenshots.split(',').filter(u => u.trim());
        if (urls.length > 0) {
            screenshotsHtml = `<div class="modal-screenshots-title">游戏截图</div>
            <div class="modal-screenshots-wrapper">
                <button class="modal-shots-arrow modal-shots-prev" aria-label="上一张"><svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"/></svg></button>
                <div class="modal-screenshots">`;
            urls.forEach((url, i) => {
                screenshotsHtml += `<img src="${url}" alt="截图" class="screenshot-clickable" data-idx="${i}">`;
            });
            screenshotsHtml += `</div>
                <button class="modal-shots-arrow modal-shots-next" aria-label="下一张"><svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg></button>
            </div>`;
        }
    }
    if (!screenshotsHtml) {
        screenshotsHtml = '<div class="modal-no-screenshot">暂无图片</div>';
    }

    content.innerHTML = `
        <div class="modal-cover-wrapper">
            ${coverHtml}
        </div>
        <div class="modal-body">
            <h2 class="modal-title">${game.title}</h2>
            <div class="modal-meta">
                <div class="modal-release">发行日期：${game.releaseDate || '未知'}</div>
                <div class="modal-rating">
                    <span class="modal-stars">${starsHtml}</span>
                    <span class="modal-score-desc">${scoreDesc}</span>
                </div>
            </div>
            <div class="modal-desc">${desc}</div>
            <div class="modal-tab-section">
                <div class="modal-tabs">
                    <div class="modal-tab active" data-tab="qr">夸克网盘转存</div>
                    <div class="modal-tab" data-tab="screenshot">游戏截图</div>
                </div>
                <div class="modal-tab-panels">
                    <div class="modal-tab-panel active" data-panel="qr">
                        <div class="modal-qr-section">
                            ${transferHtml}
                            ${stepsHtml}
                        </div>
                    </div>
                    <div class="modal-tab-panel" data-panel="screenshot">
                        ${screenshotsHtml}
                    </div>
                </div>
            </div>
        </div>
    `;

    // 绑定截图点击事件
    const screenshotUrls = game.screenshots ? game.screenshots.split(',').filter(u => u.trim()) : [];
    content.querySelectorAll('.screenshot-clickable').forEach((img, idx) => {
        img.addEventListener('click', () => {
            openImageViewer(screenshotUrls, idx);
        });
    });

    // 绑定夸克网盘跳转链接点击：上报下载量（PC为展开交互，单独处理）
    content.querySelectorAll('.modal-emulator-item:not(.modal-pc-toggle)').forEach(link => {
        link.addEventListener('click', () => {
            if (ENABLE_CLOUD_STATS && shouldCountDownload(game.title)) {
                fetch(`${HOT_GAMES_API}/download?game=${encodeURIComponent(game.title)}`, { method: 'POST' }).catch(() => {});
            }
            trackEvent('下载', '点击网盘链接', game.title);
        });
    });

    // 绑定PC转存链接点击：展开/收起二维码+下载步骤，并上报下载量
    content.querySelectorAll('.modal-pc-toggle').forEach(toggle => {
        toggle.addEventListener('click', (e) => {
            e.preventDefault();
            const downloadSection = toggle.nextElementSibling;
            const arrowIcon = toggle.querySelector('.modal-pc-arrow-icon');
            if (downloadSection && downloadSection.classList.contains('modal-pc-download')) {
                const isHidden = downloadSection.style.display === 'none';
                if (isHidden) {
                    // 展开：先显示局部假刷新（加载动画），再淡入二维码+下载步骤
                    downloadSection.style.display = 'block';
                    if (arrowIcon) arrowIcon.style.transform = 'rotate(180deg)';
                    const loadingEl = downloadSection.querySelector('.modal-pc-loading');
                    const contentEl = downloadSection.querySelector('.modal-pc-content');
                    if (loadingEl) loadingEl.style.display = 'flex';
                    if (contentEl) {
                        contentEl.style.display = 'none';
                        contentEl.classList.remove('fade-in');
                    }
                    setTimeout(() => {
                        if (loadingEl) loadingEl.style.display = 'none';
                        if (contentEl) {
                            contentEl.style.display = 'block';
                            contentEl.classList.add('fade-in');
                        }
                    }, 300);
                    if (ENABLE_CLOUD_STATS && shouldCountDownload(game.title)) {
                        fetch(`${HOT_GAMES_API}/download?game=${encodeURIComponent(game.title)}`, { method: 'POST' }).catch(() => {});
                    }
                    trackEvent('下载', '展开二维码', game.title);
                } else {
                    downloadSection.style.display = 'none';
                    if (arrowIcon) arrowIcon.style.transform = 'rotate(0)';
                }
            }
        });
    });

    // 绑定截图列表左右箭头滚动
    const shotsContainer = content.querySelector('.modal-screenshots');
    const shotsPrev = content.querySelector('.modal-shots-prev');
    const shotsNext = content.querySelector('.modal-shots-next');
    if (shotsContainer && shotsPrev && shotsNext) {
        const updateArrows = () => {
            const maxScroll = shotsContainer.scrollWidth - shotsContainer.clientWidth;
            shotsPrev.style.opacity = shotsContainer.scrollLeft <= 2 ? '0.3' : '';
            shotsNext.style.opacity = shotsContainer.scrollLeft >= maxScroll - 2 ? '0.3' : '';
        };
        shotsPrev.addEventListener('click', () => {
            shotsContainer.scrollBy({ left: -shotsContainer.clientWidth * 0.8, behavior: 'smooth' });
        });
        shotsNext.addEventListener('click', () => {
            shotsContainer.scrollBy({ left: shotsContainer.clientWidth * 0.8, behavior: 'smooth' });
        });
        shotsContainer.addEventListener('scroll', updateArrows);
        updateArrows();
    }

    // 绑定下载步骤展开/收起
    const stepsTitle = content.querySelector('.modal-qr-steps-title');
    const stepsList = content.querySelector('.modal-qr-steps');
    if (stepsTitle && stepsList) {
        stepsTitle.addEventListener('click', () => {
            stepsTitle.classList.toggle('expanded');
            stepsList.classList.toggle('expanded');
        });
    }

    // 绑定Tab切换
    content.querySelectorAll('.modal-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            const tabName = tab.dataset.tab;
            content.querySelectorAll('.modal-tab').forEach(t => t.classList.remove('active'));
            content.querySelectorAll('.modal-tab-panel').forEach(p => p.classList.remove('active'));
            tab.classList.add('active');
            const panel = content.querySelector(`.modal-tab-panel[data-panel="${tabName}"]`);
            if (panel) panel.classList.add('active');

        });
    });

    overlay.classList.add('active');
    document.body.style.overflow = 'hidden';
}

// ==================== 图片放大查看器 ====================
let currentScreenshots = [];
let currentScreenshotIndex = 0;

function openImageViewer(screenshots, index = 0) {
    const overlay = document.getElementById('imageViewerOverlay');
    const img = document.getElementById('imageViewerImg');
    const prevBtn = document.getElementById('imageViewerPrev');
    const nextBtn = document.getElementById('imageViewerNext');
    const counter = document.getElementById('imageViewerCounter');
    if (!overlay || !img) return;

    currentScreenshots = screenshots;
    currentScreenshotIndex = index;

    img.src = screenshots[index];
    overlay.classList.add('active');

    // 更新计数
    if (counter) {
        counter.textContent = (index + 1) + '/' + screenshots.length;
    }

    // 更新按钮状态
    if (prevBtn) prevBtn.disabled = index === 0;
    if (nextBtn) nextBtn.disabled = index === screenshots.length - 1;
}

function closeImageViewer() {
    const overlay = document.getElementById('imageViewerOverlay');
    if (overlay) {
        overlay.classList.remove('active');
    }
}

function prevScreenshot() {
    if (currentScreenshotIndex > 0) {
        openImageViewer(currentScreenshots, currentScreenshotIndex - 1);
    }
}

function nextScreenshot() {
    if (currentScreenshotIndex < currentScreenshots.length - 1) {
        openImageViewer(currentScreenshots, currentScreenshotIndex + 1);
    }
}

function closeGameModal() {
    const overlay = document.getElementById('gameModalOverlay');
    if (overlay) {
        overlay.classList.remove('active');
        document.body.style.overflow = '';
    }
}

// ==================== 标签页切换 ====================
function handleTabClick(e) {
    const tab = e.currentTarget;
    const tabName = tab.dataset.tab;

    // 更新标签页激活状态
    document.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');

    // 显示对应内容
    document.querySelectorAll('.filter-content').forEach(c => c.classList.remove('active'));
    const targetContent = document.getElementById(`tab-${tabName}`);
    if (targetContent) targetContent.classList.add('active');

    // 只在"游戏类型"标签下显示游戏卡片
    const gameContent = document.getElementById('gameContent');
    if (tabName === 'game-type') {
        gameContent.style.display = '';
    } else {
        gameContent.style.display = 'none';
    }
}

// ==================== 事件监听 ====================
function bindEvents() {
    // 大分类标签页
    document.querySelectorAll('.filter-tab').forEach(tab => {
        tab.addEventListener('click', handleTabClick);
    });

    // 标题链接和首页按钮 - 整体刷新
    const logoLink = document.getElementById('logoLink');
    if (logoLink) {
        logoLink.addEventListener('click', (e) => {
            e.preventDefault();
            location.reload();
        });
    }
    const homeBtn = document.getElementById('homeBtn');
    if (homeBtn) {
        homeBtn.addEventListener('click', () => location.reload());
    }

    // 游戏必备软件/模拟器分类网盘链接 - 转化统计
    document.querySelectorAll('.emulator-item').forEach(link => {
        link.addEventListener('click', () => {
            const name = link.querySelector('.emulator-name');
            trackEvent('下载', '点击网盘链接', name ? name.textContent.trim() : '');
        });
    });

    // 平台子标签
    document.querySelectorAll('.platform-tab').forEach(tab => {
        tab.addEventListener('click', handlePlatformClick);
    });

    // 自定义下拉框
    const customSelect = document.getElementById('platformSelect');
    if (customSelect) {
        const trigger = customSelect.querySelector('.custom-select-trigger');
        const options = customSelect.querySelectorAll('.custom-select-option');
        trigger.addEventListener('click', (e) => {
            e.stopPropagation();
            customSelect.classList.toggle('open');
        });
        options.forEach(opt => {
            opt.addEventListener('click', () => {
                handlePlatformChange(opt.dataset.value);
                customSelect.classList.remove('open');
            });
        });
        document.addEventListener('click', () => {
            customSelect.classList.remove('open');
        });
    }

    // 分类点击
    categoryItems.forEach(item => {
        item.addEventListener('click', handleCategoryClick);
    });

    // 排序点击
    document.querySelectorAll('.sort-tab').forEach(tab => {
        tab.addEventListener('click', (e) => {
            e.preventDefault();
            document.querySelectorAll('.sort-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            currentSort = tab.dataset.sort;
            currentPage = 1;
            renderGames();
        });
    });

    // 搜索（仅点击按钮或回车触发）
    searchBtn.addEventListener('click', handleSearch);
    searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            handleSearch();
            document.getElementById('hotGamesDropdown').style.display = 'none';
        }
    });

    // 热门游戏下拉框
    const hotDropdown = document.getElementById('hotGamesDropdown');
    searchInput.addEventListener('focus', () => {
        if (hotGamesData.length > 0) {
            // 对齐搜索输入框的宽度和位置
            hotDropdown.style.left = searchInput.offsetLeft + 'px';
            hotDropdown.style.width = searchInput.offsetWidth + 'px';
            hotDropdown.style.display = 'block';
        }
    });
    searchInput.addEventListener('blur', () => {
        setTimeout(() => { hotDropdown.style.display = 'none'; }, 200);
    });
    hotDropdown.addEventListener('mousedown', (e) => {
        const item = e.target.closest('.hot-game-item');
        if (item) {
            e.preventDefault();
            searchInput.value = item.dataset.game;
            hotDropdown.style.display = 'none';
            handleSearch();
        }
    });

    // 主题切换
    themeToggle.addEventListener('click', toggleTheme);

    // 返回顶部
    backToTop.addEventListener('click', scrollToTop);
    window.addEventListener('scroll', toggleBackToTop);

    // 游戏详情弹窗关闭
    const modalClose = document.getElementById('gameModalClose');
    const modalOverlay = document.getElementById('gameModalOverlay');
    if (modalClose) {
        modalClose.addEventListener('click', closeGameModal);
    }
    if (modalOverlay) {
        modalOverlay.addEventListener('click', (e) => {
            if (e.target === modalOverlay) {
                closeGameModal();
            }
        });
    }
    document.addEventListener('keydown', (e) => {
        const imgViewer = document.getElementById('imageViewerOverlay');
        if (imgViewer?.classList.contains('active')) {
            if (e.key === 'Escape') {
                closeImageViewer();
            } else if (e.key === 'ArrowLeft') {
                prevScreenshot();
            } else if (e.key === 'ArrowRight') {
                nextScreenshot();
            }
        } else if (e.key === 'Escape') {
            closeGameModal();
        }
    });

    // 图片放大查看器关闭
    const imgViewerClose = document.getElementById('imageViewerClose');
    const imgViewerOverlay = document.getElementById('imageViewerOverlay');
    const imgViewerPrev = document.getElementById('imageViewerPrev');
    const imgViewerNext = document.getElementById('imageViewerNext');
    if (imgViewerClose) {
        imgViewerClose.addEventListener('click', closeImageViewer);
    }
    if (imgViewerPrev) {
        imgViewerPrev.addEventListener('click', prevScreenshot);
    }
    if (imgViewerNext) {
        imgViewerNext.addEventListener('click', nextScreenshot);
    }
    if (imgViewerOverlay) {
        imgViewerOverlay.addEventListener('click', (e) => {
            if (e.target === imgViewerOverlay) {
                closeImageViewer();
            }
        });
    }

    // 自动轮播
    setInterval(nextSlide, 5000);
}

// ==================== 热门游戏 ====================
let hotGamesData = [];

async function loadHotGames() {
    try {
        const [topRes, allRes, dlRes] = await Promise.all([
            fetch(`${HOT_GAMES_API}/top?limit=10`),
            fetch(`${HOT_GAMES_API}/all`),
            fetch(`${HOT_GAMES_API}/all-downloads`)
        ]);
        if (topRes.ok) {
            const data = await topRes.json();
            if (Array.isArray(data) && data.length > 0) {
                hotGamesData = data;
                renderHotGamesDropdown(data);
            }
        }
        if (allRes.ok) {
            const allData = await allRes.json();
            if (Array.isArray(allData)) {
                allClicksMap = {};
                allData.forEach(item => {
                    allClicksMap[item.name] = item.count;
                });
            }
        }
        if (dlRes.ok) {
            const dlData = await dlRes.json();
            if (Array.isArray(dlData)) {
                allDownloadsMap = {};
                dlData.forEach(item => {
                    allDownloadsMap[item.name] = item.count;
                });
            }
        }
    } catch (e) {
        // Worker 不可用就静默跳过
    }
}

function findGamePlatform(gameName) {
    const game = gamesData.find(g => g.title === gameName);
    return game ? game.platform : null;
}

function platformBadgeHtml(platform) {
    if (!platform) return '';
    const labels = { android: 'Android', ns: 'NS', pc: 'PC' };
    return `<span class="hot-game-platform hot-platform-${platform}">${labels[platform]}</span>`;
}

function renderHotGamesDropdown(hotList) {
    const dropdown = document.getElementById('hotGamesDropdown');
    if (!dropdown) return;

    dropdown.innerHTML = `<div class="hot-games-header">
        <svg viewBox="0 0 448 512" width="14" height="14" fill="currentColor" stroke="none"><path d="M323.56 51.2c-20.8 19.3-39.58 39.59-56.22 59.97C240.08 73.62 206.28 35.53 168 0 69.74 91.17 0 209.96 0 281.6 0 408.85 100.18 512 224 512s224-103.15 224-230.4c0-53.27-51.98-163.14-124.44-230.4zm-19.47 340.65C282.43 407.01 255.72 416 226.86 416 154.71 416 96 368.26 96 290.75c0-38.61 24.31-72.63 72.79-130.75 6.93 7.98 98.83 125.34 98.83 125.34l58.63-66.88c4.14 6.85 7.91 13.55 11.27 19.97 27.35 52.19 15.81 118.97-33.43 153.42z"/></svg>
        热门搜索
    </div>` + hotList.map((item, i) => {
        const rankClass = i < 3 ? `hot-game-rank hot-rank-${i + 1}` : 'hot-game-rank';
        const platform = findGamePlatform(item.name);
        return `<a href="#" class="hot-game-item" data-game="${item.name}">
            <span class="${rankClass}">${i + 1}</span>
            ${platformBadgeHtml(platform)}
            <span class="hot-game-name" title="${item.name}">${item.name}</span>
        </a>`;
    }).join('');
}

// ==================== 初始化 ====================
async function init() {
    // 恢复保存的主题（默认浅色）
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-theme');
        document.body.classList.remove('light-theme');
        themeIcon.innerHTML = '<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';
    } else {
        document.body.classList.add('light-theme');
        document.body.classList.remove('dark-theme');
        themeIcon.innerHTML = '<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><path d="M12 1v2m0 18v2M4.22 4.22l1.42 1.42m12.72 12.72l1.42 1.42M1 12h2m18 0h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>';
    }

    // 加载游戏数据
    gamesData = await loadGamesFromJSON();

    // 初始化轮播元素
    slides = document.querySelectorAll('.carousel-slide');

    // 绑定事件
    bindEvents();

    // 渲染
    renderGames();
    showSlide(0);
    toggleBackToTop();

    // 加载热门游戏（不阻塞页面，云端统计关闭时跳过）
    if (ENABLE_CLOUD_STATS) {
        loadHotGames();
    }

    // 云端统计关闭时隐藏热度/下载量排序按钮
    if (!ENABLE_CLOUD_STATS) {
        document.querySelectorAll('.sort-tab[data-sort="hot"], .sort-tab[data-sort="downloads"]').forEach(btn => {
            btn.style.display = 'none';
        });
    }

    // 初始化留言板
    initMessageBoard();
}

document.addEventListener('DOMContentLoaded', init);

// ==================== 留言板 ====================
const MSG_API = ENABLE_CLOUD_STATS ? HOT_GAMES_API : '';

// 敏感词过滤
const BAD_WORDS = ['操', 'fuck', 'shit', 'sb', '傻逼', '草泥马', '鸡巴', '妈的', '狗日', '去死', '王八蛋', '屁眼', '婊子', ' whore', 'dick', 'asshole', 'bastard', 'crap', ' damn'];
function filterProfanity(text) {
    let result = text;
    BAD_WORDS.forEach(word => {
        const re = new RegExp(word, 'gi');
        result = result.replace(re, '**');
    });
    return result;
}

function initMessageBoard() {
    const board = document.getElementById('messageBoard');
    const tab = document.getElementById('msgBoardTab');
    const closeBtn = document.getElementById('msgBoardClose');
    const textarea = document.getElementById('msgBoardContent');
    const countEl = document.getElementById('msgBoardCount');
    const submitBtn = document.getElementById('msgBoardSubmit');
    const hint = document.getElementById('msgHint');

    // 提示气泡：页面加载自动闪烁 3s 后隐藏；悬停显示（不闪烁），移开隐藏
    let hintTimer;
    function showHint(blink) {
        clearTimeout(hintTimer);
        hint.classList.add('show');
        hint.classList.toggle('blink', !!blink);
    }
    function hideHint() {
        clearTimeout(hintTimer);
        hint.classList.remove('show', 'blink');
    }
    showHint(true);
    hintTimer = setTimeout(hideHint, 3000);
    tab.addEventListener('mouseenter', () => showHint(false));
    tab.addEventListener('mouseleave', hideHint);

    // 展开
    tab.addEventListener('click', () => {
        board.classList.remove('collapsed');
    });

    // 收起
    closeBtn.addEventListener('click', () => {
        board.classList.add('collapsed');
    });

    // 点击空白处关闭
    document.addEventListener('click', (e) => {
        if (!board.contains(e.target)) {
            board.classList.add('collapsed');
        }
    });

    // 字数计数
    textarea.addEventListener('input', () => {
        const len = textarea.value.length;
        countEl.textContent = len + '/50';
        countEl.style.color = len >= 45 ? '#e85d04' : '';
    });

    // 提交留言
    submitBtn.addEventListener('click', () => {
        const content = textarea.value.trim();
        if (!content) return;
        if (content.length > 50) return;

        // 频率限制：每30秒一条
        const lastSend = parseInt(localStorage.getItem('msgLastSend') || '0');
        const now = Date.now();
        if (now - lastSend < 30000) {
            startRateLimitCountdown();
            return;
        }

        const name = '匿名用户';
        const filtered = filterProfanity(content);

        submitBtn.disabled = true;
        submitBtn.textContent = '发送中...';

        if (MSG_API) {
            fetch(MSG_API + '/messages', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: name, content: filtered })
            }).then(r => r.json()).then(data => {
                if (data.code === 0) {
                    localStorage.setItem('msgLastSend', Date.now().toString());
                    textarea.value = '';
                    countEl.textContent = '0/50';
                    startRateLimitCountdown();
                } else {
                    alert(data.message || '发送失败');
                    submitBtn.disabled = false;
                    submitBtn.textContent = '发送';
                }
            }).catch(err => {
                alert('网络错误，请稍后重试');
                submitBtn.disabled = false;
                submitBtn.textContent = '发送';
            });
        } else {
            // 无后端时的本地演示
            const msg = {
                name: name,
                content: filtered,
                time: new Date().toISOString()
            };
            let localMsgs = JSON.parse(localStorage.getItem('localMessages') || '[]');
            localMsgs.unshift(msg);
            localMsgs = localMsgs.slice(0, 50);
            localStorage.setItem('localMessages', JSON.stringify(localMsgs));
            localStorage.setItem('msgLastSend', Date.now().toString());
            textarea.value = '';
            countEl.textContent = '0/50';
            startRateLimitCountdown();
        }
    });

    // 频率限制：冷却期间按钮显示"留言成功，X秒后可继续留言"实时倒计时，30秒后恢复
    function startRateLimitCountdown() {
        const lastSend = parseInt(localStorage.getItem('msgLastSend') || '0');
        const elapsed = Date.now() - lastSend;
        if (elapsed < 30000) {
            const remain = Math.ceil((30000 - elapsed) / 1000);
            submitBtn.textContent = '留言成功，' + remain + '秒后可继续留言';
            submitBtn.disabled = true;
            const timer = setInterval(() => {
                const r = Math.ceil((30000 - (Date.now() - lastSend)) / 1000);
                if (r <= 0) {
                    clearInterval(timer);
                    submitBtn.textContent = '发送';
                    submitBtn.disabled = false;
                } else {
                    submitBtn.textContent = '留言成功，' + r + '秒后可继续留言';
                }
            }, 1000);
        }
    }

    // 页面加载时检查频率限制
    startRateLimitCountdown();
}
