import json
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

with open('sheet_analysis.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"File name: {data.get('file_name')}")
print(f"File size: {data.get('file_size_mb')} MB\n")

for s in data['sheets']:
    sheet_name = s['sheet_name']
    row_count = s['row_count']
    headers = s['column_headers']
    # Clean headers by removing empty strings to get a count of non-empty headers
    active_cols = [h for h in headers if h.strip() != ""]
    print(f"- Sheet: {sheet_name}")
    print(f"  Rows: {row_count}")
    print(f"  Headers (sample): {active_cols[:10]}")
    print("-" * 30)
