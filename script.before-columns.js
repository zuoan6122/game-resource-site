// ==================== 状态管理 ====================
let gamesData = [];
let dropdownPlatform = 'all';
let currentPlatform = 'all';
let currentCategory = 'all';
let searchQuery = '';
let currentPage = 1;
const pageSize = 20; // 每页显示数量

const platformLabels = { android: '安卓', ns: 'NS', pc: 'PC' };
const platformOrder = { android: 0, ns: 1, pc: 2 };
const platformIcons = {
    android: '<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M6 9a1 1 0 0 0-1 1v4a1 1 0 0 0 2 0v-4a1 1 0 0 0-1-1zm12 0a1 1 0 0 0-1 1v4a1 1 0 0 0 2 0v-4a1 1 0 0 0-1-1zM7 10v5a1 1 0 0 0 1 1h1v2.5a1 1 0 0 0 2 0V16h2v2.5a1 1 0 0 0 2 0V16h1a1 1 0 0 0 1-1v-5H7zm8.5-3.5l1.2-1.8a.4.4 0 0 0-.66-.44l-1.3 1.95A5.97 5.97 0 0 0 12 6c-1.05 0-2.04.27-2.9.75L7.8 4.8a.4.4 0 0 0-.56.56l1.2 1.8A5.98 5.98 0 0 0 6 12h12a5.98 5.98 0 0 0-2.5-5.5zM10 9a.75.75 0 1 0 0-1.5A.75.75 0 0 0 10 9zm4 0a.75.75 0 1 0 0-1.5A.75.75 0 0 0 14 9z"/></svg>',
    ns: '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="2" y="6" width="8" height="12" rx="2"/><rect x="14" y="6" width="8" height="12" rx="2"/><circle cx="6" cy="12" r="1.5" fill="currentColor" stroke="none"/><circle cx="18" cy="10" r="0.9" fill="currentColor" stroke="none"/><circle cx="18" cy="14" r="0.9" fill="currentColor" stroke="none"/></svg>',
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

// ==================== 从JSON加载数据 ====================
async function loadGamesFromJSON() {
    try {
        const response = await fetch(`data/games.json?t=${Date.now()}`);
        if (!response.ok) throw new Error('网络请求失败');
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('加载游戏数据失败:', error);
        return [];
    }
}

// ==================== 获取过滤后的游戏 ====================
function getFilteredGames() {
    if (searchQuery) {
        // 搜索时：下拉框平台 + 关键词
        const filtered = gamesData.filter(game => {
            const matchPlatform = dropdownPlatform === 'all' || game.platform === dropdownPlatform;
            const matchSearch = game.title.toLowerCase().includes(searchQuery.toLowerCase());
            return matchPlatform && matchSearch;
        });
        if (dropdownPlatform === 'all') {
            filtered.sort((a, b) => (platformOrder[a.platform] ?? 99) - (platformOrder[b.platform] ?? 99));
        }
        return filtered;
    } else {
        // 浏览时：平台标签 + 类型
        const filtered = gamesData.filter(game => {
            const matchPlatform = currentPlatform === 'all' || game.platform === currentPlatform;
            const matchCategory = currentCategory === 'all' || game.category === currentCategory;
            return matchPlatform && matchCategory;
        });
        if (currentPlatform === 'all') {
            filtered.sort((a, b) => (platformOrder[a.platform] ?? 99) - (platformOrder[b.platform] ?? 99));
        }
        return filtered;
    }
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
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M6 11h4m-2-2v4"/><circle cx="15" cy="11" r="1"/><circle cx="18" cy="13" r="1"/><path d="M17.32 4H6.68a4 4 0 0 0-3.78 2.72L2 11a2 2 0 0 0 0 2l.9 4.28A4 4 0 0 0 6.68 20h10.64a4 4 0 0 0 3.78-2.72L22 13a2 2 0 0 0 0-2l-.9-4.28A4 4 0 0 0 17.32 4z"/></svg>
               </div>`;
        const coverHtml = game.coverImage
            ? `<img src="${game.coverImage}" alt="${game.title}" class="game-cover-img" loading="lazy" onerror="this.style.display='none';this.nextElementSibling.style.display='flex'">${placeholderSvg.replace('class="game-cover-placeholder"', 'class="game-cover-placeholder" style="display:none;"')}`
            : placeholderSvg;
        card.innerHTML = `
            <div class="game-cover">
                ${coverHtml}
            </div>
            <div class="game-info">
                <h3 class="game-title" title="${game.title}">${game.title}</h3>
                <div class="game-tags">
                    <span class="platform-badge platform-${game.platform}">${platformIcons[game.platform] || ''}<span class="platform-text">${platformLabels[game.platform] || ''}</span></span>
                    <span class="game-tag">${categoryNames[game.category] || '其他'}</span>
                </div>
                <a href="${game.downloadUrl}" class="download-btn" target="_blank">跳转</a>
            </div>
        `;

        // PC游戏有详情弹窗，点击封面或标题打开
        if (game.platform === 'pc' && game.coverImage) {
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

    // 无搜索条件时立即渲染
    if (!searchQuery) {
        renderGames();
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
let indicators = [];

function showSlide(index) {
    slides.forEach(slide => slide.classList.remove('active'));
    indicators.forEach(indicator => indicator.classList.remove('active'));
    slides[index].classList.add('active');
    indicators[index].classList.add('active');
}

function nextSlide() {
    currentSlide = (currentSlide + 1) % slides.length;
    showSlide(currentSlide);
}

function handleIndicatorClick(e) {
    const index = parseInt(e.target.dataset.slide);
    currentSlide = index;
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

    const scoreDesc = reviewScoreMap[game.reviewScoreDesc] || game.reviewScoreDesc || '';
    const starsHtml = game.reviewScore != null ? buildStars(game.reviewScore) : '';

    let screenshotsHtml = '';
    if (game.screenshots) {
        const urls = game.screenshots.split(',');
        if (urls.length > 0) {
            screenshotsHtml = '<div class="modal-screenshots-section"><div class="modal-screenshots-title">游戏截图</div><div class="modal-screenshots">';
            urls.slice(0, 2).forEach(url => {
                screenshotsHtml += `<img src="${url}" alt="截图" loading="lazy" class="screenshot-clickable" data-src="${url}">`;
            });
            screenshotsHtml += '</div></div>';
        }
    }

    content.innerHTML = `
        <div class="modal-cover-wrapper">
            <img src="${game.coverImage}" alt="${game.title}" class="modal-cover">
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
            <div class="modal-desc">${game.description || '暂无简介'}</div>
            <div class="modal-qr-section">
                <div class="modal-qr-title">夸克网盘转存</div>
                <div class="modal-qr-img">
                    <svg viewBox="0 0 150 150" width="150" height="150">
                        <rect x="0" y="0" width="150" height="150" fill="#fff"/>
                        <text x="75" y="82" text-anchor="middle" font-size="20" fill="#bbb" font-weight="500">二维码</text>
                    </svg>
                </div>
                <div class="modal-qr-steps-title">下载小贴士</div>
                <ol class="modal-qr-steps">
                    <li>使用网盘软件或者微信或 QQ 扫描二维码。</li>
                    <li>扫描后，点击"去APP内查看/保存"按钮。</li>
                    <li>跳转到网盘 APP，将资源转存到自己账号（若未安装该 App，请下载）。</li>
                    <li>在电脑端登录网盘账号，找到转存好的游戏文件，即可下载。</li>
                </ol>
            </div>
            ${screenshotsHtml}
        </div>
    `;

    // 绑定截图点击事件
    const screenshotUrls = game.screenshots ? game.screenshots.split(',').slice(0, 2) : [];
    content.querySelectorAll('.screenshot-clickable').forEach((img, idx) => {
        img.addEventListener('click', () => {
            openImageViewer(screenshotUrls, idx);
        });
    });

    // 绑定下载小贴士展开/收起
    const stepsTitle = content.querySelector('.modal-qr-steps-title');
    const stepsList = content.querySelector('.modal-qr-steps');
    if (stepsTitle && stepsList) {
        stepsTitle.addEventListener('click', () => {
            stepsTitle.classList.toggle('expanded');
            stepsList.classList.toggle('expanded');
        });
    }

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
    if (!overlay || !img) return;

    currentScreenshots = screenshots;
    currentScreenshotIndex = index;

    img.src = screenshots[index];
    overlay.classList.add('active');

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

    // 搜索（仅点击按钮或回车触发）
    searchBtn.addEventListener('click', handleSearch);
    searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
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

    // 轮播图指示器
    indicators.forEach(indicator => {
        indicator.addEventListener('click', handleIndicatorClick);
    });

    // 自动轮播
    setInterval(nextSlide, 5000);
}

// ==================== 初始化 ====================
async function init() {
    // 恢复保存的主题
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
        document.body.classList.add('light-theme');
        document.body.classList.remove('dark-theme');
        themeIcon.innerHTML = '<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><path d="M12 1v2m0 18v2M4.22 4.22l1.42 1.42m12.72 12.72l1.42 1.42M1 12h2m18 0h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>';
    }

    // 加载游戏数据
    gamesData = await loadGamesFromJSON();

    // 初始化轮播元素
    slides = document.querySelectorAll('.carousel-slide');
    indicators = document.querySelectorAll('.indicator');

    // 绑定事件
    bindEvents();

    // 渲染
    renderGames();
    showSlide(0);
    toggleBackToTop();
}

document.addEventListener('DOMContentLoaded', init);
