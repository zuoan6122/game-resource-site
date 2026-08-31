# -*- coding: utf-8 -*-
"""搜索TitleDB港区数据，确认剩余不确定游戏的港区译名"""
import json, os
from gen_ns_data import normalize

BASE = os.path.dirname(os.path.abspath(__file__))
TITLEDB = os.path.join(BASE, 'data', 'HK.zh.json')

with open(TITLEDB, encoding='utf-8') as f:
    data = json.load(f)

keywords = [
    'ezio', '艾吉奥', '艾吉歐',
    'rebel', '叛逆者',
    'storm', '疾风传', '疾風傳', '风暴', '風暴', 'ultimate ninja',
    'splintered', '史林特', '斯普林特',
    'red dead', '荒野大镖客', '荒野大鏢客', '碧血狂殺',
    'dead or alive', '沙滩排球', '沙灘排球', '绯红', 'scarlet',
    'gta', 'grand theft', '三部曲',
    'saints row', '黑道圣徒', '黑道聖徒', '黑街聖徒', 're-elected', '连任',
    'cadence', '节奏海拉鲁', '節奏海拉魯', '死灵舞师', '死靈舞師',
    'witcher', '巫师', '巫師',
    'kof', '拳皇', '拳王',
    'metal slug', '合金弹头', '合金彈頭',
    'dragon dogma', '龙之信条', '龍之信條', 'dark arisen', '黑暗再临',
    'bioshock', '生化奇兵',
    'unravel', '毛线', '毛線',
    'steamworld', '蒸汽世界', '蒸汽世界',
    'crysis', '孤岛危机', '孤島危機', '末日之戰',
    'divinity', '神界', '原罪',
    'rune factory', '符文', '符文工房', '符文工廠',
    'trine', '三位一体', '三位一體',
    'somnium', '梦境档案', '夢境檔案',
    'lego harry', '乐高哈利', '樂高哈利',
    'cold steel', '闪之轨迹', '閃之軌跡',
    'daybreak', '黎之轨迹', '黎之軌跡',
    'zombie army', '僵尸部队', '殭屍部隊',
    'danganronpa', '弹丸论破', '彈丸論破', '槍彈辯駁',
    'world war z', '僵尸世界大战', '殭屍世界大戰',
    'snow bros', '雪人兄弟',
    'castle crashers', '城堡破坏者', '城堡破壞者',
    'last remnant', '最后的神迹', '最後的神蹟',
    'company of heroes', '英雄连', '英雄連',
    'civilization', '文明',
    'little nightmares', '小小梦魇', '小小夢魘',
    'ori', '奥日', '奧日',
    'captain toad', '奇诺比奥', '奇諾比奧',
    'lets go', '去吧', '皮卡丘', '伊布',
    'ghost trick', '幽灵诡计', '幽靈偵探', '幻影侦探',
    'romancing saga', '浪漫沙加', '復活邪神',
    'house of the dead', '死亡之屋',
    'kingdom two crowns', '两位君主', '兩位君主',
    'binding of isaac', '以撒', '忏悔', '懺悔',
    'balatro', '小丑牌',
    'darksiders', '暗黑血统', '暗黑血統',
    'super mario 3d', '3d全明星', '3D全明星',
    'new super mario', '新超级马里奥', '新超級瑪利歐',
    'paper mario', '纸片马里奥', '紙片瑪利歐', '折纸王国', '摺紙國王',
    'star ocean', '星之海洋', '第二个故事', '第二個故事',
    'mega man zero', '洛克人zero', 'zerozx', 'zero zx',
    'super dragon ball', '超龙珠', '超七龍珠', '英雄',
    'max curse', '麦克斯', '兄弟魔咒',
    'mirror', '魔镜', '魔鏡',
    'fog', '雾隐', '霧隱',
    'ravenswatch', '鸦卫', '鴉衛',
    'achilles', '阿喀琉斯',
    'metal slug attack', '攻击重装', '攻擊重裝',
    'dicefolk', '魔骰',
    'black future', '黑色未来', '黑色未來',
    'mercenaries', '佣兵', '傭兵', '编年史', '編年史',
    'six star', '六星', '星轨', '星軌',
    'dead rising', '勇闯死人谷', '勇闖死人谷',
    'fumamuxingzhe', '伏魔行者',
    'heroes', '英雄传说', '英雄傳說', '轨迹', '軌跡',
]

for kw in keywords:
    kw_norm = normalize(kw)
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
    print(f'===== {kw} =====')
    if hits:
        for name, tid in hits[:6]:
            print(f'  {name}  ({tid})')
    else:
        print('  无匹配')
    print()
