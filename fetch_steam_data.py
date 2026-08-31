import json
import re
import time
import urllib.request
import urllib.parse

STEAM_SEARCH_URL = "https://store.steampowered.com/api/storesearch/?term={}&l=schinese&cc=CN"
STEAM_DETAIL_URL = "https://store.steampowered.com/api/appdetails?appids={}&l=schinese"
STEAM_REVIEWS_URL = "https://store.steampowered.com/appreviews/{}?json=1&language=schinese&num_per_page=0"

# Exact title -> search term mapping for known games
TITLE_EXACT_MAP = {
    '罪域征途': '罪域征途',
    '职业篮球经理 2026': 'Pro Basketball Manager 2026',
    '中土世界 战争之影': 'Middle-earth Shadow of War',
    '致命解药': 'The Killing Antidote',
    '致命公司': 'Lethal Company',
    '战魂铭人': '战魂铭人',
    '征服黑暗': 'Conquest Dark',
    '正当防卫4': 'Just Cause 4',
    '正当防卫4重装版': 'Just Cause 4 Reloaded',
    '云之国': 'Cloudheim',
    '盐与避难所': 'Salt and Sanctuary',
    '盐和避难所': 'Salt and Sanctuary',
    '英雄围城': 'Hero Siege',
    '幽灵行者': 'Ghostrunner',
    '英灵神殿': 'Valheim',
    '信长之野望16 新生': 'Nobunagas Ambition Awakening',
    '信长之野望･新生': 'Nobunagas Ambition Awakening',
    '新月沃土': 'The Fertile Crescent',
    '吸血鬼：避世之血族2': 'Vampire The Masquerade Bloodlines 2',
    '吸血鬼：避世血族2': 'Vampire The Masquerade Bloodlines 2',
    '向死而生': 'We Who Are About To Die',
    '宣誓': 'Avowed',
    '心灵杀手2': 'Alan Wake 2',
    '星际勇士': 'Star Valor',
    '小骨杀手': 'Skul The Hero Slayer',
    '小骨：英雄杀手': 'Skul The Hero Slayer',
    '瘟疫公司：物竞天择': 'Plague Inc Evolved',
    '无双大蛇3终极版': 'Warriors Orochi 4',
    '往日不再': 'Days Gone',
    '卧龙苍天陨落': 'Wo Long Fallen Dynasty',
    '卧龙：苍天陨落': 'Wo Long Fallen Dynasty',
    '王国之心3': 'Kingdom Hearts III',
    '无感染区': 'Infection Free Zone',
    '泰坦之旅2': 'Titan Quest II',
    '泰坦陨落2': 'Titanfall 2',
    '特里修斯之门': 'The Doors of Trithius',
    '逃离塔科夫': 'Escape from Tarkov',
    '天国拯救2': 'Kingdom Come Deliverance II',
    '天国：拯救2': 'Kingdom Come Deliverance II',
    '天国拯救': 'Kingdom Come Deliverance',
    '天国：拯救': 'Kingdom Come Deliverance',
    '神之亵渎': 'Blasphemous',
    '神之天平': 'ASTLIBRA Revision',
    '石油大亨': 'Turmoil',
    '石油骚动': 'Turmoil',
    '嗜血印': 'Bloody Spell',
    '噬血代码': 'CODE VEIN',
    '嗜血代码': 'CODE VEIN',
    '三位一体4': 'Trine 4',
    '三位一体5': 'Trine 5',
    '死亡细胞': 'Dead Cells',
    '死神必须死': 'Death Must Die',
    '杀手5': 'Hitman Absolution',
    '杀手5：赦免': 'Hitman Absolution',
    '森林之子': 'Sons Of The Forest',
    '杀戮空间3': 'Killing Floor 3',
    '杀戮空间2': 'Killing Floor 2',
    '杀戮尖塔2': 'Slay the Spire 2',
    '神话时代：重述版': 'Age of Mythology Retold',
    '死或生6': 'Dead or Alive 6',
    '收获日2': 'Payday 2',
    '上古卷轴IV：湮灭重制版': 'The Elder Scrolls IV Oblivion',
    '上古卷轴 5：天际': 'The Elder Scrolls V Skyrim',
    '上古卷轴5：天际': 'The Elder Scrolls V Skyrim',
    '师父': 'Sifu',
    '师父Sifu': 'Sifu',
    '忍者神龟 施莱德的复仇': 'Teenage Mutant Ninja Turtles Shredders Revenge',
    '忍者神龟：施莱德的复仇': 'Teenage Mutant Ninja Turtles Shredders Revenge',
    '忍者龙剑传4': 'NINJA GAIDEN 4',
    '人渣': 'SCUM',
    '人渣(SCUM)': 'SCUM',
    '热血无赖': 'Sleeping Dogs',
    '人头落地': 'Heads Will Roll Reforged',
    '人头落地 重铸版': 'Heads Will Roll Reforged',
    '人狼村之谜': 'Raging Loop',
    '全网公敌': 'Cyber Manhunt',
    '奇迹时代4': 'Age of Wonders 4',
    '枪火重生': '枪火重生',
    '浅红2': 'Easy Red 2',
    '匹诺曹的谎言': 'Lies of P',
    '脑叶公司': 'Lobotomy Corporation',
    '虐杀原形': 'Prototype',
    '模拟山羊3': 'Goat Simulator 3',
    '模拟农场25': 'Farming Simulator 25',
    '漫漫长夜': 'The Long Dark',
    '龙之信条 黑暗觉醒': 'Dragons Dogma Dark Arisen',
    '龙之信条：黑暗觉醒': 'Dragons Dogma Dark Arisen',
    '流放者柯南': 'Conan Exiles',
    '狂野之心': 'Wild Hearts',
    '空洞骑士：丝之歌': 'Hollow Knight Silksong',
    '空洞骑士': 'Hollow Knight',
    '僵尸世界大战：劫后余生': 'World War Z Aftermath',
    '极速骑行4': 'RIDE 4',
    '僵尸毁灭工程': 'Project Zomboid',
    '加拿大死亡之路': 'Death Road to Canada',
    '加雷利亚的地下迷宫与魔女的旅团': '加雷利亚的地下迷宫',
    '极乐迪斯科': 'Disco Elysium',
    '极乐迪斯科 最终剪辑版': 'Disco Elysium The Final Cut',
    '绝地潜兵': 'HELLDIVERS',
    '绝对魔权': '绝对魔权',
    '毁灭战士：黑暗时代': 'DOOM The Dark Ages',
    '毁灭战士 永恒': 'DOOM Eternal',
    '毁灭战士：永恒': 'DOOM Eternal',
    '合金装备 食蛇者': 'Snake Eater',
    '合金装备Δ：食蛇者': 'Snake Eater',
    '红警合集': 'Command Conquer',
    '黑道圣徒3': 'Saints Row The Third',
    '哈迪斯': 'Hades',
    '哈迪斯 地狱之战': 'Hades Battle Out of Hell',
    '荒岛求生': '荒岛求生',
    'GTA5': 'Grand Theft Auto V',
    '侠盗猎车手5': 'Grand Theft Auto V',
    '孤胆枪手': 'Alien Shooter',
    '方舟 生存进化': 'ARK Survival Evolved',
    '方舟：生存进化': 'ARK Survival Evolved',
    '辐射4': 'Fallout 4',
    '腐烂国度2': 'State of Decay 2',
    '腐烂国度': 'State of Decay',
    '腐烂国度1': 'State of Decay',
    '风暴崛起': 'Tempest Rising',
    'Fate 武士遗迹': 'Fate Samurai Remnant',
    'Fate/武士遗迹': 'Fate Samurai Remnant',
    '地狱之刃2：塞娜的献祭': 'Hellblade II',
    '地狱之刃2：塞娜的传说': 'Hellblade II',
    '地狱丧钟': 'Hell Clock',
    '地铁离去': 'Metro Exodus',
    '地铁：离去': 'Metro Exodus',
    '德洛瓦：被弃之族': 'Drova Forsaken Kin',
    '堆叠大陆': 'Stacklands',
    '沉没之地': 'Sunkenland',
    '茶杯头': 'Cuphead',
    '孢子': 'Spore',
    '冰汽时代': 'Frostpunk',
    '北欧女神 极乐世界': 'Valkyrie Elysium',
    '北欧女神：极乐世界': 'Valkyrie Elysium',
    '崩溃：核冬天': 'Crash Nuclear Winter',
    '北境之地': 'Northgard',
    '边境检查官': 'Border Officer',
    '奥日 森林': 'Ori and the Blind Forest',
    '奥日与黑暗森林': 'Ori and the Blind Forest',
    '奥日 萤火': 'Ori and the Will of the Wisps',
    '奥日与萤火意志': 'Ori and the Will of the Wisps',
    '暗黑地牢2': 'Darkest Dungeon II',
    '暗黑地牢': 'Darkest Dungeon',
    '七日杀': '7 Days to Die',
}

