# -*- coding: utf-8 -*-
import sys, os, io, extract_msg

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
current_dir = r'd:\Dự án AI\chay_tool'
sys.path.insert(0, current_dir)

# Disable easyocr to prevent waiting for download
import core_logic
def dummy_ocr(): return None
core_logic.get_ocr = dummy_ocr

# Override to simulate fast skip of attachments loop
old_msg = extract_msg.Message
class MockMsg(old_msg):
    @property
    def attachments(self): return []
extract_msg.Message = MockMsg

f1 = r"d:\Dự án AI\chay_tool\failed_RE_ 20251113_Thẩm định AN_ Mặt bằng mở mới (MB) - P2_WM+ VPC Thôn Ngũ Hồ_MB07620.msg"
f2 = r"d:\Dự án AI\chay_tool\failed_RE_ Thẩm định AN_ Mặt bằng mở mới (MB)_ MN2665_Xóm 6_ X_ Quỳnh Minh_ H_ Quỳnh Lưu_ T_ Nghệ An.msg"

print("=== FINAL VERIFICATION OF PATCHES ===")
for f in [f1, f2]:
    res = core_logic.process_msg_file(f)
    print(f"\nFile: {os.path.basename(f)}")
    print(f"Status: {'SUCCESS' if res['success'] else 'FAILED'}")
    print(f"Partial: {res.get('partial')}")
    print(f"Missing: {res.get('missing_fields')}")
    if res['success']:
        d = res['data']
        print(f" >> MA_MB: {d.get('ma_mb')}")
        print(f" >> DTT: {d.get('dtt')}")
        print(f" >> GIA_THUE: {d.get('gia_thue_vat')}")
        print(f" >> BCT: {d.get('bct')}")
        print(f" >> TN_TKMB: {d.get('tn_tkmb')}")
    else:
        print(f" >> ERROR: {res.get('error')}")
