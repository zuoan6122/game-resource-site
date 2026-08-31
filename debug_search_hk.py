# -*- coding: utf-8 -*-
"""搜索TitleDB港区数据，确认不确定游戏的港区译名"""
import json, os
from gen_ns_data import normalize

BASE = os.path.dirname(os.path.abspath(__file__))
TITLEDB = os.path.join(BASE, 'data', 'HK.zh.json')

with open(TITLEDB, encoding='utf-8') as f:
    data = json.load(f)

keywords = [
    'ninja gaiden', '忍者龙剑传', '忍者外傳', '忍者外传',
    'fighterz', '斗士', 'dragon ball fighter',
    'shin megami', '真女神', 'vengeance',
    'hollow', '空洞',
    'stardew', '星露',
    'celeste', '蔚蓝', '蔚藍',
    'asphalt', '狂野',
    'front mission', '前线任务', '前線任務',
    'hogwarts', '霍格',
    'amalur', '阿玛拉', '阿瑪拉',
    'tactics ogre', '皇家骑士团', '皇家騎士團',
    'arkham', '阿卡姆',
    'kingdom come', '天国',
    'batman', '蝙蝠侠', '蝙蝠俠',
    'doom eternal', '永恒', 'doom',
    'nier automata', '机械纪元', '尼爾',
    'kingdomsofamalur',
]

for kw in keywords:
    kw_norm = normalize(kw)
    print(f'\n===== 关键词: {kw} (norm={kw_norm}) =====')
    hits = []
    for nsuid, info in data.items():
        name = info.get('name')
        if not isinstance(name, str):
            continue
        norm = normalize(name)
        if kw_norm and (kw_norm in norm or norm in kw_norm):
            hits.append((name, info.get('id')))
        elif kw.lower() in name.lower():
            hits.append((name, info.get('id')))
    if hits:
        for name, tid in hits[:8]:
            print(f'  {name}  ({tid})')
    else:
        print('  无匹配')
