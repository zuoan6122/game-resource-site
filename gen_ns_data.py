# -*- coding: utf-8 -*-
"""NS游戏数据补齐 - 小批量试跑：标题清洗 + TitleDB匹配"""
import json, os, re, sys
import opencc
from translation_map import apply_translation

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, 'data', 'games.json')
TITLEDB = os.path.join(BASE, 'data', 'HK.zh.json')

cc = opencc.OpenCC('t2s')  # 繁体转简体

# 常见版本后缀，匹配时去掉（按长度降序，避免"威力加强版"先被"加强版"截断）
SUFFIXES = sorted([
    '豪华限定版', '威力加强版', '周年纪念版', '豪华版', '重制版', '重置版', '复刻版', '完整版',
    '黄金版', '携带版', '特别版', '年度版', '终极版', '决定版', '加强版', '高清版',
    '合集版', '限定版', '标准版', '皇家版', '白金版', '典藏版', '收藏版', '周年版',
    '重聚', '重生', '豪华', '合集', '重制', '全集', 'DX', 'HD', 'dx', 'hd',
    'remastered', 'remake', 'definitive', 'ultimate', 'complete', 'anniversary',
    'collection', 'edition', 'hd remaster',
], key=len, reverse=True)

# 罗马数字 → 阿拉伯数字（仅独立 token，避免误伤英文单词）
def _int_to_roman(n):
    val = [(1000, 'm'), (900, 'cm'), (500, 'd'), (400, 'cd'), (100, 'c'), (90, 'xc'),
           (50, 'l'), (40, 'xl'), (10, 'x'), (9, 'ix'), (5, 'v'), (4, 'iv'), (1, 'i')]
    res = ''
    for v, s in val:
        while n >= v:
            res += s
            n -= v
    return res

_ROMAN = {_int_to_roman(i): i for i in range(1, 40)}
_ROMAN_RE = re.compile(
    r'(?<![a-z])(?:' + '|'.join(sorted(_ROMAN, key=len, reverse=True)) + r')(?![a-z])'
)
# 全角罗马数字 Ⅰ-Ⅹ (U+2160-2169) / ⅰ-ⅹ (U+2170-2179)
_FULLWIDTH_ROMAN = {}
for _i, _c in enumerate(range(0x2160, 0x216A)):
    _FULLWIDTH_ROMAN[chr(_c)] = str(_i + 1)
for _i, _c in enumerate(range(0x2170, 0x217A)):
    _FULLWIDTH_ROMAN[chr(_c)] = str(_i + 1)
# 汉字数字 → 阿拉伯数字
_CHINESE_NUM = {'一': '1', '二': '2', '三': '3', '四': '4', '五': '5',
                '六': '6', '七': '7', '八': '8', '九': '9',
                '壹': '1', '贰': '2', '叁': '3', '肆': '4', '伍': '5',
                '陆': '6', '柒': '7', '捌': '8', '玖': '9',
                '參': '3', '参': '3'}


def clean_title(t):
    """清洗标题：去掉+后缀、末尾（中文）括号、前导编号"""
    t = t.split('+')[0]
    t = re.sub(r'^\d+[.,、\s]*', '', t)
    t = re.sub(r'[（(][^）)]*[）)]$', '', t).strip()
    return t


def normalize(s):
    """标准化：转简体、全角转半角、数字统一、译名统一、去符号空格、小写"""
    s = cc.convert(s)
    s = s.lower()
    # 全角 ASCII 转半角
    s = ''.join(chr(ord(c) - 0xFEE0) if 0xFF01 <= ord(c) <= 0xFF5E else c for c in s)
    # 全角罗马数字 → 阿拉伯
    s = ''.join(_FULLWIDTH_ROMAN.get(c, c) for c in s)
    # 独立罗马数字 token → 阿拉伯（在去空格前，保证 token 边界可识别）
    s = _ROMAN_RE.sub(lambda m: str(_ROMAN[m.group(0)]), s)
    # 第一轮译名替换（去符号前）：只处理含英文字母的 key（如 "mario maker"），
    # 避免中文短 key 抢先替换破坏中文长 key（如"怪物猎人"破坏"怪物猎人崛起"）
    s = apply_translation(s, english_only=True)
    s = re.sub(r'[™®©★☆♪♬™]', '', s)
    s = re.sub(r'[\s:：·\-—_/\\()（）\[\]【】.。、,，!！?？\'"“”~～]', '', s)
    # 第二轮译名替换（去符号后）：处理全部 key（含被标点/空格隔开的中文 key）
    s = apply_translation(s)
    # 汉字数字 → 阿拉伯
    s = ''.join(_CHINESE_NUM.get(c, c) for c in s)
    return s


