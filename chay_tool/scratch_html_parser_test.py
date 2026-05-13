# -*- coding: utf-8 -*-
import sys, extract_msg, io
from bs4 import BeautifulSoup

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

f1 = r"d:\Dự án AI\chay_tool\failed_RE_ 20251113_Thẩm định AN_ Mặt bằng mở mới (MB) - P2_WM+ VPC Thôn Ngũ Hồ_MB07620.msg"
msg = extract_msg.Message(f1)
html = msg.htmlBody
print("--- HTML ANALYSIS USING HTML.PARSER ---")
if html:
    # Use standard builtin html.parser
    soup = BeautifulSoup(html.decode('utf-8', errors='ignore'), 'html.parser')
    tables = soup.find_all('table')
    print(f"Found {len(tables)} tables.")
    for i, t in enumerate(tables):
        print(f"\n--- TABLE {i} CONTENT ---")
        rows = t.find_all('tr')
        for r in rows:
             cells = [c.get_text(strip=True) for c in r.find_all(['td', 'th'])]
             if cells:
                 print(cells)
msg.close()
