# -*- coding: utf-8 -*-
"""调试：检查特定游戏的归一化结果和匹配情况"""
import json, os
from gen_ns_data import clean_title, normalize, match_title, load_titledb

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, 'data', 'games.json')
TITLEDB = os.path.join(BASE, 'data', 'HK.zh.json')

with open(DATA, encoding='utf-8') as f:
    games = json.load(f)
ns_games = [g for g in games if g.get('platform') == 'ns']
entries = load_titledb(TITLEDB)
norm_map = {}
for e in entries:
    norm_map.setdefault(e['norm'], []).append(e)

tests = [
    '塞尔达无双 海拉鲁全明星DX+1.0.1升补（中文）',
    '王国：两位君主+2.2.0升补+2DLC（中文）',
    '古墓丽影4-6重制版+1.0.1升补（中文）',
    '仙乐传说 重制版+1.1.0升补（中文）',
    '圣恩传说F：重制版+1.0.3升补+9DLC（中文）',
    '胡闹厨房1+1.1.1升补',
    '暗黑血统123+创世纪(中文)',
    '宝可梦 去吧,皮卡丘!+1.0.2升补（中文）',
    '小骨：英雄杀手+1.9.2升补+1DLC',
    'GTA三部曲终极版+1.0.7升补（中文）',
]

for raw in tests:
    cleaned = clean_title(raw)
    norm = normalize(cleaned)
    mtype, e = match_title(cleaned, norm_map, entries)
    print(f'===== {raw}')
    print(f'  清洗后: {cleaned}')
    print(f'  norm: {norm}')
    if mtype:
        print(f'  [{mtype}] -> {e["name"]} ({e["tid"]})')
    else:
        # 找港区相似
        found = False
        for en in entries:
            if norm and (norm in en['norm'] or en['norm'] in norm):
                print(f'  [相似] {en["name"]} ({en["tid"]}) norm={en["norm"]}')
                found = True
        if not found:
            print(f'  港区无相似')
    print()
