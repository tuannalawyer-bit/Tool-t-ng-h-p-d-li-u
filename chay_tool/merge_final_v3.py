"""
merge_final_v3.py
-----------------
Ghép 2 file Excel theo địa chỉ - PHIÊN BẢN SIÊU CHẶT CHẼ CÓ ĐIỀN GIÁ TRỊ GẦN NHẤT (V3.1)
Mục tiêu:
1. Giữ nguyên phân loại Exact/Fuzzy/No Match cực kỳ chặt chẽ của V3.
2. Với dòng NO_MATCH, VẪN ĐIỀN dữ liệu của ứng viên có điểm cao nhất từ File 2 để tiện tra cứu thủ công.
"""

import pandas as pd
import sys, io, re, unicodedata
from rapidfuzz import fuzz, process

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PATH1 = r"D:\OneDrive - WIN\Desktop\công việc thực hiện\Tháng 5\Chuyên đề xây dựng mở mới\danh sach ky hop dong.xlsx"
PATH2 = r"D:\OneDrive - WIN\Desktop\công việc thực hiện\Tháng 5\Chuyên đề xây dựng mở mới\form tool.xlsx"
OUTPUT = r"D:\OneDrive - WIN\Desktop\công việc thực hiện\Tháng 5\Chuyên đề xây dựng mở mới\merged_result_v3_ultra_strict_filled.xlsx"

TINH_THRESHOLD = 85
ADDR_THRESHOLD = 82
EXACT_THRESHOLD = 92

ADMIN_WORDS_ACCENTS = [
    r'\bthành phố\b', r'\btp\b', r'\btỉnh\b', r'\bquận\b', r'\bhuyện\b', r'\bthị xã\b', r'\bthị trấn\b', r'\btt\b',
    r'\bphường\b', r'\bxã\b', r'\bthôn\b', r'\bxóm\b', r'\btổ dân phố\b', r'\btdp\b', r'\btổ\b', r'\bkhu vực\b',
    r'\bkhu\b', r'\bấp\b', r'\bđường\b', r'\bphố\b', r'\bngõ\b', r'\bhẻm\b', r'\bsố\b', r'\btòa nhà\b', r'\bchợ\b',
    r'\bkđt\b', r'\bkhu đô thị\b', r'\bđ\b', r'\bp\b', r'\bq\b', r'\bt\b', r'\bh\b', r'\bx\b', r'\btb\b', r'\btbd\b', r'\btđ\b'
]

def normalize_tinh(s):
    if not s or s != s: return ""
    s = str(s).strip()
    s = unicodedata.normalize('NFC', s).lower()
    s = re.sub(r'^(tp\.|t\.|tỉnh|thành phố|tphcm)\s*', '', s)
    s = s.split('/')[0].strip()
    return s

def normalize_core_addr(s):
    if not s or s != s: return ""
    s = str(s).lower()
    s = unicodedata.normalize('NFC', s)
    s = re.sub(r'[\W_]+', ' ', s)
    for word in ADMIN_WORDS_ACCENTS:
        s = re.sub(word, ' ', s)
    return " ".join(s.split())

def extract_outer_addr(s):
    if not s or s != s: return ""
    s = str(s)
    s = re.sub(r'\([^)]*\)', '', s)
    return normalize_core_addr(s)

def extract_inner_addr(s):
    if not s or s != s: return ""
    s = str(s)
    matches = re.findall(r'\(([^)]+)\)', s)
    for inner in matches:
        if len(inner) < 6: continue
        inner = re.sub(r'^(?:địa chỉ (?:đầu vào|ban đầu)|đầu vào)[:\s]*', '', inner, flags=re.IGNORECASE)
        return normalize_core_addr(inner)
    return ""

print("Đang tải dữ liệu...")
df1 = pd.read_excel(PATH1)
df2 = pd.read_excel(PATH2, header=2)

df1_work = df1.dropna(subset=['Địa chỉ']).reset_index(drop=True)
df2_work = df2.dropna(subset=['Thông tin MB đang thuê']).reset_index(drop=True)

print(f"File 1 (Ký HĐ): {len(df1_work)} dòng có địa chỉ")
print(f"File 2 (Form Tool): {len(df2_work)} dòng có địa chỉ")

print("Đang chuẩn hóa dữ liệu...")
tinh1_n = df1_work['Tỉnh/TP/Quận'].apply(normalize_tinh)
tinh2_n = df2_work['Tỉnh'].apply(normalize_tinh)

addr1_n = df1_work['Địa chỉ'].apply(normalize_core_addr)
addr2_outer_n = df2_work['Thông tin MB đang thuê'].apply(extract_outer_addr)
addr2_inner_n = df2_work['Thông tin MB đang thuê'].apply(extract_inner_addr)

tinh2_unique = [t for t in tinh2_n.unique() if t]
addr2_outer_list = addr2_outer_n.tolist()
addr2_inner_list = addr2_inner_n.tolist()

match_df2_idx   = []
match_scores    = []
match_statuses  = []
match_methods   = []

