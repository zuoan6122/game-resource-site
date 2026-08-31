import json, re, time, urllib.request, urllib.parse

def clean_title(title):
    t = title
    t = re.sub(r'【.*?】', '', t)
    t = re.sub(r'v\d+[\.\d]*', '', t, flags=re.IGNORECASE)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

def fetch_json(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode('utf-8', errors='ignore'))

with open('data/games.json', 'r', encoding='utf-8') as f:
    games = json.load(f)

pc_games = [(i, g) for i, g in enumerate(games) if g.get('platform') == 'pc']
print('PC games:', len(pc_games))

for idx, (i, game) in enumerate(pc_games[:3]):
    title = game['title']
    clean = clean_title(title)
    print('[' + str(idx+1) + '] ' + title + ' -> search: ' + clean)
    encoded = urllib.parse.quote(clean)
    url = 'https://store.steampowered.com/api/storesearch/?term=' + encoded + '&l=schinese&cc=CN'
    try:
        data = fetch_json(url)
        items = data.get('items', [])
        if items:
            appid = items[0]['id']
            print('  AppID:', appid)
            detail_url = 'https://store.steampowered.com/api/appdetails?appids=' + str(appid) + '&l=schinese'
            details = fetch_json(detail_url)
            app_data = details.get(str(appid), {})
            if app_data.get('success'):
                d = app_data['data']
                print('  Name:', d.get('name', ''))
                print('  Header:', d.get('header_image', '')[:80])
                ss = d.get('screenshots', [])
                print('  Screenshots:', len(ss))
                print('  Release:', d.get('release_date', {}).get('date', ''))
                desc = d.get('short_description', '')
                print('  Desc:', desc[:80])
            else:
                print('  Detail failed')
        else:
            print('  Not found')
    except Exception as e:
        print('  Error:', e)
    time.sleep(1.5)
    print()
