import sys, io, re, unicodedata
from rapidfuzz import fuzz

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ADMIN_WORDS = [
    r'\bthành phố\b', r'\btp\b', r'\btỉnh\b', r'\bquận\b', r'\bhuyện\b', r'\bthị xã\b', r'\bthị trấn\b', r'\btt\b',
    r'\bphường\b', r'\bxã\b', r'\bthôn\b', r'\bxóm\b', r'\btổ dân phố\b', r'\btdp\b', r'\btổ\b', r'\bkhu vực\b',
    r'\bkhu\b', r'\bấp\b', r'\bđường\b', r'\bphố\b', r'\bngõ\b', r'\bhẻm\b', r'\bsố\b', r'\btòa nhà\b', r'\bchợ\b',
    r'\bkđt\b', r'\bkhu đô thị\b', r'\bđ\b', r'\bp\b', r'\bq\b', r'\bt\b', r'\bh\b', r'\bx\b', r'\btb\b', r'\btbd\b', r'\btđ\b'
]

def normalize_core_addr_accents(s):
    if not s or s != s: return ""
    s = str(s).lower()
    s = unicodedata.normalize('NFC', s)
    s = re.sub(r'[\W_]+', ' ', s)
    
    for word in ADMIN_WORDS:
        s = re.sub(word, ' ', s)
    
    return " ".join(s.split())

s1 = "Phố Điền Lư, Xã Điền Lư, Tỉnh Thanh Hóa"
s2 = "Số 07-09, Tô Vĩnh Diện, Phường Điện Biên, TP Thanh Hóa"

s1_norm = normalize_core_addr_accents(s1)
s2_norm = normalize_core_addr_accents(s2)

print(f"s1_norm (with accents): '{s1_norm}'")
print(f"s2_norm (with accents): '{s2_norm}'")

score_set = fuzz.token_set_ratio(s1_norm, s2_norm)
score_sort = fuzz.token_sort_ratio(s1_norm, s2_norm)
score_final = (score_set + score_sort) / 2

print(f"token_set_ratio: {score_set:.2f}")
print(f"token_sort_ratio: {score_sort:.2f}")
print(f"Final Score: {score_final:.2f}")
