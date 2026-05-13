# -*- coding: utf-8 -*-
import sys, re, extract_msg, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def test_regex(body):
    print("--- TESTING BODY ---")
    # Test DTT regex exactly as in core_logic
    m = re.search(r'(?:diện tích\s*(?:là\s*|:\s*)?|DTT[^\d\n]*)(\d+(?:[.,]\d+)?)|(\d+(?:[.,]\d+)?)\s*m2', body, re.IGNORECASE)
    if m:
        print(f"DTT Match Groups: {m.groups()}")
        print(f"DTT Final Value: {(m.group(1) or m.group(2))}")
        print(f"Matched Text: '{m.group(0)}'")
    
    # Test phone/bct
    print("--- Testing BCT regex ---")
    body_phones = re.finditer(r'(?:Cô|Chú|Bác|Anh|Chị|Ông|Bà|BCT)\s*([A-Z][a-zà-ỹA-ZÀ-Ỹ\s]{1,20})?[:\-]?\s*(0\d{2,3}[\s.]?\d{3,4}[\s.]?\d{3,4})', body, re.IGNORECASE)
    found = False
    for match in body_phones:
        found = True
        print(f"BCT Match: name='{match.group(1)}', phone='{match.group(2)}'")
    if not found: print("No standard BCT regex match found.")

    # Let's try a more inclusive Vietnamese phone pattern
    print("--- Testing generic VN phone search ---")
    phone_matches = re.findall(r'(?:\b|[^0-9])(0\d{2,3}[\s.]?\d{3,4}[\s.]?\d{3,4})(?:\b|[^0-9])', body)
    print(f"Generic phones found: {phone_matches}")

f1 = r"d:\Dự án AI\chay_tool\failed_RE_ 20251113_Thẩm định AN_ Mặt bằng mở mới (MB) - P2_WM+ VPC Thôn Ngũ Hồ_MB07620.msg"
f2 = r"d:\Dự án AI\chay_tool\failed_RE_ Thẩm định AN_ Mặt bằng mở mới (MB)_ MN2665_Xóm 6_ X_ Quỳnh Minh_ H_ Quỳnh Lưu_ T_ Nghệ An.msg"

for f in [f1, f2]:
    print(f"\n>>> FILE: {f.split(chr(92))[-1]}")
    msg = extract_msg.Message(f)
    test_regex(msg.body or "")
    msg.close()
