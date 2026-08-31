import json
d = json.load(open('data/games.json','r',encoding='utf-8'))
pc = [g for g in d if g['platform']=='pc' and g.get('coverImage')]
pc.sort(key=lambda x: x.get('reviewScore', 0), reverse=True)
for g in pc[:12]:
    print(f"标题: {g['title']}")
    print(f"评分: {g.get('reviewScore')}")
    print(f"封面: {g['coverImage']}")
    shots = g.get('screenshots','').split(',') if g.get('screenshots') else []
    print(f"截图1: {shots[0] if shots else '无'}")
    print('---')
