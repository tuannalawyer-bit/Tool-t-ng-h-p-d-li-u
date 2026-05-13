# -*- coding: utf-8 -*-
import sys, extract_msg, io
from bs4 import BeautifulSoup

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def extract_table_improved(html_bytes):
    if not html_bytes: return {}
    soup = BeautifulSoup(html_bytes.decode('utf-8', errors='ignore'), 'html.parser')
    data = {}
    for table in soup.find_all('table'):
        rows = table.find_all('tr')
        if not rows: continue
        for i, row in enumerate(rows):
            cells = [c.get_text(separator=' ', strip=True) for c in row.find_all(['th', 'td'])]
            if not cells: continue
            if len(cells) == 2:
                key = cells[0].lower().strip()
                val = cells[1].strip()
                # ONLY write if not already filled! Prevents trailing history threads from overwriting.
                if not data.get(key): data[key] = val
            if any('mã mb' in c.lower() or 'giá thuê' in c.lower() for c in cells):
                headers = [c.lower().strip() for c in cells]
                if i + 1 < len(rows):
                    data_cells = [c.get_text(separator=' ', strip=True) for c in rows[i+1].find_all(['th', 'td'])]
                    for h, v in zip(headers, data_cells + ['']*(len(headers)-len(data_cells))):
                        if h and v and not data.get(h): # PRESERVE FIRST MATCH
                             data[h] = v
    return data

f1 = r"d:\Dự án AI\chay_tool\failed_RE_ 20251113_Thẩm định AN_ Mặt bằng mở mới (MB) - P2_WM+ VPC Thôn Ngũ Hồ_MB07620.msg"
msg = extract_msg.Message(f1)
result = extract_table_improved(msg.htmlBody)
print("--- IMPROVED HTML EXTRACTION RESULT ---")
for k, v in result.items():
    print(f"  - {k}: {v}")
msg.close()
