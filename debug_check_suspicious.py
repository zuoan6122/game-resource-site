# -*- coding: utf-8 -*-
"""全面检查匹配质量：找出港区名与游戏名差异大的可疑匹配"""
import json, os
from gen_ns_data import clean_title, match_title, load_titledb, normalize

BASE = os.path.dirname(os.path.abspath(__file__))
TITLEDB = os.path.join(BASE, 'data', 'HK.zh.json')
DATA = os.path.join(BASE, 'data', 'games.json')

with open(DATA, encoding='utf-8') as f:
    games = json.load(f)
ns = [g for g in games if g.get('platform') == 'ns' and 'coverImage' in g]
entries = load_titledb(TITLEDB)
norm_map = {}
for e in entries:
    norm_map.setdefault(e['norm'], []).append(e)

# 检查：港区名与查询名没有共同中文/数字的（疑似误匹配）
suspicious = []
for g in ns:
    cleaned = clean_title(g['title'])
    mtype, e = match_title(cleaned, norm_map, entries)
    if not e:
        continue
    # 提取共同子串长度
    q = normalize(cleaned)
    en = e['norm']
    # 找最长公共子串
    def lcs(a, b):
        m, n = len(a), len(b)
        dp = [[0]*(n+1) for _ in range(m+1)]
        best = 0
        for i in range(1, m+1):
            for j in range(1, n+1):
                if a[i-1] == b[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                    if dp[i][j] > best:
                        best = dp[i][j]
        return best
    common = lcs(q, en)
    # 如果共同子串很短且港区名与查询名差异大，标记可疑
    if common < 4 and mtype == 'substr':
        suspicious.append((g['title'], e['name'], common))

print(f'共匹配 {len(ns)} 个，可疑 {len(suspicious)} 个')
for t, n, c in suspicious:
    print(f'  {t[:40]:<42} -> {n[:50]}  [共同子串: {c}]')
