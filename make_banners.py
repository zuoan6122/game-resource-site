import json
import urllib.request
from PIL import Image, ImageDraw, ImageFilter
import io
import os
import random

# 读取游戏数据
d = json.load(open('data/games.json','r',encoding='utf-8'))
pc = [g for g in d if g['platform']=='pc' and g.get('coverImage')]
pc.sort(key=lambda x: x.get('reviewScore', 0), reverse=True)
top_games = pc[:20]  # 取前20个高分游戏备用

os.makedirs('images', exist_ok=True)

def download_cover(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=10)
        return Image.open(io.BytesIO(resp.read())).convert('RGB')
    except:
        return None

def add_rounded_corners(img, radius):
    mask = Image.new('L', img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), img.size], radius=radius, fill=255)
    result = img.copy()
    result.putalpha(mask)
    return result

# 预下载封面
covers = []
for g in top_games:
    img = download_cover(g['coverImage'])
    if img:
        covers.append(img)
    if len(covers) >= 16:
        break

print(f"下载了 {len(covers)} 张封面")

# ============================================================
# 风格1：密集海报墙（多张小封面错落排列，带倾斜角度）
# ============================================================
def make_poster_wall():
    w, h = 1600, 500
    bg = Image.new('RGB', (w, h), (25, 27, 31))
    draw = ImageDraw.Draw(bg, 'RGBA')
    
    # 背景加一些装饰圆点
    for _ in range(30):
        x = random.randint(0, w)
        y = random.randint(0, h)
        r = random.randint(2, 8)
        alpha = random.randint(10, 30)
        draw.ellipse([x-r, y-r, x+r, y+r], fill=(245, 124, 51, alpha))
    
    # 选10张封面，随机大小和角度
    selected = random.sample(covers, min(10, len(covers)))
    positions = []
    
    # 网格基础位置 + 随机偏移
    cols = 5
    rows = 2
    base_w = w / (cols + 0.5)
    base_h = h / (rows + 0.5)
    
    idx = 0
    for row in range(rows):
        for col in range(cols):
            if idx >= len(selected):
                break
            img = selected[idx].copy()
            # 随机缩放 0.8~1.2
            scale = random.uniform(0.85, 1.15)
            cw = int(base_w * scale)
            ch = int(cw * 0.45)  # 2:1 比例
            img = img.resize((cw, ch), Image.LANCZOS)
            
            # 随机旋转 -6~6度
            angle = random.uniform(-6, 6)
            img = img.rotate(angle, resample=Image.BICUBIC, expand=True)
            img = add_rounded_corners(img, 6)
            
            # 位置
            bx = int(col * base_w + base_w * 0.3)
            by = int(row * base_h + base_h * 0.25)
            offset_x = random.randint(-15, 15)
            offset_y = random.randint(-10, 10)
            
            x = bx + offset_x
            y = by + offset_y
            
            # 阴影
            shadow = Image.new('RGBA', img.size, (0, 0, 0, 0))
            shadow_draw = ImageDraw.Draw(shadow)
            shadow_draw.rounded_rectangle([(3, 3), (img.size[0]+3, img.size[1]+3)], radius=6, fill=(0, 0, 0, 60))
            bg.paste(shadow, (x, y), shadow)
            
            bg.paste(img, (x, y), img)
            idx += 1
    
    # 左右渐变暗角
    for x in range(150):
        alpha = int(200 * (1 - x / 150))
        draw.line([(x, 0), (x, h)], fill=(25, 27, 31, alpha))
    for x in range(150):
        alpha = int(200 * (x / 150))
        draw.line([(w-150+x, 0), (w-150+x, h)], fill=(25, 27, 31, alpha))
    
    return bg

