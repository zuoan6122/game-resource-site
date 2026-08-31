import json
import urllib.request
from PIL import Image, ImageDraw, ImageFilter
import io
import os

# 读取游戏数据
d = json.load(open('data/games.json','r',encoding='utf-8'))
pc = [g for g in d if g['platform']=='pc' and g.get('coverImage')]
pc.sort(key=lambda x: x.get('reviewScore', 0), reverse=True)

# 挑评分最高的12个游戏封面
selected = pc[:12]

# 轮播图尺寸（宽屏banner）
banner_w = 1600
banner_h = 500
bg = Image.new('RGB', (banner_w, banner_h), (20, 22, 26))

# 封面尺寸
cover_w = 230
cover_h = 110  # Steam header图比例约 2:1
cols = 6
rows = 2
gap_x = 30
gap_y = 25
start_x = (banner_w - (cols * cover_w + (cols - 1) * gap_x)) // 2
start_y = (banner_h - (rows * cover_h + (rows - 1) * gap_y)) // 2

for i, game in enumerate(selected):
    try:
        req = urllib.request.Request(game['coverImage'], headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=10)
        img = Image.open(io.BytesIO(resp.read())).convert('RGB')
        img = img.resize((cover_w, cover_h), Image.LANCZOS)
        
        # 加圆角
        mask = Image.new('L', (cover_w, cover_h), 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([(0, 0), (cover_w, cover_h)], radius=8, fill=255)
        
        row = i // cols
        col = i % cols
        x = start_x + col * (cover_w + gap_x)
        y = start_y + row * (cover_h + gap_y)
        
        # 加轻微阴影效果（用底层放大一点的暗色图模拟）
        shadow = Image.new('RGBA', (cover_w + 4, cover_h + 4), (0, 0, 0, 80))
        shadow_mask = Image.new('L', (cover_w + 4, cover_h + 4), 0)
        shadow_draw = ImageDraw.Draw(shadow_mask)
        shadow_draw.rounded_rectangle([(0, 0), (cover_w + 4, cover_h + 4)], radius=10, fill=255)
        bg.paste(shadow, (x - 2, y - 2 + 3), shadow_mask)
        
        # 粘贴封面
        bg.paste(img, (x, y), mask)
        
        print(f"✓ {game['title']}")
    except Exception as e:
        print(f"✗ {game['title']}: {e}")

# 顶部渐变遮罩（让标题区域更清晰）
overlay = Image.new('RGBA', (banner_w, banner_h), (0, 0, 0, 0))
draw = ImageDraw.Draw(overlay)
for y in range(120):
    alpha = int(180 * (1 - y / 120))
    draw.line([(0, y), (banner_w, y)], fill=(0, 0, 0, alpha))

bg = bg.convert('RGBA')
bg = Image.alpha_composite(bg, overlay)
bg = bg.convert('RGB')

# 保存
os.makedirs('images', exist_ok=True)
output_path = 'images/banner-collage.jpg'
bg.save(output_path, quality=90)
print(f"\n已保存到: {output_path}")
print(f"尺寸: {banner_w} x {banner_h}")
