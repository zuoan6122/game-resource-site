# -*- coding: utf-8 -*-
"""检查怪物猎人系列和真人快打的当前匹配"""
import json, os
from gen_ns_data import clean_title, match_title, load_titledb

BASE = os.path.dirname(os.path.abspath(__file__))
TITLEDB = os.path.join(BASE, 'data', 'HK.zh.json')
DATA = os.path.join(BASE, 'data', 'games.json')

with open(DATA, encoding='utf-8') as f:
    games = json.load(f)
ns = [g for g in games if g.get('platform') == 'ns']
entries = load_titledb(TITLEDB)
norm_map = {}
for e in entries:
    norm_map.setdefault(e['norm'], []).append(e)

for g in ns:
    if '怪物猎人' in g['title'] or '真人快打' in g['title']:
        cleaned = clean_title(g['title'])
        mtype, e = match_title(cleaned, norm_map, entries)
        print(f'{g["title"]}')
        print(f'   -> [{mtype}] {e["name"]} ({e["tid"]})' if e else '   -> 未匹配')
