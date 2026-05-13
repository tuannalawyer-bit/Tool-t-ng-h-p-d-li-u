# -*- coding: utf-8 -*-
import sys, os, io, extract_msg
from core_logic import extract_table_from_html

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

f3 = r"d:\Dự án AI\chay_tool\emails\RE_ TKMB MN trình AN thẩm định gia hạn của MB_ 6175_WM+ NAN Thôn 7_ Xã Diễn Kỷ_ Huyện Diễn Châu_ Tỉnh Nghệ An.msg"

msg = extract_msg.Message(f3)
html_bytes = msg.htmlBody
data = extract_table_from_html(html_bytes, anchor_ma_mb="")

print("--- RAW TABLE EXTRACTION OUTPUT FOR FILE 3 ---")
for k, v in data.items():
    print(f"'{k}': '{v}'")
msg.close()
