# -*- coding: utf-8 -*-
import sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

bad_str = "Chiò Phýõòng"
print(f"Attempting to fix: {bad_str}")

# Common mojibake sequences for Vietnamese
encodings = ['utf-8', 'cp1252', 'latin-1', 'cp1258', 'iso-8859-1']

for e1 in encodings:
    for e2 in encodings:
        if e1 == e2: continue
        try:
            candidate = bad_str.encode(e1).decode(e2)
            if "Chị" in candidate or "Phượng" in candidate:
                 print(f"SUCCESS FOUND: {e1} -> {e2}: {candidate}")
        except: pass

# Let's try manually mapping the broken characters
def fix_vn_mojibake(s):
    mapping = {
        'ò': 'ị', 'ý': 'ư', 'õ': 'ơ', 'ã': 'ă', 'â': 'â',
        'Ð': 'Đ', 'ð': 'đ', 'ê': 'ê', 'ô': 'ô',
    }
    # wait, it's more complex than simple mapping
    return s

print("Script finished.")
