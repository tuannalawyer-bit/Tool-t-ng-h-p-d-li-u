# -*- coding: utf-8 -*-
import sys, glob, importlib
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\TĐMB\chạy tool')

import email_tool
importlib.reload(email_tool)

tests = {
    'OCR (Thanh Huong)': 'MB07985',
    'Shifted col (MB07948)': 'MB07948',
    'Duplicate (MB07899)': 'MB07899',
}

files = glob.glob(r'D:\TĐMB\chạy tool\*.msg')

for label, code in tests.items():
    matching = [f for f in files if code in f]
    if not matching:
        print(f'[{label}] No file found for {code}')
        continue
    print(f'--- {label} ({len(matching)} files) ---')
    for f in sorted(matching):
        res = email_tool.process_msg_file(f)
        d = res.get('data', {})
        status = 'OK' if res['success'] else 'FAIL'
        fname = f.split('\\')[-1][:65]
        print(f'  [{status}] {fname}')
        if res['success']:
            bct_short = d['bct'][:30] if d.get('bct') else '-'
            print(f'         MaMB={d["ma_mb"]}  DTT={d["dtt"]}  Gia={d["gia_thue_vat"]}  BCT={bct_short}')
        else:
            print(f'         ERR: {res["error"]}')
    print()

# Also check deduplication
print('--- DEDUP TEST: MB07899 (should produce 1 merged row) ---')
mb_files = [f for f in files if 'MB07899' in f]
results = [email_tool.process_msg_file(f) for f in sorted(mb_files)]
success = [r for r in results if r['success']]
print(f'  Raw results: {len(results)}, Success: {len(success)}')

# Simulate deduplication
import re
from datetime import datetime

earliest = {}
latest = {}
for res in success:
    data = res.get('data', {})
    ma_mb = data.get('ma_mb', '').strip().upper()
    ngay_tra = data.get('ngay_tra')
    
    if ma_mb not in earliest:
        earliest[ma_mb] = res
    else:
        ex = earliest[ma_mb]['data'].get('ngay_tra')
        if ngay_tra and (ex is None or ngay_tra < ex):
            earliest[ma_mb] = res
    
    if ma_mb not in latest:
        latest[ma_mb] = res
    else:
        la = latest[ma_mb]['data'].get('ngay_tra')
        if ngay_tra and (la is None or ngay_tra > la):
            latest[ma_mb] = res

for key in earliest:
    e = earliest[key]['data']
    l = latest[key]['data']
    print(f'  Earliest: ngay_tra={e["ngay_tra"]}, DTT={e["dtt"]}')
    print(f'  Latest:   ngay_tra={l["ngay_tra"]}, KSTT={l["chi_tiet_thamdinh"][:60] if l["chi_tiet_thamdinh"] else "-"}')
    print(f'  -> DEDUP OK: 1 row from {len(mb_files)} files')
