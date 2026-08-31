import openpyxl
import json

files = [
    r'c:\Users\73974\.trae-cn\attachments\6a9167779f968d5062a924c7\99fbefb3-b78b-4cab-a5a2-c24abf3e9bff_69aed267-f229-4878-8a4c-c04f01ebc5f6_安卓及PC移植合集（一）.xlsx',
    r'c:\Users\73974\.trae-cn\attachments\6a9167779f968d5062a924c7\deff19a7-ee97-4c5d-9b7b-7434719303cf_3c185d53-13b3-4391-96d4-3580d6bdbc2a_安卓及PC移植合集（二）.xlsx',
    r'c:\Users\73974\.trae-cn\attachments\6a9167779f968d5062a924c7\ee4e0e3d-8c79-40f7-ac02-f0aa3429f345_6706bb86-1d48-4ff0-9e80-b4463116b185_安卓手机游戏合集.xlsx',
]

all_games = []

for f in files:
    wb = openpyxl.load_workbook(f, read_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    
    # Print headers
    print(f"\n=== {f.split('_')[-1]} ===")
    print(f"Headers: {rows[0]}")
    print(f"Total rows (excl header): {len(rows)-1}")
    
    # Print first 3 data rows
    for r in rows[1:4]:
        print(f"  {r}")
    
    wb.close()

print(f"\nTotal data across all files would be checked above")
