import json
import re

with open(r'E:\deepseek\game-resource-site\data\games.json', 'r', encoding='utf-8') as f:
    games = json.load(f)

fixed = 0
for g in games:
    if g['platform'] == 'ns':
        old_title = g['title']
        g['title'] = re.sub(r'^\d+\.\s*', '', old_title)
        if g['title'] != old_title:
            fixed += 1

with open(r'E:\deepseek\game-resource-site\data\games.json', 'w', encoding='utf-8') as f:
    json.dump(games, f, ensure_ascii=False, indent=4)

print(f"Fixed {fixed} NS game titles")
print("Samples:")
for g in games:
    if g['platform'] == 'ns':
        print(f"  {g['title']}")
        break
