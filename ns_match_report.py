# -*- coding: utf-8 -*-
"""NS游戏匹配分析报告：列出全部NS游戏的匹配状态和未匹配原因"""
import json, os, re
import opencc
from gen_ns_data import clean_title, normalize, match_title, load_titledb, SUFFIXES

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, 'data', 'games.json')
TITLEDB = os.path.join(BASE, 'data', 'HK.zh.json')

cc = opencc.OpenCC('t2s')


def find_similar(cleaned, entries):
    """在TitleDB中找与清洗后标题相似的条目（用于判断名称差异）"""
    norm = normalize(cleaned)
    # 找包含清洗标题中任意>=3字子串的条目
    results = []
    for e in entries:
        en = e['norm']
        # 双向子串或公共子串>=3
        if norm in en or en in norm:
            results.append(e)
            continue
        # 找最长公共子串
        common = longest_common_substring(norm, en)
        if len(common) >= 3:
            results.append((e, common))
    return results[:5]


def longest_common_substring(a, b):
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    best = 0
    end = 0
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
                if dp[i][j] > best:
                    best = dp[i][j]
                    end = i
    return a[end - best:end]


def main():
    with open(DATA, encoding='utf-8') as f:
        games = json.load(f)
    ns_games = [g for g in games if g.get('platform') == 'ns']
    entries = load_titledb(TITLEDB)
    norm_map = {}
    for e in entries:
        norm_map.setdefault(e['norm'], []).append(e)

    lines = []
    matched = []
    unmatched = []
    for g in ns_games:
        raw = g['title']
        cleaned = clean_title(raw)
        mtype, e = match_title(cleaned, norm_map, entries)
        if mtype:
            matched.append((raw, mtype, e))
        else:
            # 分析未匹配原因
            similar = find_similar(cleaned, entries)
            unmatched.append((raw, cleaned, similar))

    # 输出摘要
    print(f'NS游戏总数: {len(ns_games)}')
    print(f'匹配成功: {len(matched)} ({len(matched)/len(ns_games)*100:.0f}%)')
    print(f'未匹配: {len(unmatched)} ({len(unmatched)/len(ns_games)*100:.0f}%)')

    # 保存完整报告
    report_path = os.path.join(BASE, 'ns_match_report.txt')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f'NS游戏总数: {len(ns_games)}\n')
        f.write(f'匹配成功: {len(matched)} ({len(matched)/len(ns_games)*100:.0f}%)\n')
        f.write(f'未匹配: {len(unmatched)} ({len(unmatched)/len(ns_games)*100:.0f}%)\n\n')
        f.write('【未匹配的游戏及原因】\n')
        for raw, cleaned, similar in unmatched:
            f.write(f'{raw}\n')
            f.write(f'  清洗后: {cleaned}\n')
            if similar:
                for s in similar[:3]:
                    if isinstance(s, tuple):
                        e, common = s
                        f.write(f'  港区相似: {e["name"]} ({e["tid"]}) [共同: {common}]\n')
                    else:
                        f.write(f'  港区相似: {s["name"]} ({s["tid"]})\n')
            else:
                f.write(f'  港区无此游戏\n')
            f.write('\n')

    # 打印未匹配列表（带原因）
    print(f'\n=== 未匹配的游戏（{len(unmatched)}个）===')
    for raw, cleaned, similar in unmatched:
        if similar:
            e0 = similar[0]
            name0 = e0["name"] if not isinstance(e0, tuple) else e0[0]["name"]
            print(f'✗ {raw}  [港区有相似: {name0}]')
        else:
            print(f'✗ {raw}  [港区无此游戏]')
    print(f'\n完整报告已保存: {report_path}')


if __name__ == '__main__':
    main()
