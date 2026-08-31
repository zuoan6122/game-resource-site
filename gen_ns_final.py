# -*- coding: utf-8 -*-
"""生成最终NS游戏数据：把匹配到的港区数据（封面、截图、发行日期、简介）写入games.json"""
import json, os, re
from gen_ns_data import clean_title, match_title, load_titledb

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, 'data', 'games.json')
TITLEDB = os.path.join(BASE, 'data', 'HK.zh.json')

# 优先排除体验版/DLC/周边等非本体条目
BAD_KEYWORDS = ['體驗版', '体验版', 'DLC', 'dlc', '原聲帶', '原声带', '美術', '美术',
                '畫冊', '画册', '音樂包', '音乐包', '服裝', '服装', '組合包', '组合包',
                '套組', '套组', '包1', '包2', '包3', '包4', '包5', '包6', '包7', '包8',
                'Retail Only', 'Demo', 'demo', '試玩', '试玩', '數位', '数字']


def pick_entry(norm_map, norm):
    """从同norm的多个条目中挑选本体（排除体验版/DLC等）"""
    cands = norm_map.get(norm, [])
    if not cands:
        return None
    for e in cands:
        if not any(kw in e['name'] for kw in BAD_KEYWORDS):
            return e
    return cands[0]


def fmt_date(d):
    """20221013 -> 2022 年 10 月 13 日"""
    s = str(d)
    if len(s) == 8 and s.isdigit():
        return f'{s[0:4]} 年 {int(s[4:6])} 月 {int(s[6:8])} 日'
    return None


def main():
    with open(DATA, encoding='utf-8') as f:
        games = json.load(f)
    with open(TITLEDB, encoding='utf-8') as f:
        hk = json.load(f)

    entries = load_titledb(TITLEDB)
    norm_map = {}
    for e in entries:
        norm_map.setdefault(e['norm'], []).append(e)
    # 建立 tid -> 港区数据
    tid_map = {}
    for nsuid, info in hk.items():
        tid = info.get('id')
        if tid:
            tid_map[tid] = info

    updated = 0
    unmatched = []
    for g in games:
        if g.get('platform') != 'ns':
            continue
        # 先清除旧港区数据，保证与当前匹配结果一致
        for k in ('coverImage', 'screenshots', 'releaseDate', 'description'):
            g.pop(k, None)
        cleaned = clean_title(g['title'])
        mtype, e = match_title(cleaned, norm_map, entries)
        if not mtype:
            unmatched.append(g['title'])
            continue
        # 用 pick_entry 重新挑选本体条目
        e2 = pick_entry(norm_map, e['norm']) or e
        info = tid_map.get(e2['tid'])
        if not info:
            unmatched.append(g['title'])
            continue
        banner = info.get('bannerUrl')
        shots = info.get('screenshots') or []
        desc = (info.get('description') or '').strip()
        rdate = fmt_date(info.get('releaseDate'))
        if banner:
            g['coverImage'] = banner
        if shots:
            g['screenshots'] = ','.join(shots[:2])
        if rdate:
            g['releaseDate'] = rdate
        if desc:
            g['description'] = desc
        updated += 1

    with open(DATA, 'w', encoding='utf-8') as f:
        json.dump(games, f, ensure_ascii=False, indent=4)

    print(f'已更新NS游戏: {updated}')
    print(f'未匹配: {len(unmatched)}')
    print(f'games.json 总游戏数: {len(games)}')


if __name__ == '__main__':
    main()
