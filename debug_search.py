# -*- coding: utf-8 -*-
"""在TitleDB中搜索指定关键词，查看港区名称"""
import json, os, sys
from gen_ns_data import normalize

BASE = os.path.dirname(os.path.abspath(__file__))
TITLEDB = os.path.join(BASE, 'data', 'HK.zh.json')

with open(TITLEDB, encoding='utf-8') as f:
    data = json.load(f)

keywords = sys.argv[1:] if len(sys.argv) > 1 else ['织梦岛', '旷野之息', '空洞', '星露', '蔚蓝', 'Celeste', '文明', '歧路旅人', '八方旅人', '魔界战记', '暗黑破坏神', '无双大蛇', '真女神转生', '浪漫沙加', '轩辕剑', '太阁立志传', '拳皇', '鬼灭', '七龙珠', '龙珠', '毁灭战士', '生化奇兵', '孤岛危机', '符文工坊', '星之海洋', '圣剑传说', '仙乐传说', '圣恩传说', '皇家骑士团', '以撒', '小丑', '血污', '幽灵诡计', '弹丸论破', '死亡之屋', '王国', '城堡破坏者', '英雄连', '黑色未来', '魔骰', '伏魔行者', '勇闯死人谷', '六星之门', '阿喀琉斯', '雪人兄弟', '合金弹头', '僵尸世界大战', '神界', '火影忍者', '尼尔', '渡神纪', '上古卷轴', '天国', '终焉之玛格诺利亚', '破败王者', '古墓丽影', '蝙蝠侠', '异形', '波斯王子', '漫威', '超级房车赛', '魂斗罗', '胡闹厨房', '胡闹搬家', '小小梦魇', '奥日', '赤影战士', '战律', '鸦卫', '雾隐', '魔镜', '麦克斯', '邪恶铭刻', 'IGS', '圣塔战记', '噩梦骑士', '动物井']

for kw in keywords:
    kw_norm = normalize(kw)
    print(f'\n===== 关键词: {kw} (norm={kw_norm}) =====')
    hits = []
    for nsuid, info in data.items():
        name = info.get('name', '')
        if not isinstance(name, str):
            continue
        norm = normalize(name)
        if kw_norm and (kw_norm in norm or norm in kw_norm):
            hits.append((name, info.get('id'), norm))
        elif kw.lower() in name.lower():
            hits.append((name, info.get('id'), norm))
    if hits:
        for name, tid, norm in hits[:15]:
            print(f'  {name}  ({tid})  norm={norm}')
    else:
        print('  无匹配')
