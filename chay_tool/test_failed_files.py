# -*- coding: utf-8 -*-
import sys, glob
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\TĐMB\chay tool')
import importlib, email_tool
importlib.reload(email_tool)

# Test all failed_ files
files = glob.glob(r'D:\TĐMB\chay tool\failed_*.msg')
print(f'Failed files found: {len(files)}')

for f in files:
    res = email_tool.process_msg_file(f)
    d = res.get('data', {})
    status = 'OK' if res['success'] else 'FAIL'
    fname = f.split('\\')[-1][:70]
    print(f'[{status}] {fname}')
    if res['success']:
        ma = d.get('ma_mb', '')
        dtt = d.get('dtt', '')
        gia = d.get('gia_thue_vat', '')
        tinh = d.get('tinh', '')
        print(f'       MaMB={ma}, DTT={dtt}, Gia={gia}, Tinh={tinh}')
    else:
        print(f'       ERR: {res["error"]}')
