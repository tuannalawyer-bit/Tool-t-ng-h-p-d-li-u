# -*- coding: utf-8 -*-
import sys, os, io
from core_logic import process_msg_file

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

f1 = r"d:\Dự án AI\chay_tool\emails\failed_RE_ Thẩm định an ninh thực địa và giá MBMM_  BNH _ Trung Tâm_ Hợp Thịnh (MB07834).msg"
f2 = r"d:\Dự án AI\chay_tool\emails\failed_RE_ Thẩm định AN_  WM+ BNH Đại Trạch_ xã Đình Tổ  (MB06650).msg"

res1 = process_msg_file(f1)
print("\n--- FILE 1 FULL DATA ---")
print("Success:", res1.get("success"))
print("Partial:", res1.get("partial"))
print("Data Fields:")
for k, v in res1.get("data", {}).items():
    print(f" >> {k.upper()}: {v}")

res2 = process_msg_file(f2)
print("\n--- FILE 2 FULL DATA ---")
print("Success:", res2.get("success"))
print("Partial:", res2.get("partial"))
print("Data Fields:")
for k, v in res2.get("data", {}).items():
    print(f" >> {k.upper()}: {v}")
