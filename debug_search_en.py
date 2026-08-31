# -*- coding: utf-8 -*-
"""在TitleDB中搜索英文关键词，确认港区是否有这些游戏（可能只有英文名）"""
import json, os, sys
from gen_ns_data import normalize

BASE = os.path.dirname(os.path.abspath(__file__))
TITLEDB = os.path.join(BASE, 'data', 'HK.zh.json')

with open(TITLEDB, encoding='utf-8') as f:
    data = json.load(f)

keywords = sys.argv[1:] if len(sys.argv) > 1 else [
    'celeste', 'hollow knight', 'stardew', 'animal well', 'bioshock', 'crysis',
    'tomb raider', 'grid autosport', 'moving out', 'inscryption', 'castle crashers',
    'company of heroes', 'world war z', 'divinity', 'into the dead', 'kingdom two crowns',
    'house of the dead', 'rune factory', 'ori and the blind', 'star ocean',
    'tales of symphonia', 'tales of graces', 'king of fighters', 'ravenswatch',
    'max curse', "dragon's dogma", 'fighterz', 'doom 3', 'kof', 'balatro',
    'slay the spire', 'dead cells', 'hades', 'cuphead', 'celeste', 'undertale',
    'shovel knight', 'katana zero', 'dead cells', 'grime', 'blasphemous',
    'salt and sanctuary', 'skul', 'wargroove', 'kage', 'contra', 'metal slug',
    'overcooked', 'little nightmares', 'ori', 'nier', 'fenyx', 'assassin',
    'batman', 'alien', 'prince of persia', 'marvel', 'saints row', 'red dead',
    'diablo', 'witcher', 'skyrim', 'kingdom come', 'doom', 'doom eternal',
    'elden ring', 'dark souls', 'sekiro', 'bloodborne', 'resident evil',
    'monster hunter', 'final fantasy', 'dragon quest', 'persona', 'shin megami',
    'xenoblade', 'splatoon', 'pokemon', 'zelda', 'mario', 'kirby', 'metroid',
]

for kw in keywords:
    kw_norm = normalize(kw)
    print(f'\n===== 关键词: {kw} =====')
    hits = []
    for nsuid, info in data.items():
        name = info.get('name', '')
        if not isinstance(name, str):
            continue
        norm = normalize(name)
        if kw_norm and (kw_norm in norm or norm in kw_norm):
            hits.append((name, info.get('id')))
        elif kw.lower() in name.lower():
            hits.append((name, info.get('id')))
    if hits:
        for name, tid in hits[:10]:
            print(f'  {name}  ({tid})')
    else:
        print('  无匹配')
