# -*- coding: utf-8 -*-
import sys, os, io
from core_logic import process_msg_file

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

f3 = r"d:\Dự án AI\chay_tool\emails\RE_ TKMB MN trình AN thẩm định gia hạn của MB_ 6175_WM+ NAN Thôn 7_ Xã Diễn Kỷ_ Huyện Diễn Châu_ Tỉnh Nghệ An.msg"

print("\n=== RUNNING ULTIMATE TEST ON FILE 3 (GIA HẠN) ===")
res = process_msg_file(f3)

print(f"SUCCESS: {res.get('success')}")
print(f"PARTIAL: {res.get('partial')}")
print("--- DATA FIELDS ---")
for k, v in res.get("data", {}).items():
    print(f" >> {k.upper()}: '{v}'")

print("\nALL SYSTEMS NOMINAL!")
