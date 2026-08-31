"""从已有截图URL提取appid，直接获取5张截图"""
import json
import re
import time
import urllib.request

STEAM_DETAIL_URL = "https://store.steampowered.com/api/appdetails?appids={}&l=schinese"

def fetch_json(url):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'application/json'
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode('utf-8', errors='ignore'))

def extract_appid(screenshots_str):
    """从截图URL中提取appid"""
    m = re.search(r'/apps/(\d+)/', screenshots_str)
    if m:
        return m.group(1)
    return None

def main():
    json_path = 'data/games.json'
    with open(json_path, 'r', encoding='utf-8') as f:
        games = json.load(f)

    # 找出有截图但不到5张的PC游戏
    pc_games = [(i, g) for i, g in enumerate(games)
                if g.get('platform') == 'pc' and g.get('screenshots')
                and len(g['screenshots'].split(',')) < 5]
    print('PC games needing update:', len(pc_games), flush=True)

    success = 0
    fail = 0

    for idx, (i, game) in enumerate(pc_games):
        title = game['title']
        current_shots = game['screenshots'].split(',')

        appid = extract_appid(game['screenshots'])
        if not appid:
            print('[' + str(idx+1) + '/' + str(len(pc_games)) + '] ' + title + ' -> No appid found', flush=True)
            fail += 1
            continue

        print('[' + str(idx+1) + '/' + str(len(pc_games)) + '] ' + title + ' (appid:' + appid + ')', flush=True)

        url = STEAM_DETAIL_URL.format(appid)
        try:
            data = fetch_json(url)
            app_data = data.get(str(appid), {})
            if not app_data.get('success'):
                print('  -> API returned failure', flush=True)
                fail += 1
                time.sleep(1)
                continue
            details = app_data.get('data', {})
            screenshots = details.get('screenshots', [])
            if screenshots:
                ss_urls = [ss.get('path_full', '') for ss in screenshots[:5] if ss.get('path_full')]
                if ss_urls:
                    games[i]['screenshots'] = ','.join(ss_urls)
                    print('  -> Updated to ' + str(len(ss_urls)) + ' screenshots', flush=True)
                    success += 1
                else:
                    print('  -> No screenshot URLs', flush=True)
                    fail += 1
            else:
                print('  -> No screenshots in API', flush=True)
                fail += 1
        except Exception as e:
            print('  -> Error: ' + str(e), flush=True)
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