def match_title(cleaned, norm_map, entries):
    """返回 (匹配类型, 条目) 或 (None, None)"""
    norm = normalize(cleaned)
    if norm in norm_map:
        return 'exact', norm_map[norm][0]
    # 去掉版本后缀，生成多个候选 base（如"orochi3豪华版"→"orochi3"）
    bases = [norm]
    for suf in SUFFIXES:
        if norm.endswith(suf):
            bases.append(norm[: -len(suf)])
    for base in bases:
        if base in norm_map:
            return 'suffix', norm_map[base][0]
    # 子串匹配（全量扫描，含去后缀 base）
    for base in bases:
        if len(base) < 2:
            continue
        for e in entries:
            if e['norm'] == base:
                continue
            if base in e['norm']:
                # 港区名 = 查询名 + 纯数字时跳过（如"真人快打1"匹配"真人快打11"）
                if re.fullmatch(re.escape(base) + r'\d+', e['norm']):
                    continue
                # 查询名较短且不是港区名前缀时跳过（如"哈迪斯"匹配"…哈迪斯的戀愛冒險"）
                if len(base) < 5 and not e['norm'].startswith(base):
                    continue
                return 'substr', e
            # 港区名是查询名的子串时，要求港区名至少3字且与查询名长度比>=0.4
            # 避免"hunt"匹配"monsterhunter物语"这类短词误伤
            if (len(e['norm']) >= 3 and e['norm'] in base
                    and len(e['norm']) / len(base) >= 0.4):
                return 'substr', e
    return None, None


def load_titledb(path):
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    entries = []
    for nsuid, info in data.items():
        tid = info.get('id')
        name = info.get('name')
        if tid and name:
            entries.append({'tid': tid, 'name': name, 'norm': normalize(name)})
    return entries


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 15
    with open(DATA, encoding='utf-8') as f:
        games = json.load(f)
    ns_games = [g for g in games if g.get('platform') == 'ns']

    print('加载 TitleDB...')
    entries = load_titledb(TITLEDB)
    norm_map = {}
    for e in entries:
        norm_map.setdefault(e['norm'], []).append(e)
    print(f'TitleDB 条目: {len(entries)}')

    print(f'\n=== 测试前 {n} 个 NS 游戏 ===')
    exact = suffix = substr = fail = 0
    for g in ns_games[:n]:
        raw = g['title']
        cleaned = clean_title(raw)
        mtype, e = match_title(cleaned, norm_map, entries)
        if mtype == 'exact':
            print(f'[精确] {raw}')
            print(f'        -> {e["name"]} ({e["tid"]})')
            exact += 1
        elif mtype == 'suffix':
            print(f'[去后缀] {raw}')
            print(f'        -> {e["name"]} ({e["tid"]})')
            suffix += 1
        elif mtype == 'substr':
            print(f'[子串] {raw}')
            print(f'        -> {e["name"]} ({e["tid"]})')
            substr += 1
        else:
            print(f'[未匹配] {raw} (清洗后: {cleaned})')
            fail += 1
    total = exact + suffix + substr + fail
    print(f'\n=== 结果: 精确{exact} 去后缀{suffix} 子串{substr} 未匹配{fail} / {total} ===')
    print(f'总匹配率: {(exact+suffix+substr)/total*100:.0f}%')


if __name__ == '__main__':
    main()
