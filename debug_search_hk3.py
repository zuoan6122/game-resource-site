# -*- coding: utf-8 -*-
"""最后一轮港区搜索：预计算所有norm加速"""
import json, os
from gen_ns_data import normalize

BASE = os.path.dirname(os.path.abspath(__file__))
TITLEDB = os.path.join(BASE, 'data', 'HK.zh.json')

with open(TITLEDB, encoding='utf-8') as f:
    data = json.load(f)

# 预计算所有条目的 norm
all_entries = []
for nsuid, info in data.items():
    name = info.get('name')
    if isinstance(name, str):
        all_entries.append((name, info.get('id'), normalize(name)))

keywords = [
    'steamworld quest', '蒸汽世界冒险', '蒸汽世界冒險', 'quest', '吉尔伽美什', '吉爾伽美什',
    'ori and the blind', '奥日与黑暗森林', '奧日與黑暗森林', 'blind forest', '黑暗森林',
    '3d all-stars', '3d all stars', '全明星', '收藏輯', '收藏辑',
    'new super mario', '新超级马里奥', '新超級瑪利歐', '兄弟u', '兄弟U', 'deluxe',
    'six star', '六星', '观星者', '觀星者', 'stargazer',
    'captain toad', '奇诺比奥队长', '奇諾比奧隊長', 'treasure tracker',
    'hollow knight', '空洞骑士', '空洞騎士',
    'stardew', '星露谷', '星露穀物語',
    'celeste', '蔚蓝', '蔚藍',
    'bioshock', '生化奇兵',
    'crysis', '孤岛危机', '孤島危機',
    'divinity', '神界', '原罪',
    'castle crashers', '城堡破坏者', '城堡破壞者',
    'world war z', '僵尸世界大战', '殭屍世界大戰',
    'super dragon ball', '超龙珠', '超七龍珠',
    'mercenaries', '佣兵传说', '傭兵傳說',
    'metal slug 1', '合金弹头1', '合金彈頭1', 'anthology',
    'house of the dead', '死亡之屋',
    'black future', '黑色未来', '黑色未來',
    'fog', '雾隐', '霧隱',
    'max', '麦克斯', '兄弟魔咒',
    'dead rising', '勇闯死人谷', '勇闖死人谷',
    'fumamuxingzhe', '伏魔行者',
    'mirror', '魔镜', '魔鏡',
    'darksiders', '暗黑血统', '暗黑血統',
    'achilles', '阿喀琉斯',
    'dicefolk', '魔骰', '神骰',
    'six star gate', '六星之门', '六星之門',
]

for kw in keywords:
    kw_norm = normalize(kw)
    hits = []
    for name, tid, norm in all_entries:
        if kw_norm and (kw_norm in norm or norm in kw_norm):
            hits.append((name, tid))
        elif kw.lower() in name.lower():
            hits.append((name, tid))
    print(f'===== {kw} =====')
    if hits:
        for name, tid in hits[:6]:
            print(f'  {name}  ({tid})')
    else:
        print('  无匹配')
    print()
