# -*- coding: utf-8 -*-
"""批量根据 games.json 中的 downloadUrl 生成二维码，并写回 qrCode 字段"""
import json
import os
import hashlib
import qrcode
from qrcode.constants import ERROR_CORRECT_M

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, 'data', 'games.json')
QR_DIR = os.path.join(BASE, 'images', 'qrcodes')
os.makedirs(QR_DIR, exist_ok=True)

with open(DATA, encoding='utf-8') as f:
    games = json.load(f)

count = 0
referenced = set()
for game in games:
    if game.get('platform') != 'pc':
        game.pop('qrCode', None)
        continue
    url = game.get('downloadUrl')
    if not url:
        continue
    digest = hashlib.md5(url.encode('utf-8')).hexdigest()[:8]
    fname = f'qr_{digest}.png'
    path = os.path.join(QR_DIR, fname)
    if not os.path.exists(path):
        qr = qrcode.QRCode(version=None, error_correction=ERROR_CORRECT_M, box_size=6, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        qr.make_image(fill_color='black', back_color='white').save(path)
    game['qrCode'] = f'images/qrcodes/{fname}'
    referenced.add(fname)
    count += 1

# 删除未被 PC 游戏引用的多余二维码文件
for f in os.listdir(QR_DIR):
    if f not in referenced:
        os.remove(os.path.join(QR_DIR, f))

with open(DATA, 'w', encoding='utf-8') as f:
    json.dump(games, f, ensure_ascii=False, indent=2)

print(f'共处理 {count} 个游戏，二维码已保存到 images/qrcodes/')
