import pandas as pd
from rapidfuzz import fuzz
import re
from unidecode import unidecode
import sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ADMIN_WORDS = [
    r'\bthanh pho\b', r'\btp\b', r'\btinh\b', r'\bquan\b', r'\bhuyen\b', r'\bthi xa\b', r'\bthi tran\b', r'\btt\b',
    r'\bphuong\b', r'\bxa\b', r'\bthon\b', r'\bxom\b', r'\bto dan pho\b', r'\btdp\b', r'\bto\b', r'\bkhu vuc\b',
    r'\bkhu\b', r'\bap\b', r'\bduong\b', r'\bpho\b', r'\bngo\b', r'\bhem\b', r'\bso\b', r'\btoa nha\b', r'\bcho\b',
    r'\bkdt\b', r'\bkhu do thi\b', r'\bd\b', r'\bp\b', r'\bq\b', r'\bt\b', r'\bh\b', r'\bx\b', r'\btb\b', r'\btbd\b', r'\btd\b'
]

def normalize_core_addr(s):
    if pd.isna(s): return ""
    s = s.lower()
    s = unidecode(s)
    s = re.sub(r'[\W_]+', ' ', s)
    for word in ADMIN_WORDS:
        s = re.sub(word, ' ', s)
    return " ".join(s.split())

s1 = "Phố Điền Lư, Xã Điền Lư, Tỉnh Thanh Hóa"
s2 = "Số 07-09, Tô Vĩnh Diện, Phường Điện Biên, TP Thanh Hóa"

s1_norm = normalize_core_addr(s1)
s2_norm = normalize_core_addr(s2)

print(f"s1_norm: '{s1_norm}'")
print(f"s2_norm: '{s2_norm}'")

score_set = fuzz.token_set_ratio(s1_norm, s2_norm)
score_sort = fuzz.token_sort_ratio(s1_norm, s2_norm)
score_final = (score_set + score_sort) / 2

print(f"token_set_ratio: {score_set}")
print(f"token_sort_ratio: {score_sort}")
print(f"Final Score (v2 logic): {score_final}")
