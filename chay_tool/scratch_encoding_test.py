# -*- coding: utf-8 -*-
import sys, extract_msg, io
from bs4 import BeautifulSoup

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

f1 = r"d:\Dự án AI\chay_tool\failed_RE_ 20251113_Thẩm định AN_ Mặt bằng mở mới (MB) - P2_WM+ VPC Thôn Ngũ Hồ_MB07620.msg"
msg = extract_msg.Message(f1)
html_bytes = msg.htmlBody

print("=== COMPARING DECODING METHODS ===")

# 1. Original Hardcoded UTF-8
try:
    txt1 = html_bytes.decode('utf-8', errors='ignore')
    soup1 = BeautifulSoup(txt1, 'html.parser')
    text1 = soup1.get_text()
    if "0356302380" in text1:
        idx = text1.find("0356302380")
        print(f"UTF-8 DECODE: {text1[idx-15 : idx+15].strip()}")
except Exception as e:
    print(f"UTF-8 Failed: {e}")

# 2. BS4 Auto-Detection (Passing Bytes Directly)
try:
    soup2 = BeautifulSoup(html_bytes, 'html.parser')
    text2 = soup2.get_text()
    if "0356302380" in text2:
        idx = text2.find("0356302380")
        print(f"BS4 AUTO-DETECTION: {text2[idx-15 : idx+15].strip()}")
    # Let's see what encoding BS4 picked
    print(f"Detected Encoding by BS4: {soup2.original_encoding}")
except Exception as e:
    print(f"BS4 Auto Failed: {e}")

# 3. Try Windows-1258 (Vietnamese legacy)
try:
    txt3 = html_bytes.decode('windows-1258', errors='ignore')
    soup3 = BeautifulSoup(txt3, 'html.parser')
    text3 = soup3.get_text()
    if "0356302380" in text3:
        idx = text3.find("0356302380")
        print(f"WINDOWS-1258 DECODE: {text3[idx-15 : idx+15].strip()}")
except: pass

msg.close()