# ============================================================
# 风格2：横向滚动条风格（封面连续排列，有透视感）
# ============================================================
def make_horizontal_row():
    w, h = 1600, 500
    bg = Image.new('RGB', (w, h), (30, 32, 38))
    
    # 背景渐变
    draw = ImageDraw.Draw(bg)
    for y in range(h):
        t = y / h
        r = int(30 + 15 * t)
        g = int(32 + 15 * t)
        b = int(38 + 20 * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    
    # 选中8张封面，中间大两边小
    selected = covers[:8]
    center_idx = 3.5  # 中间位置
    center_x = w // 2
    center_y = h // 2
    
    items = []
    for i, cover in enumerate(selected):
        # 距离中心越远越小
        dist = abs(i - center_idx)
        scale = max(0.55, 1 - dist * 0.15)
        cw = int(320 * scale)
        ch = int(cw * 0.47)
        img = cover.resize((cw, ch), Image.LANCZOS)
        img = add_rounded_corners(img, 8)
        
        # x位置
        offset = (i - center_idx) * 180 * scale
        x = int(center_x + offset - cw / 2)
        y = int(center_y - ch / 2)
        
        # z-index：中间的在上面
        z = -abs(i - center_idx)
        
        items.append((z, x, y, img))
    
    # 按z排序，从后往前画
    items.sort(key=lambda x: x[0])
    for z, x, y, img in items:
        # 阴影
        shadow = Image.new('RGBA', img.size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow)
        sd.rounded_rectangle([(4, 4), (img.size[0]+4, img.size[1]+4)], radius=8, fill=(0, 0, 0, 50))
        bg.paste(shadow, (x, y), shadow)
        bg.paste(img, (x, y), img)
    
    return bg

# ============================================================
# 风格3：网格整齐排列 + 彩色背景（清新风格）
# ============================================================
def make_grid_clean():
    w, h = 1600, 500
    # 渐变背景（橙色系，呼应主题色）
    bg = Image.new('RGB', (w, h), (45, 48, 54))
    draw = ImageDraw.Draw(bg)
    
    # 顶部橙色光晕
    bg = bg.convert('RGBA')
    glow = Image.new('RGBA', (w, 300), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for i in range(150):
        alpha = int(50 * (1 - i / 150))
        gd.ellipse([w//2 - 600 - i*4, -100 - i, w//2 + 600 + i*4, 200 + i], 
                   fill=(245, 124, 51, alpha))
    # 把glow贴到bg顶部
    bg.paste(glow, (0, 0), glow)
    bg = bg.convert('RGB')
    draw = ImageDraw.Draw(bg)
    
    selected = covers[:10]
    cols = 5
    rows = 2
    cw = 240
    ch = 110
    gap_x = 28
    gap_y = 24
    
    total_w = cols * cw + (cols - 1) * gap_x
    total_h = rows * ch + (rows - 1) * gap_y
    start_x = (w - total_w) // 2
    start_y = (h - total_h) // 2
    
    for i, cover in enumerate(selected):
        if i >= cols * rows:
            break
        row = i // cols
        col = i % cols
        x = start_x + col * (cw + gap_x)
        y = start_y + row * (ch + gap_y)
        
        img = cover.resize((cw, ch), Image.LANCZOS)
        img = add_rounded_corners(img, 10)
        
        # 卡片底色（白色边框效果）
        card = Image.new('RGBA', (cw + 4, ch + 4), (60, 63, 70, 255))
        card_draw = ImageDraw.Draw(card)
        card_draw.rounded_rectangle([(0, 0), (cw+4, ch+4)], radius=12, fill=(60, 63, 70, 255))
        bg.paste(card, (x-2, y-2), card)
        
        bg.paste(img, (x, y), img)
    
    return bg

# ============================================================
# 风格4：散落漂浮风格（大小不一，自由散落）
# ============================================================
def make_floating():
    w, h = 1600, 500
    # 深色渐变背景
    bg = Image.new('RGB', (w, h), (20, 22, 26))
    draw = ImageDraw.Draw(bg)
    for y in range(h):
        t = y / h
        r = int(20 + 10 * t)
        g = int(22 + 10 * t)
        b = int(26 + 12 * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    
    selected = random.sample(covers, min(12, len(covers)))
    
    for i, cover in enumerate(selected):
        scale = random.uniform(0.7, 1.3)
        cw = int(200 * scale)
        ch = int(cw * 0.47)
        img = cover.resize((cw, ch), Image.LANCZOS)
        
        # 随机旋转
        angle = random.uniform(-8, 8)
        img = img.rotate(angle, resample=Image.BICUBIC, expand=True)
        img = add_rounded_corners(img, 8)
        
        # 随机位置
        x = random.randint(30, w - cw - 30)
        y = random.randint(30, h - ch - 30)
        
        # 阴影
        shadow_offset = int(6 * scale)
        shadow = Image.new('RGBA', (img.size[0] + shadow_offset, img.size[1] + shadow_offset), (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow)
        sd.rounded_rectangle([(shadow_offset, shadow_offset), (img.size[0]+shadow_offset, img.size[1]+shadow_offset)], 
                           radius=8, fill=(0, 0, 0, 70))
        bg.paste(shadow, (x, y), shadow)
        
        bg.paste(img, (x, y), img)
    
    return bg

# 生成所有风格
styles = [
    ('poster-wall', make_poster_wall, '海报墙风格（错落倾斜）'),
    ('horizontal-row', make_horizontal_row, '横向透视风格（中间大两边小）'),
    ('grid-clean', make_grid_clean, '整齐网格风格（带卡片边框）'),
    ('floating', make_floating, '散落漂浮风格（自由散落）'),
]

for name, func, desc in styles:
    print(f"生成中: {desc}...")
    random.seed(42)  # 固定随机种子，可复现
    img = func()
    path = f'images/banner-{name}.jpg'
    img.save(path, quality=90)
    print(f"  已保存: {path}")

print("\n全部完成！")