def clean_title(title):
    t = title
    t = re.sub(r'【.*?】', '', t)
    t = re.sub(r'\[.*?\]', '', t)
    t = re.sub(r'\(.*?\)', '', t)
    t = re.sub(r'v\d+[\.\d]*', '', t, flags=re.IGNORECASE)
    t = re.sub(r'版本.*$', '', t)
    t = re.sub(r'免广.*$', '', t)
    t = re.sub(r'破解.*$', '', t)
    t = re.sub(r'汉化.*$', '', t)
    t = re.sub(r'中文版.*$', '', t)
    t = re.sub(r'完整版.*$', '', t)
    t = re.sub(r'高清.*$', '', t)
    t = re.sub(r'重制.*$', '', t)
    t = re.sub(r'全dlc', '', t, flags=re.IGNORECASE)
    t = re.sub(r'dlc', '', t, flags=re.IGNORECASE)
    t = re.sub(r'——', ' ', t)
    t = re.sub(r'—', ' ', t)
    t = re.sub(r'apk', '', t, flags=re.IGNORECASE)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

def get_search_variants(title):
    clean = clean_title(title)
    variants = []

    # 1. Check exact map first（同时匹配原始标题，避免清洗后丢失关键词如"重制版"）
    for cn, en in sorted(TITLE_EXACT_MAP.items(), key=lambda x: -len(x[0])):
        if cn in title or cn in clean or title.startswith(cn) or clean.startswith(cn):
            variants.append(en)
            break

    # 2. Original cleaned
    variants.append(clean)

    # 3. Remove numbers
    no_nums = re.sub(r'\d+', '', clean).strip()
    if no_nums and len(no_nums) >= 2:
        variants.append(no_nums)

    # 4. Shorter versions
    if len(clean) > 10:
        variants.append(clean[:10])
    if len(clean) > 6:
        variants.append(clean[:6])

    # 5. Minimal
    minimal = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', '', clean)
    if len(minimal) >= 2:
        variants.append(minimal)

    # Deduplicate
    seen = set()
    result = []
    for v in variants:
        v = v.strip()
        if v and v not in seen and len(v) >= 2:
            seen.add(v)
            result.append(v)
    return result

