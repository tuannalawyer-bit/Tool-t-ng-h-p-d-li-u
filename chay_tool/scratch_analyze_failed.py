# -*- coding: utf-8 -*-
import sys, os, json
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

current_dir = r'd:\Dự án AI\chay_tool'
sys.path.insert(0, current_dir)

import core_logic

# Let's initialize Gemini to make sure it runs the full pipeline if key exists
api_key_path = os.path.join(current_dir, "gemini_api_key.txt")
if os.path.exists(api_key_path):
    with open(api_key_path, "r") as f:
        key = f.read().strip()
    try:
        core_logic.init_gemini(key)
        print("[DEBUG] Gemini initialized successfully.")
    except Exception as e:
        print(f"[DEBUG] Gemini init warning: {e}")
else:
    print("[DEBUG] No Gemini key found.")

failed_files = [
    r"failed_RE_ 20251113_Thẩm định AN_ Mặt bằng mở mới (MB) - P2_WM+ VPC Thôn Ngũ Hồ_MB07620.msg",
    r"failed_RE_ Thẩm định AN_ Mặt bằng mở mới (MB)_ MN2665_Xóm 6_ X_ Quỳnh Minh_ H_ Quỳnh Lưu_ T_ Nghệ An.msg"
]

print("=== ANALYZING FAILED FILES ===")
for filename in failed_files:
    full_path = os.path.join(current_dir, filename)
    print(f"\n>>> File: {filename}")
    if not os.path.exists(full_path):
        print("FILE NOT FOUND")
        continue
    try:
        result = core_logic.process_msg_file(full_path)
        print("Result Structure:")
        print(f"  Success: {result.get('success')}")
        print(f"  Partial: {result.get('partial')}")
        if result.get('error'):
             print(f"  Error: {result.get('error')}")
        if result.get('missing_fields'):
             print(f"  Missing Fields: {result.get('missing_fields')}")
        
        data = result.get('data', {})
        print("  Extracted Data Snippet:")
        for k, v in data.items():
            if v:
                print(f"    - {k}: {v}")
            else:
                print(f"    - {k}: MISSING")
    except Exception as e:
        print(f"CRITICAL ERROR during processing: {e}")
