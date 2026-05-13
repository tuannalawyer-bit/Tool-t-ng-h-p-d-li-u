# -*- coding: utf-8 -*-
import sys, os, io, re
import extract_msg
from bs4 import BeautifulSoup
from core_logic import process_msg_file, extract_table_from_html

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

f1 = r"d:\Dự án AI\chay_tool\emails\failed_RE_ Thẩm định an ninh thực địa và giá MBMM_  BNH _ Trung Tâm_ Hợp Thịnh (MB07834).msg"
f2 = r"d:\Dự án AI\chay_tool\emails\failed_RE_ Thẩm định AN_  WM+ BNH Đại Trạch_ xã Đình Tổ  (MB06650).msg"
f3 = r"d:\Dự án AI\chay_tool\emails\RE_ TKMB MN trình AN thẩm định gia hạn của MB_ 6175_WM+ NAN Thôn 7_ Xã Diễn Kỷ_ Huyện Diễn Châu_ Tỉnh Nghệ An.msg"

files = [f1, f2, f3]

print("=== EXPERT DIAGNOSTIC REPORT ===")

for i, fpath in enumerate(files, 1):
    print(f"\n--- ANALYZING FILE {i}: {os.path.basename(fpath)} ---")
    if not os.path.exists(fpath):
        print("FILE NOT FOUND!")
        continue
        
    try:
        # 1. Direct core_logic run
        result = process_msg_file(fpath)
        print(f"CoreLogic Execution Status: {result.get('status')}")
        print(f"Partial: {result.get('partial')}")
        print(f"Missing Fields: {result.get('missing_fields')}")
        print("Extracted Values:")
        for k in ['ma_mb', 'dtt', 'gia_thue', 'bct', 'tn_tkmb']:
            print(f" >> {k.upper()}: '{result.get(k, '')}'")
            
        # 2. Dig deeper if it totally skipped or missed major fields
        msg = extract_msg.Message(fpath)
        print(f"Subject: {msg.subject}")
        
        # Check Table Data
        html_bytes = msg.htmlBody
        
        # Test anchor matching
        subject_ma_mb = ""
        m_sub = re.search(r'(?:[^a-zA-Z0-9]|^)(MB[\s_]*\d+|MN[\s_]*\d+)', msg.subject, re.IGNORECASE)
        if m_sub:
            subject_ma_mb = re.sub(r'[\s_]+', '', m_sub.group(1)).upper()
        
        print(f"Detected Subject Anchor: '{subject_ma_mb}'")
        
        table_data = extract_table_from_html(html_bytes, anchor_ma_mb=subject_ma_mb)
        print("HTML Table Keys Found:", list(table_data.keys()))
        if not table_data:
            print("WARNING: HTML TABLE EXTRACTOR RETURNED EMPTY DICT!")
            
        msg.close()

    except Exception as e:
        print(f"FATAL ERROR RUNNING FILE: {e}")
        import traceback
        traceback.print_exc()

print("\n=== DIAGNOSTIC END ===")
