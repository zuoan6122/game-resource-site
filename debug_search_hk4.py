# -*- coding: utf-8 -*-
"""搜索港区TitleDB中是否存在这些未匹配游戏，确认港区名称"""
import json, os
from gen_ns_data import normalize

BASE = os.path.dirname(os.path.abspath(__file__))
TITLEDB = os.path.join(BASE, 'data', 'HK.zh.json')

with open(TITLEDB, encoding='utf-8') as f:
    data = json.load(f)

# 预计算所有条目的 norm
entries = []
for nsuid, info in data.items():
    tid = info.get('id')
    name = info.get('name')
    if tid and name:
        entries.append({'tid': tid, 'name': name, 'norm': normalize(name)})

# 关键词列表：每个关键词搜索港区名称
keywords = [
    'zelda', 'hyrule', '海拉鲁', '全明星', '无双',
    'kingdom', '两位君主', 'two crowns', '王國',
    'tomb', '古墓', 'remastered', '重製版',
    'symphonia', '仙乐', '交響曲', 'tales of',
    'graces', '美德', '圣恩', '聖恩',
    'overcooked', '煮過頭', '胡鬧廚房', '胡闹厨房',
    'darksiders', '末世騎士', '暗黑血統', '暗黑血统',
    'lets go', '去吧', '皮卡丘', '伊布', 'let\'s go',
    'skul', '小骨', '英雄殺手', '英雄杀手',
    'gta', 'grand theft', '三部曲', '終極版', '终极版',
    'stardew', '星露', '空洞', 'hollow',
    'celeste', '蔚藍', '蔚蓝',
    'animal well', '動物井', '动物井',
    'salt', '鹽與', '盐与',
    'bioshock', '生化奇兵',
    'crysis', '末日之戰', '孤島危機', '孤岛危机',
    'divinity', '神諭', '神界', '原罪',
    'naruto', '火影', '終極風暴', '究极风暴',
    'steamworld', '蒸氣世界', '蒸汽世界', 'gilgamech', '吉爾伽美什',
    'ori', '聖靈之光', '奥日', '奧日',
    'captain toad', '奇諾比奧', '奇诺比奥',
    'house of the dead', '死亡之屋',
    'castle crashers', '城堡破壞者', '城堡破坏者',
    'marvel ultimate', '漫威終極聯盟', '漫威终极联盟',
    'grid', '房車賽', '房车赛', 'autosport',
    'ruined king', '破敗王者', '破败王者', '英雄聯盟傳奇',
    'persona 5', '女神異聞錄5', '魅影攻手', '幽灵先锋',
    'bravely', '勇氣默示錄', '勇气默示录',
    'dragon ball heroes', '超七龍珠', '超龙珠', '世界任務',
    'kof', '拳皇', '94-03',
    'doom', '毀滅戰士', '毁灭战士',
    'metal slug', '合金彈頭', '合金弹头',
    'world war z', '殭屍世界大戰', '僵尸世界大战',
    'mercenaries', '傭兵傳說', '佣兵传说', '編年史', '编年史',
    'nightmare', '噩夢', '噩梦', '騎士',
    'amalur', '阿瑪拉', '阿玛拉', 'reckoning',
    'somnium', '夢境檔案', '梦境档案', 'nirvana', '涅槃',
    'black future', '黑色未來', '黑色未来',
    'fog', '霧隱', '雾隐',
    'max', '麥克斯', '兄弟魔咒',
    'dead rising', '勇闖死人谷', '勇闯死人谷',
    'fumamuxingzhe', '伏魔行者',
    'mirror', '魔鏡', '魔镜',
    'achilles', '阿喀琉斯',
    'dicefolk', '魔骰', '神骰',
    'six star', '六星', 'stargazer', '觀星者',
    'splintered', '史林特', '斯普林特', '命運',
    'scarlet', '緋紅', '绯红',
    'cadence', '節奏海拉魯', '节奏海拉鲁', '凱登絲',
    'unravel', '毛線小精靈', '毛线小精灵',
    'aclockwork', '發條', '发条', 'conspiracy',
    'erebonian', '埃雷波尼亞', '埃雷波尼亚',
    'legends untold', '傳說未竟', '传说未竟',
    'last remnant', '最後的神蹟', '最后的神迹',
    'romancing', '復活邪神', '复活邪神',
    'origami', '摺紙', '折纸',
    'legacy', '遺產', '遗产',
    'ninja gaiden', '忍者龍劍傳', '忍者龙剑传',
    'super mario', '超級瑪利歐', '超级马里奥',
    'zelda musou', '薩爾達無雙', '塞尔达无双',
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
        for e in hits[:6]:
            print(f'  {e["name"]}  ({e["tid"]})')
        print()
