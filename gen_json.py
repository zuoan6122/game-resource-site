import openpyxl
import json

files_info = [
    {
        'path': r'c:\Users\73974\.trae-cn\attachments\6a9167779f968d5062a924c7\99fbefb3-b78b-4cab-a5a2-c24abf3e9bff_69aed267-f229-4878-8a4c-c04f01ebc5f6_安卓及PC移植合集（一）.xlsx',
        'title_col': 2,
        'cat_col': 1,
        'url_col': 4,
        'img_col': 3,
    },
    {
        'path': r'c:\Users\73974\.trae-cn\attachments\6a9167779f968d5062a924c7\deff19a7-ee97-4c5d-9b7b-7434719303cf_3c185d53-13b3-4391-96d4-3580d6bdbc2a_安卓及PC移植合集（二）.xlsx',
        'title_col': 2,
        'cat_col': 1,
        'url_col': 4,
        'img_col': 3,
    },
    {
        'path': r'c:\Users\73974\.trae-cn\attachments\6a9167779f968d5062a924c7\ee4e0e3d-8c79-40f7-ac02-f0aa3429f345_6706bb86-1d48-4ff0-9e80-b4463116b185_安卓手机游戏合集.xlsx',
        'title_col': 2,
        'cat_col': 1,
        'url_col': 3,
        'img_col': None,
    },
]

cat_map = {
    '策略': 'strategy',
    '动作': 'action',
    '冒险': 'adventure',
    '角色扮演': 'rpg',
    '模拟': 'simulation',
    '竞速': 'racing',
    '街机': 'arcade',
    '射击': 'shooter',
    '卡牌': 'card',
    '体育': 'sports',
    '音乐': 'music',
    '解谜': 'puzzle',
    '生存': 'survival',
    '格斗': 'fighting',
}

all_games = []

for fi in files_info:
    wb = openpyxl.load_workbook(fi['path'], read_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    
    for row in rows[1:]:
        title = row[fi['title_col']]
        cat_cn = row[fi['cat_col']]
        url = row[fi['url_col']]
        
        if not title or not url or not cat_cn:
            continue
        
        title = str(title).strip()
        url = str(url).strip()
        cat_cn = str(cat_cn).strip()
        
        if not url.startswith('http'):
            continue
        
        cat_en = cat_map.get(cat_cn, 'other')
        
        game = {
            'title': title,
            'category': cat_en,
            'downloadUrl': url,
            'platform': 'android',
        }
        
        if fi['img_col'] is not None and row[fi['img_col']]:
            img = str(row[fi['img_col']]).strip()
            if img.startswith('http'):
                game['coverImage'] = img
        
        all_games.append(game)
    
    wb.close()

# Group by category
by_cat = {}
for g in all_games:
    by_cat.setdefault(g['category'], []).append(g)

print(f"Total games collected: {len(all_games)}")
print(f"Categories: {[(c, len(v)) for c, v in by_cat.items()]}")

# Write all games
output_path = r'E:\deepseek\game-resource-site\data\games.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(all_games, f, ensure_ascii=False, indent=4)

cats = {}
for g in all_games:
    cats[g['category']] = cats.get(g['category'], 0) + 1
print(f"Total games: {len(all_games)}")
print(f"Category distribution: {cats}")
print(f"Wrote {len(all_games)} games to {output_path}")
