# -*- coding: utf-8 -*-
import sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

s1 = "Chiò Phýõòng"
s2 = "Thôn NguÞ HôÌ"

print("=== TESTING VISCII CODEC ===")
try:
    # First encode to latin1 to get raw bytes, then decode as viscii
    b1 = s1.encode('latin1')
    print(f"Decoded via VISCII: {b1.decode('viscii')}")
    
    b2 = s2.encode('latin1')
    print(f"Decoded via VISCII: {b2.decode('viscii')}")
except Exception as e:
    print(f"VISCII failed: {e}")

print("\n=== TESTING TCVN3 (CP1258 / OTHER) ===")
try:
    print(f"Decoded via CP1258: {s1.encode('latin1').decode('cp1258')}")
except Exception as e:
    print(f"CP1258 failed: {e}")