def fetch_json(url):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'application/json'
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode('utf-8', errors='ignore'))

def search_steam_appid(title):
    variants = get_search_variants(title)

    for variant in variants:
        encoded = urllib.parse.quote(variant)
        url = STEAM_SEARCH_URL.format(encoded)
        try:
            data = fetch_json(url)
            items = data.get('items', [])
            if items:
                return items[0]['id']
        except:
            pass
        time.sleep(0.3)

    return None

def get_app_details(appid):
    url = STEAM_DETAIL_URL.format(appid)
    try:
        data = fetch_json(url)
        app_data = data.get(str(appid), {})
        if not app_data.get('success'):
            return None
        return app_data.get('data')
    except Exception as e:
        print('  Detail error:', e)
        return None

def get_app_reviews(appid):
    url = STEAM_REVIEWS_URL.format(appid)
    try:
        data = fetch_json(url)
        if data.get('success') != 1:
            return None
        return data.get('query_summary')
    except Exception as e:
        print('  Reviews error:', e)
        return None

def extract_fields(details, reviews):
    result = {}

    header = details.get('header_image', '')
    if header:
        result['coverImage'] = header

    screenshots = details.get('screenshots', [])
    if screenshots:
        ss_urls = [ss.get('path_full', '') for ss in screenshots[:5] if ss.get('path_full')]
        if ss_urls:
            result['screenshots'] = ','.join(ss_urls)

    release_info = details.get('release_date', {})
    if release_info.get('date'):
        result['releaseDate'] = release_info['date']

    desc = details.get('short_description', '')
    if not desc:
        desc = details.get('detailed_description', '')
    if desc:
        desc = re.sub(r'<[^>]+>', '', desc).strip()
        if len(desc) > 300:
            desc = desc[:300] + '...'
        result['description'] = desc

    if reviews:
        score = reviews.get('review_score')
        if score is not None:
            result['reviewScore'] = score
        score_desc = reviews.get('review_score_desc')
        if score_desc:
            result['reviewScoreDesc'] = score_desc

    return result

def main():
    json_path = 'data/games.json'

    with open(json_path, 'r', encoding='utf-8') as f:
        games = json.load(f)

    # Only process PC games missing coverImage
    pc_games = [(i, g) for i, g in enumerate(games) if g.get('platform') == 'pc' and not g.get('coverImage')]
    print('PC games to process:', len(pc_games), flush=True)

    success = 0
    fail = 0

    for idx, (i, game) in enumerate(pc_games):
        title = game['title']

        print('[' + str(idx+1) + '/' + str(len(pc_games)) + '] ' + title, flush=True)

        appid = search_steam_appid(title)
        if not appid:
            print('  -> Not found', flush=True)
            fail += 1
            time.sleep(1)
            continue

        print('  -> App ID: ' + str(appid), flush=True)

        details = get_app_details(appid)
        if not details:
            print('  -> Failed to get details', flush=True)
            fail += 1
            time.sleep(1)
            continue

        reviews = get_app_reviews(appid)

        fields = extract_fields(details, reviews)
        if fields:
            for k, v in fields.items():
                games[i][k] = v
            print('  -> OK: ' + ', '.join(fields.keys()), flush=True)
            success += 1
        else:
            print('  -> No data', flush=True)
            fail += 1

        if (idx + 1) % 20 == 0:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(games, f, ensure_ascii=False, indent=4)
            print('  [Saved at ' + str(idx+1) + ']', flush=True)

        time.sleep(1.5)

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(games, f, ensure_ascii=False, indent=4)

    print('\nDone! Success: ' + str(success) + ', Failed: ' + str(fail), flush=True)

if __name__ == '__main__':
    main()
