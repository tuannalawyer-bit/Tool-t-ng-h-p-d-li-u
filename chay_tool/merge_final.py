"""
merge_final.py
--------------
Ghép 2 file Excel theo địa chỉ dùng chiến lược tốt nhất:
  1. Normalize tỉnh (fuzzy 80%) để lọc nhóm
  2. token_set_ratio trên địa chỉ (ngoài + trong ngoặc)
  3. Fallback toàn file nếu không tìm được tỉnh
  4. Thêm cột match_score + match_status để review

Output: merged_result_final.xlsx
"""

import pandas as pd
import sys, io, re
from rapidfuzz import fuzz, process
from unidecode import unidecode

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PATH1 = r"D:\OneDrive - WIN\Desktop\công việc thực hiện\Tháng 5\Chuyên đề xây dựng mở mới\danh sach ky hop dong.xlsx"
PATH2 = r"D:\OneDrive - WIN\Desktop\công việc thực hiện\Tháng 5\Chuyên đề xây dựng mở mới\form tool.xlsx"
OUTPUT = r"D:\OneDrive - WIN\Desktop\công việc thực hiện\Tháng 5\Chuyên đề xây dựng mở mới\merged_result_final.xlsx"

TINH_THRESHOLD = 80   # Ngưỡng khớp tỉnh (%)
ADDR_THRESHOLD = 75   # Ngưỡng khớp địa chỉ (%)
EXACT_THRESHOLD = 90  # Ngưỡng "tin cậy cao" (%)

# -----------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------
def normalize_tinh(s):
    """Bỏ prefix TP./T./Tỉnh/Thành phố, lấy phần trước dấu /"""
    if pd.isna(s): return ""
    s = str(s).strip()
    s = re.sub(r'^(TP\.|T\.|Tỉnh|Thành phố|Thành Phố|TPHCM)\s*', '', s, flags=re.IGNORECASE)
    s = s.split('/')[0].strip()
    return unidecode(s).lower().strip()

def normalize_addr(s):
    """Normalize địa chỉ: bỏ ngoặc, lower, unidecode, loại ký tự đặc biệt"""
    if pd.isna(s): return ""
    s = re.sub(r'\([^)]*\)', '', str(s))   # bỏ phần trong ngoặc
    s = s.lower()
    s = unidecode(s)
    s = re.sub(r'[\W_]+', ' ', s)
    return " ".join(s.split())

def extract_inner_addr(s):
    """Lấy địa chỉ đầu vào trong ngoặc nếu có"""
    if pd.isna(s): return ""
    m = re.search(r'\(([^)]+)\)', str(s))
    if not m: return ""
    inner = m.group(1)
    inner = re.sub(r'^(?:Địa chỉ (?:đầu vào|ban đầu)|Đầu vào)[:\s]*', '', inner, flags=re.IGNORECASE)
    return normalize_addr(inner)

# -----------------------------------------------------------------------
# Load
# -----------------------------------------------------------------------
print("Đang tải dữ liệu...")
df1 = pd.read_excel(PATH1)
df2 = pd.read_excel(PATH2, header=2)

df1 = df1.dropna(subset=['Địa chỉ']).reset_index(drop=True)
df2 = df2.dropna(subset=['Thông tin MB đang thuê']).reset_index(drop=True)

print(f"  File 1: {len(df1)} dòng")
print(f"  File 2: {len(df2)} dòng")

# -----------------------------------------------------------------------
# Normalize
# -----------------------------------------------------------------------
print("Đang chuẩn hóa dữ liệu...")
tinh1_n = df1['Tỉnh/TP/Quận'].apply(normalize_tinh)
tinh2_n = df2['Tỉnh'].apply(normalize_tinh)
addr1_n = df1['Địa chỉ'].apply(normalize_addr)
addr2_outer_n = df2['Thông tin MB đang thuê'].apply(normalize_addr)
addr2_inner_n = df2['Thông tin MB đang thuê'].apply(extract_inner_addr)

tinh2_unique = tinh2_n.unique().tolist()

# -----------------------------------------------------------------------
# Matching
# -----------------------------------------------------------------------
print("Đang so khớp địa chỉ (chiến lược: Fuzzy tỉnh + dual-address)...")

match_df2_idx   = []   # index trong df2 được ghép
match_scores    = []   # score cuối cùng
match_statuses  = []   # EXACT / FUZZY / NO_MATCH
match_methods   = []   # mô tả cách ghép

addr2_outer_list = addr2_outer_n.tolist()
addr2_inner_list = addr2_inner_n.tolist()

