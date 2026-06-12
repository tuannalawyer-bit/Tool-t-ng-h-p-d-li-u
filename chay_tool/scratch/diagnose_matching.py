import pandas as pd
import sys, io, re
from rapidfuzz import fuzz, process
from unidecode import unidecode

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

path1 = r"D:\OneDrive - WIN\Desktop\công việc thực hiện\Tháng 5\Chuyên đề xây dựng mở mới\danh sach ky hop dong.xlsx"
path2 = r"D:\OneDrive - WIN\Desktop\công việc thực hiện\Tháng 5\Chuyên đề xây dựng mở mới\form tool.xlsx"

# ==== LOAD ====
df1 = pd.read_excel(path1)
df2 = pd.read_excel(path2, header=2)

df1 = df1.dropna(subset=['Địa chỉ']).reset_index(drop=True)
df2 = df2.dropna(subset=['Thông tin MB đang thuê']).reset_index(drop=True)

print(f"=== FILE 1: danh sach ky hop dong ===")
print(f"Số dòng dữ liệu: {len(df1)}")
print(f"\n--- 10 địa chỉ mẫu (File 1) ---")
for i, v in enumerate(df1['Địa chỉ'].head(10)):
    print(f"  [{i}] {v}")

print(f"\n=== FILE 2: form tool ===")
print(f"Số dòng dữ liệu: {len(df2)}")
print(f"\n--- 10 địa chỉ mẫu (File 2) ---")
for i, v in enumerate(df2['Thông tin MB đang thuê'].head(10)):
    print(f"  [{i}] {v}")

# ==== NORMALIZE FUNCTIONS ====
def normalize_v1(s):
    """Normalize v1 - current"""
    if pd.isna(s): return ""
    s = str(s).lower()
    s = unidecode(s)
    s = re.sub(r'[\W_]+', ' ', s)
    return " ".join(s.split())

ABBREV_MAP = {
    r'\bp\.?\s': 'phuong ',
    r'\bx\.?\s': 'xa ',
    r'\bq\.?\s': 'quan ',
    r'\bh\.?\s': 'huyen ',
    r'\btp\.?\s': 'thanh pho ',
    r'\bt\.?\s': 'tinh ',
    r'\btx\.?\s': 'thi xa ',
    r'\btt\.?\s': 'thi tran ',
    r'\bd\.?\s': 'duong ',
    r'duong\b': 'duong',
    r'pho\b': 'pho',
    r'ngo\b': 'ngo',
    r'hem\b': 'hem',
    r'so\s+(\d)': r'\1',
}

def normalize_v2(s):
    """Normalize v2 - expand abbreviations"""
    if pd.isna(s): return ""
    s = str(s).lower()
    s = unidecode(s)
    # expand abbreviations BEFORE removing punctuation
    for pattern, replacement in ABBREV_MAP.items():
        s = re.sub(pattern, replacement, s)
    s = re.sub(r'[\W_]+', ' ', s)
    return " ".join(s.split())

def extract_key_components(s_normalized):
    """Extract numeric parts (street numbers, house numbers) - often most unique"""
    nums = re.findall(r'\d+', s_normalized)
    return set(nums)

# ==== RUN MATCHING WITH DIFFERENT METHODS ====
print("\n\n====================================================")
print("=== PHÂN TÍCH TỈ LỆ KHỚP VỚI CÁC PHƯƠNG PHÁP ===")
print("====================================================\n")

methods = [
    ("token_sort_ratio + normalize_v1", fuzz.token_sort_ratio, normalize_v1),
    ("token_set_ratio  + normalize_v1", fuzz.token_set_ratio,  normalize_v1),
    ("WRatio           + normalize_v1", fuzz.WRatio,           normalize_v1),
    ("token_sort_ratio + normalize_v2", fuzz.token_sort_ratio, normalize_v2),
    ("token_set_ratio  + normalize_v2", fuzz.token_set_ratio,  normalize_v2),
    ("WRatio           + normalize_v2", fuzz.WRatio,           normalize_v2),
]

df1_addrs = df1['Địa chỉ'].tolist()
df2_addrs = df2['Thông tin MB đang thuê'].tolist()

for label, scorer, norm_fn in methods:
    n1 = [norm_fn(a) for a in df1_addrs]
    n2 = [norm_fn(a) for a in df2_addrs]
    
    matched = 0
    threshold = 80
    for a in n1:
        result = process.extractOne(a, n2, scorer=scorer)
        if result and result[1] >= threshold:
            matched += 1
    
    pct = matched / len(n1) * 100 if n1 else 0
    print(f"  [{label}] => {matched}/{len(n1)} ({pct:.1f}%) khớp ở ngưỡng {threshold}%")

# ==== SHOW UNMATCHED SAMPLES ====
print("\n\n====================================================")
print("=== CÁC TRƯỜNG HỢP KHÔNG KHỚP (Phương pháp tốt nhất) ===")
print("====================================================\n")

n1 = [normalize_v2(a) for a in df1_addrs]
n2 = [normalize_v2(a) for a in df2_addrs]

unmatched = []
for i, (orig, norm) in enumerate(zip(df1_addrs, n1)):
    result = process.extractOne(norm, n2, scorer=fuzz.token_set_ratio)
    score = result[1] if result else 0
    best_idx = result[2] if result else None
    if score < 80:
        unmatched.append({
            'file1_addr': orig,
            'best_score': score,
            'best_match_file2': df2_addrs[best_idx] if best_idx is not None else None
        })

print(f"Số dòng KHÔNG khớp: {len(unmatched)}/{len(n1)}")
print("\n--- 15 trường hợp không khớp (kèm best-match) ---")
for item in unmatched[:15]:
    print(f"\n  FILE1: {item['file1_addr']}")
    print(f"  SCORE: {item['best_score']}%")
    print(f"  BEST MATCH FILE2: {item['best_match_file2']}")
    print("  " + "-"*60)

# ==== CHECK IF STORE CODE COULD HELP ====
print("\n\n====================================================")
print("=== PHÂN TÍCH CÁC TRƯỜNG KHÁC CÓ THỂ DÙNG ĐỂ GHÉP ===")
print("====================================================\n")
print("FILE 1 columns:", df1.columns.tolist())
print("\nFILE 2 columns:", df2.columns.tolist())

if 'Mã MB' in df2.columns and 'Store code' in df1.columns:
    print("\n=> Cả 2 file đều có mã cửa hàng! Có thể ghép chính xác 100% qua 'Store code' / 'Mã MB'")
    # Check overlap
    codes1 = set(df1['Store code'].dropna().astype(str).str.upper())
    codes2 = set(df2['Mã MB'].dropna().astype(str).str.upper())
    overlap = codes1 & codes2
    print(f"  Số mã trong File 1: {len(codes1)}")
    print(f"  Số mã trong File 2: {len(codes2)}")
    print(f"  Số mã TRÙNG nhau: {len(overlap)} ({len(overlap)/len(codes1)*100:.1f}%)")
    print(f"  Mẫu mã trùng: {list(overlap)[:10]}")
