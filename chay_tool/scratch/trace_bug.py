import pandas as pd
from rapidfuzz import fuzz, process
import re
from unidecode import unidecode
import sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PATH1 = r"D:\OneDrive - WIN\Desktop\công việc thực hiện\Tháng 5\Chuyên đề xây dựng mở mới\danh sach ky hop dong.xlsx"
PATH2 = r"D:\OneDrive - WIN\Desktop\công việc thực hiện\Tháng 5\Chuyên đề xây dựng mở mới\form tool.xlsx"

df1 = pd.read_excel(PATH1)
df2 = pd.read_excel(PATH2, header=2)
df1 = df1.dropna(subset=['Địa chỉ']).reset_index(drop=True)
df2 = df2.dropna(subset=['Thông tin MB đang thuê']).reset_index(drop=True)

def normalize_tinh(s):
    if pd.isna(s): return ""
    s = str(s).strip()
    s = re.sub(r'^(TP\.|T\.|Tỉnh|Thành phố|Thành Phố|TPHCM)\s*', '', s, flags=re.IGNORECASE)
    s = s.split('/')[0].strip()
    return unidecode(s).lower().strip()

def normalize_addr(s):
    if pd.isna(s): return ""
    s = re.sub(r'\([^)]*\)', '', str(s))
    s = s.lower()
    s = unidecode(s)
    s = re.sub(r'[\W_]+', ' ', s)
    return " ".join(s.split())

def extract_inner_addr(s):
    if pd.isna(s): return ""
    m = re.search(r'\(([^)]+)\)', str(s))
    if not m: return ""
    inner = m.group(1)
    inner = re.sub(r'^(?:Địa chỉ (?:đầu vào|ban đầu)|Đầu vào)[:\s]*', '', inner, flags=re.IGNORECASE)
    return normalize_addr(inner)

tinh1_n = df1['Tỉnh/TP/Quận'].apply(normalize_tinh)
tinh2_n = df2['Tỉnh'].apply(normalize_tinh)
addr1_n = df1['Địa chỉ'].apply(normalize_addr)
addr2_outer_n = df2['Thông tin MB đang thuê'].apply(normalize_addr)
addr2_inner_n = df2['Thông tin MB đang thuê'].apply(extract_inner_addr)

tinh2_unique = tinh2_n.unique().tolist()
addr2_outer_list = addr2_outer_n.tolist()
addr2_inner_list = addr2_inner_n.tolist()

idx1 = 265
t1 = tinh1_n.iloc[idx1]
a1 = addr1_n.iloc[idx1]
print(f"Index 265:")
print(f"  t1: {t1}")
print(f"  a1: {a1}")

tinh_match = process.extractOne(t1, tinh2_unique, scorer=fuzz.ratio)
print(f"  tinh_match: {tinh_match}")

if tinh_match and tinh_match[1] >= 80:
    matched_tinh_val = tinh_match[0]
    sub_idx = tinh2_n[tinh2_n == matched_tinh_val].index.tolist()
    sub_outer = [addr2_outer_list[j] for j in sub_idx]
    
    r_out = process.extractOne(a1, sub_outer, scorer=fuzz.token_set_ratio)
    print(f"  r_out: {r_out}")
    if r_out:
        orig_j = sub_idx[r_out[2]]
        print(f"  Matched outer in df2 at {orig_j}: {df2['Thông tin MB đang thuê'].iloc[orig_j]}")

    sub_inner_pairs = [(addr2_inner_list[j], j) for j in sub_idx if addr2_inner_list[j]]
    if sub_inner_pairs:
        r_inn = process.extractOne(a1, [v for v, _ in sub_inner_pairs], scorer=fuzz.token_set_ratio)
        print(f"  r_inn: {r_inn}")
        if r_inn:
            orig_j = sub_inner_pairs[r_inn[2]][1]
            print(f"  Matched inner in df2 at {orig_j}: {df2['Thông tin MB đang thuê'].iloc[orig_j]}")

