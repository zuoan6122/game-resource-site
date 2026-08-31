# -*- coding: utf-8 -*-
"""补充搜索：确认剩余未匹配游戏的港区名称"""
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
    'orochi', '蛇魔', '大蛇', '无双',
    'symphonia', '仙乐', '仙樂', '交響曲傳奇',
    'tomb raider', '古墓奇兵', '古墓丽影', '古墓麗影',
    'animal well', '動物井', 'animal',
    'sanctuary', '避難所', '避难所',
    'splatoon', '斯普拉遁', '喷射战士',
    'overcooked', '煮過頭',
    'stardew', '星露',
    'hollow knight', '空洞騎士',
    'celeste', '蔚藍',
    'ori and', '聖靈之光',
    'captain toad', '奇諾比奧隊長',
    'crysis', '末日之戰', '孤島危機',
    'bioshock', '生化奇兵',
    'divinity', '神諭', '神界',
    'naruto', '火影忍者',
    'steamworld quest', '蒸汽世界冒險',
    'house of the dead', '死亡之屋',
    'castle crashers', '城堡破壞者',
    'grid autosport', '房車賽',
    'ruined king', '破敗王者',
    'max curse', '兄弟魔咒', '麥克斯',
    'amalur', '阿瑪拉王國',
    'black future', '黑色未來',
    'fog', '霧隱戰記', '雾隐',
    'dead rising', '勇闖死人谷',
    'mercenaries', '傭兵傳說',
    'kof', '拳皇', '94',
    'metal slug', '合金彈頭',
    'world war z', '殭屍世界大戰',
    'doom', '毀滅戰士',
    'nightmare knight', '噩夢騎士',
    'dragon ball heroes', '七龍珠英雄',
    'symphonia', '交響曲',
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
