"""更新PC游戏截图从2张到5张"""
import json
import time
import sys
sys.path.insert(0, '.')
from fetch_steam_data import search_steam_appid, get_app_details, fetch_json

STEAM_DETAIL_URL = "https://store.steampowered.com/api/appdetails?appids={}&l=schinese"

def main():
    json_path = 'data/games.json'
    with open(json_path, 'r', encoding='utf-8') as f:
        games = json.load(f)

    pc_games = [(i, g) for i, g in enumerate(games)
                if g.get('platform') == 'pc' and g.get('screenshots')]
    print('PC games with screenshots:', len(pc_games), flush=True)

    success = 0
    fail = 0

    for idx, (i, game) in enumerate(pc_games):
        title = game['title']
        current_shots = game['screenshots'].split(',')
        if len(current_shots) >= 5:
            success += 1
            continue

        print('[' + str(idx+1) + '/' + str(len(pc_games)) + '] ' + title, flush=True)

        appid = search_steam_appid(title)
        if not appid:
            print('  -> Not found', flush=True)
            fail += 1
            time.sleep(1)
            continue

        url = STEAM_DETAIL_URL.format(appid)
        try:
            data = fetch_json(url)
            app_data = data.get(str(appid), {})
            if not app_data.get('success'):
                print('  -> API returned failure', flush=True)
                fail += 1
                time.sleep(1.5)
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
