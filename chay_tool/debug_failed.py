# -*- coding: utf-8 -*-
import sys, glob, extract_msg, re
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\TĐMB\chay tool')

failed_files = glob.glob(r'D:\TĐMB\chay tool\failed_*.msg')
print(f'Total failed files: {len(failed_files)}')

for f in failed_files[:4]:
    try:
        msg = extract_msg.Message(f)
        body = (msg.body or '')
        subject = msg.subject or ''
        print(f'\n=== {f.split(chr(92))[-1][:80]} ===')
        print(f'Subject: {subject[:100]}')
        print(f'Body (first 40 non-empty lines):')
        lines = [l.strip() for l in body.split('\n') if l.strip()][:40]
        for i, l in enumerate(lines):
            print(f'  {i:2}: {l[:110]}')
        print()
        msg.close()
    except Exception as e:
        print(f'Error reading file: {e}')
