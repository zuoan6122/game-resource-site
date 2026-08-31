import openpyxl
import json

f = r'c:\Users\73974\.trae-cn\attachments\6a9167779f968d5062a924c7\58832706-bee0-4e23-b92d-623c7e742629_872da4ae-93e6-42df-ab7b-82f60ff7543b_NS游戏合集（一）.xlsx'

wb = openpyxl.load_workbook(f, read_only=True)
ws = wb.active
rows = list(ws.iter_rows(values_only=True))

print(f"Headers: {rows[0]}")
print(f"Total rows: {len(rows)-1}")
print(f"First 5 rows:")
for r in rows[1:6]:
    print(f"  {r}")

wb.close()