print("Bắt đầu ghép cặp tìm ứng viên tốt nhất...")
for idx1 in range(len(df1_work)):
    t1 = tinh1_n.iloc[idx1]
    a1 = addr1_n.iloc[idx1]

    best_df2_idx = None
    best_score = -1
    method = "NO_MATCH"

    if len(a1.strip()) < 4:
        match_df2_idx.append(None)
        match_scores.append(0)
        match_statuses.append("NO_MATCH")
        match_methods.append("SHORT_ADDR")
        continue

    # BƯỚC 1: KHỚP THEO TỈNH
    tinh_match = process.extractOne(t1, tinh2_unique, scorer=fuzz.ratio)
    search_indices = []
    
    if tinh_match and tinh_match[1] >= TINH_THRESHOLD:
        matched_tinh_val = tinh_match[0]
        search_indices = tinh2_n[tinh2_n == matched_tinh_val].index.tolist()
        is_global_search = False
    else:
        # Nếu không khớp tỉnh nào, tìm kiếm trên toàn bộ dữ liệu quốc gia
        search_indices = list(range(len(df2_work)))
        is_global_search = True

    # Duyệt và chấm điểm cho tất cả ứng viên trong phạm vi tìm kiếm
    for j in search_indices:
        out_str = addr2_outer_list[j]
        inn_str = addr2_inner_list[j]
        
        # Thử với Outer
        score_out_set = fuzz.token_set_ratio(a1, out_str)
        score_out_sort = fuzz.token_sort_ratio(a1, out_str)
        blended_out = (score_out_set * 0.4) + (score_out_sort * 0.6)
        
        m_prefix = "NATION" if is_global_search else "TINH"
        
        if blended_out > best_score:
            best_df2_idx = j
            best_score = blended_out
            method = f"{m_prefix}+OUTER"
            
        # Thử với Inner (nếu có)
        if inn_str:
            score_inn_set = fuzz.token_set_ratio(a1, inn_str)
            score_inn_sort = fuzz.token_sort_ratio(a1, inn_str)
            blended_inn = (score_inn_set * 0.4) + (score_inn_sort * 0.6)
            if blended_inn > best_score:
                best_df2_idx = j
                best_score = blended_inn
                method = f"{m_prefix}+INNER"

    # PHÂN LOẠI THEO NGƯỠNG (GIỮ NGUYÊN LOGIC CỰC KỲ CHẶT CHẼ)
    if best_df2_idx is None:
        status = "NO_MATCH"
        best_score = 0
    elif best_score >= EXACT_THRESHOLD:
        status = "EXACT"
    elif best_score >= ADDR_THRESHOLD:
        status = "FUZZY"
    else:
        # Vẫn giữ nguyên nhãn NO_MATCH dù đã tìm ra ứng viên tốt nhất
        status = "NO_MATCH"

    match_df2_idx.append(best_df2_idx)
    match_scores.append(round(best_score, 1))
    match_statuses.append(status)
    match_methods.append(method)

# Thống kê
n_exact = match_statuses.count("EXACT")
n_fuzzy = match_statuses.count("FUZZY")
n_none  = match_statuses.count("NO_MATCH")
n_total = len(df1_work)

print(f"\n📊 THỐNG KÊ KẾT QUẢ GHÉP CẶP:")
print(f"   🟢 EXACT  (Điểm ≥{EXACT_THRESHOLD}%): {n_exact:3d} dòng ({n_exact/n_total*100:.1f}%)")
print(f"   🟡 FUZZY  ({ADDR_THRESHOLD}-{EXACT_THRESHOLD}%):      {n_fuzzy:3d} dòng ({n_fuzzy/n_total*100:.1f}%)")
print(f"   🔴 NO_MATCH (<{ADDR_THRESHOLD}%):      {n_none:3d} dòng ({n_none/n_total*100:.1f}%)")
print(f"   📌 Tất cả {n_none} dòng NO_MATCH giờ đều đã được điền ứng viên gần nhất phục vụ xem xét thủ công.")

# Nối dữ liệu
df1_work['_match_idx']    = match_df2_idx
df1_work['_match_score']  = match_scores
df1_work['_match_status'] = match_statuses
df1_work['_match_method'] = match_methods

df2_renamed = df2_work.copy()
df2_renamed.columns = [f"TĐG_{c}" for c in df2_work.columns]

df2_matched_rows = []
for idx, row_idx in enumerate(match_df2_idx):
    if row_idx is not None:
        df2_matched_rows.append(df2_renamed.iloc[row_idx].to_dict())
    else:
        df2_matched_rows.append({c: None for c in df2_renamed.columns})

df2_matched = pd.DataFrame(df2_matched_rows)
df2_matched.index = df1_work.index

final_merged = pd.concat([df1_work, df2_matched], axis=1)

final_merged = final_merged.rename(columns={
    '_match_score':  'MATCH_SCORE (%)',
    '_match_status': 'MATCH_STATUS',
    '_match_method': 'MATCH_METHOD',
})
final_merged = final_merged.drop(columns=['_match_idx'], errors='ignore')

# Lưu Excel bôi màu
with pd.ExcelWriter(OUTPUT, engine='openpyxl') as writer:
    final_merged.to_excel(writer, index=False, sheet_name='Kết quả ghép V3')
    ws = writer.sheets['Kết quả ghép V3']
    from openpyxl.styles import PatternFill
    
    fill_exact = PatternFill("solid", fgColor="C6EFCE") # Xanh lá
    fill_fuzzy = PatternFill("solid", fgColor="FFEB9C") # Vàng
    fill_none  = PatternFill("solid", fgColor="FFC7CE") # Đỏ nhạt
    
    status_col = final_merged.columns.get_loc('MATCH_STATUS') + 1
    
    for row_i, status in enumerate(match_statuses, start=2):
        fill = fill_exact if status == "EXACT" else (fill_fuzzy if status == "FUZZY" else fill_none)
        ws.cell(row=row_i, column=status_col).fill = fill

print(f"\n✅ Đã hoàn thành ghi đè file thành công!")
print(f"👉 {OUTPUT}")
