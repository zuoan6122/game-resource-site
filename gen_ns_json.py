import openpyxl
import json

# Read existing games.json
with open(r'E:\deepseek\game-resource-site\data\games.json', 'r', encoding='utf-8') as f:
    existing = json.load(f)
print(f"Existing games: {len(existing)}")

# Read NS Excel
ns_file = r'c:\Users\73974\.trae-cn\attachments\6a9167779f968d5062a924c7\58832706-bee0-4e23-b92d-623c7e742629_872da4ae-93e6-42df-ab7b-82f60ff7543b_NS游戏合集（一）.xlsx'

cat_map = {
    '策略': 'strategy', '策略类': 'strategy',
    '动作': 'action', '动作类': 'action',
    '冒险': 'adventure', '冒险类': 'adventure',
    '角色扮演': 'rpg', '角色扮演类': 'rpg', 'RPG': 'rpg', 'RPG类': 'rpg',
    '模拟': 'simulation', '模拟类': 'simulation',
    '竞速': 'racing', '竞速类': 'racing',
    '街机': 'arcade', '街机类': 'arcade',
    '射击': 'shooter', '射击类': 'shooter',
    '卡牌': 'card', '卡牌类': 'card',
    '体育': 'sports', '体育类': 'sports',
    '音乐': 'music', '音乐类': 'music',
    '解谜': 'puzzle', '解谜类': 'puzzle',
    '生存': 'survival', '生存类': 'survival',
    '格斗': 'fighting', '格斗类': 'fighting',
}

wb = openpyxl.load_workbook(ns_file, read_only=True)
ws = wb.active
rows = list(ws.iter_rows(values_only=True))

ns_games = []
for row in rows[1:]:
    title = row[2]
    cat_cn = row[1]
    url = row[3]

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
        'platform': 'ns',
    }
    ns_games.append(game)

wb.close()

print(f"NS games collected: {len(ns_games)}")
cats = {}
for g in ns_games:
    cats[g['category']] = cats.get(g['category'], 0) + 1
print(f"NS category distribution: {cats}")
print(f"Sample: {ns_games[0]}")

# Append to existing
all_games = existing + ns_games
print(f"Total games now: {len(all_games)}")

# Write back
with open(r'E:\deepseek\game-resource-site\data\games.json', 'w', encoding='utf-8') as f:
    json.dump(all_games, f, ensure_ascii=False, indent=4)

print(f"Wrote {len(all_games)} games to games.json")
