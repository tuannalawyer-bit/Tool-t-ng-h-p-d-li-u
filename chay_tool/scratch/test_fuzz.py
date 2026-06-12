from rapidfuzz import fuzz
from unidecode import unidecode
import re

def normalize_addr(s):
    if not s: return ""
    s = re.sub(r'\([^)]*\)', '', str(s))   # bỏ phần trong ngoặc
    s = s.lower()
    s = unidecode(s)
    s = re.sub(r'[\W_]+', ' ', s)
    return " ".join(s.split())

s1 = "Thửa đất 1094-1787, tờ bản đồ số 86, Thôn Sao Vàng 1, Xã Hoằng Phú, Tỉnh Thanh Hóa"
s2 = "Hà Lũng Thượng, Thọ Dân, Triệu Sơn, Thanh Hóa (1)"

s1_norm = normalize_addr(s1)
s2_norm = normalize_addr(s2)

print(f"s1_norm: {s1_norm}")
print(f"s2_norm: {s2_norm}")

score_ratio = fuzz.ratio(s1_norm, s2_norm)
score_token_set = fuzz.token_set_ratio(s1_norm, s2_norm)
score_token_sort = fuzz.token_sort_ratio(s1_norm, s2_norm)

print(f"fuzz.ratio: {score_ratio}")
print(f"fuzz.token_set_ratio: {score_token_set}")
print(f"fuzz.token_sort_ratio: {score_token_sort}")

# Let's test the inner address extraction too
s2_with_inner = "TÐ số 316, TBÐ số 12, Thôn Duyên Hà, X. Bắc Ðông Quan, T. Hưng Yên (Ðịa chỉ ðầu vào: Thôn Duyên Hà, X. Ðông Kinh, H. Ðông Hưng, T. Thái Bình)"
def extract_inner_addr(s):
    if not s: return ""
    m = re.search(r'\(([^)]+)\)', str(s))
    if not m: return ""
    inner = m.group(1)
    inner = re.sub(r'^(?:Địa chỉ (?:đầu vào|ban đầu)|Đầu vào)[:\s]*', '', inner, flags=re.IGNORECASE)
    return normalize_addr(inner)

print(f"Inner: {extract_inner_addr(s2_with_inner)}")

