# -*- coding: utf-8 -*-
"""快速测试 normalize 对关键标题的处理"""
from gen_ns_data import normalize, clean_title

tests = [
    ('塞尔达传说 织梦岛', '薩爾達傳說 織夢島'),
    ('塞尔达传说 旷野之息', '薩爾達傳說 曠野之息'),
    ('塞尔达传说 王国之泪', '薩爾達傳說 王國之淚'),
    ('塞尔达传说 天空之剑', '薩爾達傳說 禦天之劍 HD'),
    ('塞尔达传说 智慧的再现', '薩爾達傳說 智慧的再現'),
    ('文明6豪华版', '《文明帝國VI》'),
    ('暗黑破坏神3', '《暗黑破壞神 III》永恆典藏版'),
    ('暗黑破坏神2', '《暗黑破壞神®II：獄火重生™》'),
    ('八方旅人2', '歧路旅人II OCTOPATH TRAVELER II'),
    ('真女神转生5', '真・女神轉生Ⅴ'),
    ('真女神转生3', '真・女神轉生Ⅲ NOCTURNE HD REMASTER'),
    ('太阁立志传V DX', '太閤立志傳Ⅴ DX'),
    ('轩辕剑7', '軒轅劍柒'),
    ('轩辕剑3', '軒轅劒參 雲和山的彼端'),
    ('上古卷轴5：天际', '《The Elder Scrolls V: Skyrim》'),
    ('尼尔：机械纪元', 'NieR:Automata The End of YoRHa Edition'),
    ('渡神纪：芬尼斯崛起', '《芬尼克斯傳說》(Immortals Fenyx Rising)'),
    ('天国：拯救皇家版', 'Kingdom Come Deliverance: Royal Edition'),
    ('蝙蝠侠：阿卡姆骑士', 'Batman: Arkham Knight'),
    ('异形：隔离', 'Alien: Isolation'),
    ('波斯王子 失落的王冠', '《波斯王子：失落王冠》'),
    ('漫威终极联盟3', 'MARVEL ULTIMATE ALLIANCE 3: The Black Order'),
    ('魂斗罗 加鲁加行动', 'Contra: Operation Galuga'),
    ('魂斗罗 流氓军团', 'CONTRA: ROGUE CORPS'),
    ('魂斗罗周年经典合集', 'Contra Anniversary Collection'),
    ('胡闹厨房 全部好吃', 'Overcooked! All You Can Eat'),
    ('奥日2精灵与萤火意志', 'Ori and the Will of the Wisps'),
    ('鬼灭之刃 火神血风谭', '鬼滅之刃 火之神血風譚'),
    ('七龙珠Z 卡卡罗特', '七龍珠Z 卡卡洛特 + 新覺醒篇'),
    ('龙珠 超宇宙2', '七龍珠 異戰2 for Nintendo Switch'),
    ('血污：夜之仪式', '血咒之城：暗夜儀式'),
    ('皇家骑士团 重生', 'Tactics Ogre: Reborn'),
    ('以撒的结合 忏悔', 'The Binding of Isaac: Repentance'),
    ('幽灵诡计 幻影侦探', 'Ghost Trick: Phantom Detective'),
    ('弹丸论破V3', '新槍彈辯駁V3 大家的自相殘殺新學期 Anniversary Edition'),
    ('终焉之玛格诺利亚：雾中绽放', 'ENDER MAGNOLIA: Bloom in the Mist'),
    ('赤影战士：重生', 'KAGE～Shadow of The Ninja 絕影戰士'),
    ('战律1', '戰律 (Wargroove)'),
    ('雪人兄弟 仙境', 'Snow Bros. Wonderland'),
    ('合金弹头 攻击重装版', 'METAL SLUG ATTACK RELOADED'),
    ('IGS街机游戏合集', 'IGS Classic Arcade Collection'),
    ('胡闹搬家', 'Moving Out'),
    ('邪恶铭刻', 'Inscryption'),
    ('王国：两位君主', 'Kingdom Two Crowns'),
    ('符文工坊3', '符文工廠３豪華版'),
    ('星之海洋 第二个故事', 'STAR OCEAN THE SECOND STORY R'),
    ('拳皇13：全球对决', 'THE KING OF FIGHTERS XIII GLOBAL MATCH'),
    ('鸦卫奇旅', 'Ravenswatch'),
    ('龙之信条 黑暗再临', "Dragon's Dogma: Dark Arisen"),
    ('龙珠斗士Z', 'Dragonball FighterZ'),
    ('毁灭战士：永恒', 'DOOM® Eternal'),
    ('小丑牌', 'Balatro'),
    ('圣剑传说3重制版', 'Trials of Mana (中文版)'),
    ('魔界战记4重置版', '魔界戰記４Return'),
    ('英雄连合集', 'Company of Heroes Collection'),
    ('小小梦魇1', 'Little Nightmares Complete Edition'),
]

for q, hk in tests:
    qn = normalize(clean_title(q))
    hn = normalize(hk)
    match = '✓' if (qn in hn or hn in qn or qn == hn) else '✗'
    print(f'{match} {q}')
    print(f'    q: {qn}')
    print(f'    h: {hn}')
