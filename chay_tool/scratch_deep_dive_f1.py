# -*- coding: utf-8 -*-
import sys, os, io, re, extract_msg
from bs4 import BeautifulSoup
from core_logic import extract_table_from_html, safe_fix_font

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

f1 = r"d:\Dự án AI\chay_tool\emails\failed_RE_ Thẩm định an ninh thực địa và giá MBMM_  BNH _ Trung Tâm_ Hợp Thịnh (MB07834).msg"

msg = extract_msg.Message(f1)
soup = BeautifulSoup(msg.htmlBody, 'html.parser')

print("=== FILE 1 DEEP DIVE TABLES ===")
for table in soup.find_all('table'):
    rows = table.find_all('tr')
    for r in rows:
        cells = [c.get_text(separator=' ', strip=True) for c in r.find_all(['th', 'td'])]
        print("ROW:", cells)
msg.close()
