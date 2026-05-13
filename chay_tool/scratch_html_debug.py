# -*- coding: utf-8 -*-
import sys, extract_msg, io
from bs4 import BeautifulSoup

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

f1 = r"d:\Dự án AI\chay_tool\failed_RE_ 20251113_Thẩm định AN_ Mặt bằng mở mới (MB) - P2_WM+ VPC Thôn Ngũ Hồ_MB07620.msg"

msg = extract_msg.Message(f1)
html = msg.htmlBody
print("--- HTML ANALYSIS ---")
if not html:
    print("NO HTML BODY")
else:
    print(f"HTML Length: {len(html)}")
    soup = BeautifulSoup(html, 'lxml')
    tables = soup.find_all('table')
    print(f"Found {len(tables)} tables.")
    for i, t in enumerate(tables):
        print(f"\n--- TABLE {i} SNIPPET ---")
        rows = t.find_all('tr')
        for r in rows[:5]:
             print([c.get_text(strip=True) for c in r.find_all(['td', 'th'])])
msg.close()
