# -*- coding: utf-8 -*-
"""补充搜索：用英文名搜索港区TitleDB"""
import json, os
from gen_ns_data import normalize

BASE = os.path.dirname(os.path.abspath(__file__))
TITLEDB = os.path.join(BASE, 'data', 'HK.zh.json')

with open(TITLEDB, encoding='utf-8') as f:
    data = json.load(f)

entries = []
for nsuid, info in data.items():
    tid = info.get('id')
    name = info.get('name')
    if tid and name:
        entries.append({'tid': tid, 'name': name, 'norm': normalize(name)})

keywords = [
    'ruined king', 'league of legends', '英雄聯盟',
    'dragon ball', 'heroes',
    'mercenaries', 'chronicles',
    'nightmare', 'knight',
    'grid', 'autosport', 'racing',
    'max', 'curse', 'brotherhood',
    'captain toad', 'toad', 'treasure tracker',
    'into the dead', 'dead',
    'black future', 'future',
    'house of the dead', 'house',
    'castle crashers', 'crashers',
    'world war', 'zombie',
    'saint', 'tower', '圣塔',
    'fog', 'mist',
    'fumamuxingzhe', 'fuma',
    'salt', 'sanctuary',
    'animal well', 'well',
    'ori', 'blind forest',
    'hollow', 'knight',
    'stardew', 'valley',
    'celeste',
    'tomb raider', 'raider',
    'symphonia',
    'overcooked',
    'darksiders',
    'grand theft',
    'orochi',
    'bioshock',
    'crysis',
    'divinity', 'original sin',
    'naruto', 'storm',
    'steamworld', 'quest', 'gilgamech',
    'doom',
    'metal slug',
    'kof', 'king of fighters',
    'world war z',
]

seen = set()
for kw in keywords:
    kwn = normalize(kw)
    if not kwn or kwn in seen:
        continue
    seen.add(kwn)
    hits = []
    for e in entries:
        if kwn in e['norm'] or e['norm'] in kwn:
            hits.append(e)
    if hits:
        print(f'===== {kw} =====')
        for e in hits[:8]:
            print(f'  {e["name"]}  ({e["tid"]})')
        print()
