# -*- coding: utf-8 -*-
import sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# The test subject string exactly as outputted by BS4
s1 = "Chiò Phýõòng"
s2 = "Thôn NguÞ HôÌ, xaÞ Thiện Kế"

print("Target 1: Chị Phượng")
print(f"Got string: {s1}")
for c in s1:
    print(f"  '{c}' U+{ord(c):04X}")

# Let's explore recursive re-encodings
def recursive_fix(text):
    encodings = ['utf-8', 'cp1252', 'iso-8859-1', 'macroman', 'windows-1258']
    for e1 in encodings:
        for e2 in encodings:
            if e1 == e2: continue
            try:
                t2 = text.encode(e1).decode(e2)
                if "ượ" in t2 or "ị" in t2 or "ũ" in t2:
                    print(f"WINNER ({e1} -> {e2}): {t2}")
            except: pass

recursive_fix(s1)
recursive_fix(s2)
