# -*- coding: utf-8 -*-
import sys, os, io
import extract_msg

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
current_dir = r'd:\Dự án AI\chay_tool'
sys.path.insert(0, current_dir)

import core_logic

# Mock reader and Gemini so we don't use internet or deep download.
core_logic.GEMINI_AVAILABLE = False
core_logic._gemini_client = None

# We monkey patch the extract_msg behavior to skip attachments reading, 
# or we can just monkey patch process_msg_file's inner loop if we want.
# Actually, let's just disable get_ocr.
def dummy_ocr():
    return None
core_logic.get_ocr = dummy_ocr

failed_files = [
    r"failed_RE_ 20251113_Thẩm định AN_ Mặt bằng mở mới (MB) - P2_WM+ VPC Thôn Ngũ Hồ_MB07620.msg",
    r"failed_RE_ Thẩm định AN_ Mặt bằng mở mới (MB)_ MN2665_Xóm 6_ X_ Quỳnh Minh_ H_ Quỳnh Lưu_ T_ Nghệ An.msg"
]

print("=== SIMULATING CORE LOGIC EXTRACTION ===")
for filename in failed_files:
    full_path = os.path.join(current_dir, filename)
    print(f"\n>>> Testing: {filename}")
    # We temporarily replace msg.attachments to [] during extraction to skip OCR downloading
    # To do that without rewriting core_logic, we override Message slightly.
    old_Message = extract_msg.Message
    class MockMsg(old_Message):
        @property
        def attachments(self):
            return []
    extract_msg.Message = MockMsg
    
    try:
        res = core_logic.process_msg_file(full_path)
        print(f"RESULT STATUS: {'SUCCESS' if res['success'] else 'FAIL'} | PARTIAL: {res.get('partial')}")
        print(f"MISSING FIELDS: {res.get('missing_fields')}")
        data = res.get('data', {})
        print(f"  ma_mb: {data.get('ma_mb')}")
        print(f"  thong_tin_mb: {data.get('thong_tin_mb')}")
        print(f"  dtt: {data.get('dtt')}")
        print(f"  gia_thue_vat: {data.get('gia_thue_vat')}")
        print(f"  tinh: {data.get('tinh')}")
        print(f"  bct: {data.get('bct')}")
        print(f"  cv_tkmb: {data.get('cv_tkmb')}")
        print(f"  tn_tkmb: {data.get('tn_tkmb')}")
        if res.get('error'):
             print(f"  ERROR: {res.get('error')}")
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        extract_msg.Message = old_Message