for idx1 in range(len(df1)):
    t1 = tinh1_n.iloc[idx1]
    a1 = addr1_n.iloc[idx1]

    best_df2_idx = None
    best_score = 0
    method = "NO_MATCH"

    # Bước 1: Tìm tỉnh khớp nhất trong File 2
    tinh_match = process.extractOne(t1, tinh2_unique, scorer=fuzz.ratio)

    if tinh_match and tinh_match[1] >= TINH_THRESHOLD:
        matched_tinh_val = tinh_match[0]
        sub_idx = tinh2_n[tinh2_n == matched_tinh_val].index.tolist()

        # Bước 2: Trong nhóm tỉnh — so với outer address
        sub_outer = [addr2_outer_list[j] for j in sub_idx]
        r_out = process.extractOne(a1, sub_outer, scorer=fuzz.token_set_ratio)

        # So với inner address
        sub_inner_pairs = [(addr2_inner_list[j], j) for j in sub_idx if addr2_inner_list[j]]
        r_inn = None
        if sub_inner_pairs:
            r_inn = process.extractOne(a1, [v for v, _ in sub_inner_pairs], scorer=fuzz.token_set_ratio)

        score_out = r_out[1] if r_out else 0
        score_inn = r_inn[1] if r_inn else 0

        if score_out >= score_inn and score_out >= ADDR_THRESHOLD:
            best_df2_idx = sub_idx[r_out[2]]
            best_score = score_out
            method = f"TINH({matched_tinh_val})+OUTER"
        elif score_inn > score_out and score_inn >= ADDR_THRESHOLD:
            inner_j = sub_inner_pairs[r_inn[2]][1]
            best_df2_idx = inner_j
            best_score = score_inn
            method = f"TINH({matched_tinh_val})+INNER"

    # Bước 3: Fallback — tìm global nếu chưa khớp
    if best_df2_idx is None:
        r_global = process.extractOne(a1, addr2_outer_list, scorer=fuzz.token_set_ratio)
        if r_global and r_global[1] >= ADDR_THRESHOLD:
            best_df2_idx = r_global[2]
            best_score = r_global[1]
            method = "GLOBAL_FALLBACK"

    # Xác định status
    if best_df2_idx is None:
        status = "NO_MATCH"
        best_score = 0
    elif best_score >= EXACT_THRESHOLD:
        status = "EXACT"
    else:
        status = "FUZZY"

    match_df2_idx.append(best_df2_idx)
    match_scores.append(round(best_score, 1))
    match_statuses.append(status)
    match_methods.append(method)

# -----------------------------------------------------------------------
# Thống kê
# -----------------------------------------------------------------------
n_exact = match_statuses.count("EXACT")
n_fuzzy = match_statuses.count("FUZZY")
n_none  = match_statuses.count("NO_MATCH")
n_total = len(df1)

print(f"\n📊 Kết quả so khớp:")
print(f"   EXACT  (score ≥{EXACT_THRESHOLD}%): {n_exact:3d} dòng ({n_exact/n_total*100:.1f}%)")
print(f"   FUZZY  ({ADDR_THRESHOLD}-{EXACT_THRESHOLD}%):      {n_fuzzy:3d} dòng ({n_fuzzy/n_total*100:.1f}%)")
print(f"   NO_MATCH (<{ADDR_THRESHOLD}%):      {n_none:3d} dòng ({n_none/n_total*100:.1f}%)")
print(f"   TỔNG KHỚP:          {n_exact+n_fuzzy:3d} dòng ({(n_exact+n_fuzzy)/n_total*100:.1f}%)")

# -----------------------------------------------------------------------
# Merge và ghi file
# -----------------------------------------------------------------------
print("\nĐang ghép và ghi file kết quả...")

# Thêm cột helper
df1['_match_idx']    = match_df2_idx
df1['_match_score']  = match_scores
df1['_match_status'] = match_statuses
df1['_match_method'] = match_methods

# Prefix cột file 2 (trừ các cột chung)
df2_renamed = df2.copy()
df2_renamed.columns = [f"TĐG_{c}" if c not in ['STT'] else f"TĐG_{c}" for c in df2.columns]

# Ghép từng dòng có match
df2_matched_rows = []
for idx, row_idx in enumerate(match_df2_idx):
    if row_idx is not None:
        df2_matched_rows.append(df2_renamed.iloc[row_idx].to_dict())
    else:
        df2_matched_rows.append({c: None for c in df2_renamed.columns})

df2_matched = pd.DataFrame(df2_matched_rows)
df2_matched.index = df1.index

merged = pd.concat([df1, df2_matched], axis=1)

# Đổi tên cột helper cho dễ đọc
merged = merged.rename(columns={
    '_match_score':  'MATCH_SCORE (%)',
    '_match_status': 'MATCH_STATUS',
    '_match_method': 'MATCH_METHOD',
})
merged = merged.drop(columns=['_match_idx'], errors='ignore')

# Ghi ra Excel với màu cho dễ review
with pd.ExcelWriter(OUTPUT, engine='openpyxl') as writer:
    merged.to_excel(writer, index=False, sheet_name='Kết quả ghép')

    ws = writer.sheets['Kết quả ghép']
    from openpyxl.styles import PatternFill, Font

    # Màu theo status
    fill_exact = PatternFill("solid", fgColor="C6EFCE")   # xanh lá nhạt
    fill_fuzzy = PatternFill("solid", fgColor="FFEB9C")   # vàng nhạt
    fill_none  = PatternFill("solid", fgColor="FFC7CE")   # đỏ nhạt

    status_col = merged.columns.get_loc('MATCH_STATUS') + 1  # 1-indexed

    for row_i, status in enumerate(match_statuses, start=2):  # bỏ header
        fill = fill_exact if status == "EXACT" else (fill_fuzzy if status == "FUZZY" else fill_none)
        ws.cell(row=row_i, column=status_col).fill = fill

print(f"\n✅ File kết quả đã lưu tại:\n   {OUTPUT}")
print("\nGhú thích màu sắc:")
print("  🟢 Xanh lá (EXACT) : Khớp chắc chắn, score ≥ 90%")
print("  🟡 Vàng    (FUZZY) : Cần kiểm tra thủ công, score 75-89%")
print("  🔴 Đỏ      (NO_MATCH): Không tìm thấy cặp phù hợp")
