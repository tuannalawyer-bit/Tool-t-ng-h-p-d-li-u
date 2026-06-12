import pandas as pd
import sys, io, re
from rapidfuzz import fuzz, process
from unidecode import unidecode

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

path1 = r"D:\OneDrive - WIN\Desktop\công việc thực hiện\Tháng 5\Chuyên đề xây dựng mở mới\danh sach ky hop dong.xlsx"
path2 = r"D:\OneDrive - WIN\Desktop\công việc thực hiện\Tháng 5\Chuyên đề xây dựng mở mới\form tool.xlsx"

df1 = pd.read_excel(path1)
df2 = pd.read_excel(path2, header=2)
df1 = df1.dropna(subset=['Địa chỉ']).reset_index(drop=True)
df2 = df2.dropna(subset=['Thông tin MB đang thuê']).reset_index(drop=True)

# =====================================================================
# CHẨN ĐOÁN CHUẨN HÓA TỈNH:
# File 1: "TP. Hải Phòng", "T. Phú Thọ" -> cần normalize riêng
# File 2: "Thái Bình", "Nghệ An"         -> đã clean hơn
# =====================================================================

def normalize_tinh(s):
    """Normalize tên tỉnh - bỏ prefix TP./T./Tỉnh/Thành phố"""
    if pd.isna(s): return ""
    s = str(s).strip()
    s = re.sub(r'^(TP\.|T\.|Tỉnh|Thành phố|Thành Phố|TPHCM)\s*', '', s, flags=re.IGNORECASE)
    s = s.split('/')[0].strip()   # lấy phần trước dấu /
    s = unidecode(s).lower().strip()
    return s

def normalize_addr(s):
    if pd.isna(s): return ""
    # Xóa phần ngoặc "(Địa chỉ đầu vào: ...)" trước
    s = re.sub(r'\([^)]*\)', '', str(s))
    s = s.lower()
    s = unidecode(s)
    s = re.sub(r'[\W_]+', ' ', s)
    return " ".join(s.split())

def extract_inner_addr(s):
    """Tách địa chỉ trong ngoặc làm địa chỉ thứ 2"""
    if pd.isna(s): return ""
    m = re.search(r'\(([^)]+)\)', str(s))
    if m:
        inner = m.group(1)
        # Bỏ các prefix như "Địa chỉ đầu vào:", "Đầu vào:"
        inner = re.sub(r'^(?:Địa chỉ (?:đầu vào|ban đầu)|Đầu vào)[:\s]*', '', inner, flags=re.IGNORECASE)
        return normalize_addr(inner)
    return ""

# Normalize tỉnh
tinh1_n = df1['Tỉnh/TP/Quận'].apply(normalize_tinh)
tinh2_n = df2['Tỉnh'].apply(normalize_tinh)

# Normalize địa chỉ
addr1_n = df1['Địa chỉ'].apply(normalize_addr)
addr2_outer_n = df2['Thông tin MB đang thuê'].apply(normalize_addr)  # bỏ ngoặc
addr2_inner_n = df2['Thông tin MB đang thuê'].apply(extract_inner_addr)  # lấy ngoặc

# =====================================================================
# CHIẾN LƯỢC MỚI:
# 1. Match tỉnh (fuzzy 85%) để lọc nhóm
# 2. Trong mỗi nhóm tỉnh: so khớp địa chỉ với SCORE MAX(outer, inner)
# 3. Nếu không tìm được nhóm tỉnh: so khớp toàn bộ
# =====================================================================

print("=== TEST CHIẾN LƯỢC: FUZZY TỈNH + DUAL-ADDRESS MATCHING ===\n")

# Kiểm tra: bao nhiêu tỉnh trong file 1 có thể khớp fuzzy với tỉnh file 2?
tinh2_list = tinh2_n.unique().tolist()

matched_in_tinh_group = 0
matched_global_fallback = 0
no_tinh_match = 0
total = len(df1)

TINH_THRESHOLD = 80
ADDR_THRESHOLD = 75

rows_debug = []

for idx1 in range(len(df1)):
    t1 = tinh1_n.iloc[idx1]
    a1 = addr1_n.iloc[idx1]
    orig1 = df1['Địa chỉ'].iloc[idx1]

    # Bước 1: Tìm tỉnh khớp nhất trong file 2
    best_tinh = process.extractOne(t1, tinh2_list, scorer=fuzz.ratio)
    
    if best_tinh and best_tinh[1] >= TINH_THRESHOLD:
        matched_tinh = best_tinh[0]
        # Lọc dòng trong df2 có tỉnh khớp
        df2_sub_idx = tinh2_n[tinh2_n == matched_tinh].index.tolist()
        
        n2_outer_sub = [addr2_outer_n.iloc[j] for j in df2_sub_idx]
        n2_inner_sub = [addr2_inner_n.iloc[j] for j in df2_sub_idx]
        
        # Score với outer address
        r_out = process.extractOne(a1, n2_outer_sub, scorer=fuzz.token_set_ratio)
        # Score với inner address (nếu có)
        n2_inner_nonempty = [(v, j) for j, v in zip(df2_sub_idx, n2_inner_sub) if v]
        r_inn = None
        if n2_inner_nonempty:
            r_inn = process.extractOne(a1, [v for v, _ in n2_inner_nonempty], scorer=fuzz.token_set_ratio)
        
        score_out = r_out[1] if r_out else 0
        score_inn = r_inn[1] if r_inn else 0
        best_score = max(score_out, score_inn)
        
        if best_score >= ADDR_THRESHOLD:
            matched_in_tinh_group += 1
            rows_debug.append({
                'type': 'TINH_MATCH', 'score': best_score,
                'file1': orig1, 'matched_tinh': matched_tinh,
                'file2': df2['Thông tin MB đang thuê'].iloc[df2_sub_idx[r_out[2]]] if score_out >= score_inn else None
            })
        else:
            # Fallback: tìm global
            r_global = process.extractOne(a1, addr2_outer_n.tolist(), scorer=fuzz.token_set_ratio)
            if r_global and r_global[1] >= ADDR_THRESHOLD:
                matched_global_fallback += 1
    else:
        no_tinh_match += 1
        # Global fallback
        r_global = process.extractOne(a1, addr2_outer_n.tolist(), scorer=fuzz.token_set_ratio)
        if r_global and r_global[1] >= ADDR_THRESHOLD:
            matched_global_fallback += 1

total_matched = matched_in_tinh_group + matched_global_fallback
print(f"  Tổng dòng File 1:            {total}")
print(f"  Khớp trong nhóm tỉnh:        {matched_in_tinh_group} ({matched_in_tinh_group/total*100:.1f}%)")
print(f"  Khớp qua global fallback:    {matched_global_fallback} ({matched_global_fallback/total*100:.1f}%)")
print(f"  Không tìm được tỉnh:         {no_tinh_match} ({no_tinh_match/total*100:.1f}%)")
print(f"  TỔNG KHỚP:                   {total_matched} ({total_matched/total*100:.1f}%)")

# Show debug samples
print("\n\n=== MẪU CÁC CẶP KHỚP TRONG NHÓM TỈNH ===")
for r in rows_debug[:10]:
    print(f"  FILE1: {r['file1']}")
    print(f"  FILE2: {r['file2']}")
    print(f"  SCORE: {r['score']:.1f}%  TỈNH: {r['matched_tinh']}")
    print("  " + "-"*60)
