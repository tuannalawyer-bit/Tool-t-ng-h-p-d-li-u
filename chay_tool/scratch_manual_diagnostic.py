# -*- coding: utf-8 -*-
import sys, os, io
import extract_msg

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
current_dir = r'd:\Dự án AI\chay_tool'

failed_files = [
    r"failed_RE_ 20251113_Thẩm định AN_ Mặt bằng mở mới (MB) - P2_WM+ VPC Thôn Ngũ Hồ_MB07620.msg",
    r"failed_RE_ Thẩm định AN_ Mặt bằng mở mới (MB)_ MN2665_Xóm 6_ X_ Quỳnh Minh_ H_ Quỳnh Lưu_ T_ Nghệ An.msg"
]

print("=== MANUAL FILE DIAGNOSIS ===")
for filename in failed_files:
    full_path = os.path.join(current_dir, filename)
    print(f"\n>>> File: {filename}")
    if not os.path.exists(full_path):
        print("FILE NOT FOUND")
        continue
    try:
        msg = extract_msg.Message(full_path)
        print(f"SUBJECT: {msg.subject}")
        print(f"FROM: {msg.sender}")
        print(f"CC: {msg.cc}")
        print(f"ATTACHMENTS: {[a.longFilename or a.shortFilename for a in msg.attachments]}")
        print("----- BODY SNIPPET (First 50 lines) -----")
        lines = [l.strip() for l in (msg.body or "").split('\n') if l.strip()]
        for i, line in enumerate(lines[:50]):
            print(f"Line {i}: {line}")
        msg.close()
    except Exception as e:
        print(f"Error reading: {e}")
