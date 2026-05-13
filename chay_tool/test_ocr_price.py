# -*- coding: utf-8 -*-
"""
Test parse_table_from_ocr with various simulated OCR outputs
to verify price detection works across all format variants.
"""
import sys, re
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\TĐMB\chay tool')

import importlib
import email_tool
importlib.reload(email_tool)

# --- Test cases: simulate what Windows OCR might output ---
test_cases = [
    # (description, ocr_text, expected_price)
    ("Normal: Giá thuê 15.000.000",
     "MB07930 QNH Thon Phu Cu Hong Chau Hai Phong DTT 160 Truong Nguyen Van Long Gia thue 15.000.000 BCT Phong 0336123456",
     "15.000.000"),

    ("Dấu: Giá thuê 15.000.000",
     "MB07930 Giá thuê 15.000.000 DTT 160 BCT Hùng 0394355965",
     "15.000.000"),

    ("No-accent: Gia thue 15.000.000",
     "MB07930 Gia thue 15.000.000 DTT 160",
     "15.000.000"),

    ("With comma: 15,000,000",
     "MB07930 Gia thue 15,000,000 DTT 160",
     "15,000,000"),

    ("With spaces: 15 000 000",
     "MB07930 Gia thue 15 000 000 DTT 160",
     "15.000.000"),

    ("No keyword, just number: 15.000.000",
     "MB07930 DTT 160 Truong Nguyen Van Long BCT Hung 0394355965 15.000.000",
     "15.000.000"),

    ("OCR garbled: Gi thue 15.000.000",
     "MB07930 Gi thue 15.000.000",
     "15.000.000"),

    ("Header then value (2 lines joined): 'Gia thue 15000000'",
     "MB07930 Gia thue 15000000",
     "15.000.000"),  # Strategy 4

    ("Giá thuê có thuế: 15.000.000",
     "MB07930 Giá thuê có thuế 15.000.000 DTT 160",
     "15.000.000"),
]

print("=" * 60)
print("TEST: parse_table_from_ocr price detection")
print("=" * 60)

passed = 0
failed = 0
for desc, ocr_text, expected in test_cases:
    result = email_tool.parse_table_from_ocr(ocr_text)
    got = result.get('gia_thue', '')
    # Normalize for comparison
    got_digits = re.sub(r'[.,\s]', '', got)
    exp_digits = re.sub(r'[.,\s]', '', expected)
    ok = got_digits == exp_digits
    status = "✅ PASS" if ok else "❌ FAIL"
    if ok:
        passed += 1
    else:
        failed += 1
    print(f"{status}  {desc}")
    if not ok:
        print(f"       Expected: {expected!r} (digits: {exp_digits})")
        print(f"       Got:      {got!r} (digits: {got_digits})")

print()
print(f"Result: {passed}/{passed+failed} passed")

# Also test real MB07985 if files exist
print()
print("=" * 60)
print("TEST: Real file parsing (MB07930, MB07985)")
print("=" * 60)
import glob, extract_msg, asyncio, os

for code in ['MB07930', 'MB07985', 'MB07884', 'MB07877']:
    files = glob.glob(rf'D:\TĐMB\chay tool\*{code}*.msg')
    if not files:
        print(f"[{code}] No file found")
        continue
    f = files[0]
    res = email_tool.process_msg_file(f)
    d = res.get('data', {})
    status = '✅ OK' if res['success'] else '❌ FAIL'
    print(f"[{code}] {status}")
    if res['success']:
        print(f"  MaMB={d.get('ma_mb','')}  DTT={d.get('dtt','')}  Gia={d.get('gia_thue_vat','')}  BCT={str(d.get('bct',''))[:30]}")
    else:
        print(f"  ERR: {res['error']}")
