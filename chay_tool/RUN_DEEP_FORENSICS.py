import sys
import os
import json

# Add logic and setup imports
sys.path.append(r"D:\chạy tool\chạy tool")
import extract_msg
from core_logic import process_msg_file

targets = [
    r"D:\chạy tool\chạy tool\emails\done_RE_ Thẩm định thực địa MB_ Số 23 đường Nghi Tân_ Đông Mai_ Quảng Ninh (MB07985).msg",
    r"D:\chạy tool\chạy tool\emails\done_RE_ Thẩm định thực địa MB_ Số 64 đường Bắc Hồng_ Thôn Quan Âm_ Hà Nội (MB07792).msg",
    r"D:\chạy tool\chạy tool\emails\done_RE_ 20251113_Thẩm định AN_ Mặt bằng mở mới (MB) - P2_WM+ VPC Thôn Ngũ Hồ_MB07620.msg"
]

report = []
for t in targets:
    if not os.path.exists(t): continue
    
    try:
        # Direct extraction look
        m = extract_msg.Message(t)
        subj = str(m.subject)
        body = str(m.body)[:500] # First 500 chars
        
        # Run the logic process
        def local_log(txt, level): pass
        res = process_msg_file(t, log_callback=None)
        
        report.append({
            "file": os.path.basename(t),
            "subject": subj,
            "extracted_data": res.get("data", {}),
            "missing": res.get("missing_fields", []),
            "partial_body_snippet": body
        })
    except Exception as e:
        report.append({"file": os.path.basename(t), "error": str(e)})

with open(r'd:\Dự án AI\chay_tool\deep_forensics.json', 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=4, ensure_ascii=False)
