# -*- coding: utf-8 -*-
"""抽查匹配质量：随机打印匹配结果供人工检查"""
import json, os, random
from gen_ns_data import clean_title, match_title, load_titledb

BASE = os.path.dirname(os.path.abspath(__file__))
TITLEDB = os.path.join(BASE, 'data', 'HK.zh.json')
DATA = os.path.join(BASE, 'data', 'games.json')

with open(DATA, encoding='utf-8') as f:
    games = json.load(f)
ns = [g for g in games if g.get('platform') == 'ns' and 'coverImage' in g]
entries = load_titledb(TITLEDB)
norm_map = {}
for e in entries:
    norm_map.setdefault(e['norm'], []).append(e)

random.seed(7)
sample = random.sample(ns, 25)
for g in sample:
    cleaned = clean_title(g['title'])
    mtype, e = match_title(cleaned, norm_map, entries)
    print(f'{g["title"][:42]:<44} -> {e["name"][:52]}')
