# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def fix_font(text):
    if not isinstance(text, str) or not text: return text
    # Detect condition where fixing is SAFE:
    # Strings containing high Latin-1 symbols that don't make sense in standard text
    bad_symbols = ['ý', 'õ', 'ò', 'Þ', 'Ì', 'Ð']
    if any(sym in text for sym in bad_symbols):
        try:
             return text.encode('latin1').decode('cp1258')
        except:
             return text
    return text

test1 = "Chiò Phýõòng"
test2 = "Thôn NguÞ HôÌ"
test3 = "Trần Huy Dũng" # Already perfect UTF-8

print(f"Fixed 1: {fix_font(test1)}")
print(f"Fixed 2: {fix_font(test2)}")
print(f"Fixed 3: {fix_font(test3)}")
