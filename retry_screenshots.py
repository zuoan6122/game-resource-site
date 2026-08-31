"""重试56个超时未更新的PC游戏截图"""
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
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode('utf-8', errors='ignore'))

def extract_appid(screenshots_str):
    m = re.search(r'/apps/(\d+)/', screenshots_str)
    return m.group(1) if m else None

def main():
    json_path = 'data/games.json'
    with open(json_path, 'r', encoding='utf-8') as f:
        games = json.load(f)

    pc_games = [(i, g) for i, g in enumerate(games)
                if g.get('platform') == 'pc' and g.get('screenshots')
                and len(g['screenshots'].split(',')) < 5]
    print('PC games needing retry:', len(pc_games), flush=True)

    success = 0
    fail = 0

    for idx, (i, game) in enumerate(pc_games):
        title = game['title']
        appid = extract_appid(game['screenshots'])
        if not appid:
            fail += 1
            continue

        print('[' + str(idx+1) + '/' + str(len(pc_games)) + '] ' + title + ' (appid:' + appid + ')', flush=True)

        url = STEAM_DETAIL_URL.format(appid)
        for attempt in range(3):
            try:
                data = fetch_json(url)
                app_data = data.get(str(appid), {})
                if not app_data.get('success'):
                    print('  -> API failure', flush=True)
                    break
                details = app_data.get('data', {})
                screenshots = details.get('screenshots', [])
                if screenshots:
                    ss_urls = [ss.get('path_full', '') for ss in screenshots[:5] if ss.get('path_full')]
                    if ss_urls:
                        games[i]['screenshots'] = ','.join(ss_urls)
                        print('  -> Updated to ' + str(len(ss_urls)) + ' screenshots', flush=True)
                        success += 1
                        break
                break
            except Exception as e:
                print('  -> Attempt ' + str(attempt+1) + ' error: ' + str(e), flush=True)
                time.sleep(2)
        else:
            fail += 1
            continue

        if not screenshots:
            fail += 1

        if (idx + 1) % 10 == 0:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(games, f, ensure_ascii=False, indent=4)
            print('  [Saved at ' + str(idx+1) + ']', flush=True)

        time.sleep(1.5)

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(games, f, ensure_ascii=False, indent=4)

    print('\nDone! Success: ' + str(success) + ', Failed: ' + str(fail), flush=True)

if __name__ == '__main__':
    main()
