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
# 1. Tại sao WRatio = 100%? Vì score ngưỡng quá thấp -> kiểm tra score thực tế
# =====================================================================
def normalize(s):
    if pd.isna(s): return ""
    s = str(s).lower()
    s = unidecode(s)
    s = re.sub(r'[\W_]+', ' ', s)
    return " ".join(s.split())

n1 = [normalize(a) for a in df1['Địa chỉ']]
n2 = [normalize(a) for a in df2['Thông tin MB đang thuê']]

print("=== PHÂN PHỐI SCORE (WRatio) - để phát hiện ngưỡng thực ===")
import collections
buckets = collections.Counter()
for a in n1:
    result = process.extractOne(a, n2, scorer=fuzz.WRatio)
    if result:
        score = result[1]
        bucket = (int(score)//5)*5
        buckets[bucket] += 1
for k in sorted(buckets.keys()):
    bar = "█" * (buckets[k] // 2)
    print(f"  {k:3d}-{k+4}: {buckets[k]:3d} {bar}")

# =====================================================================
# 2. Xem Mã MB vs Store code - format thực tế
# =====================================================================
print("\n=== MÃ MB (File 2) - 20 mẫu ===")
print(df2['Mã MB'].dropna().head(20).tolist())

print("\n=== Store code (File 1) - 20 mẫu ===")
print(df1['Store code'].dropna().head(20).tolist())

# Kiểm tra pattern - có thể prefix/suffix khác nhau không?
codes1 = df1['Store code'].dropna().astype(str).str.strip().str.upper()
codes2 = df2['Mã MB'].dropna().astype(str).str.strip().str.upper()

# Thử loại bỏ prefix chữ cái ở đầu
def strip_prefix(s):
    return re.sub(r'^[A-Z]+', '', s).strip()

sc1_stripped = codes1.apply(strip_prefix)
sc2_stripped = codes2.apply(strip_prefix)

overlap_numeric = set(sc1_stripped) & set(sc2_stripped)
print(f"\n=> Nếu bỏ prefix chữ cái: overlap = {len(overlap_numeric)}")
print("   Mẫu overlap:", list(overlap_numeric)[:10])

# =====================================================================
# 3. Xem chi tiết các cặp mà token_set_ratio KHỚP (để hiểu cặp đúng trông như thế nào)
# =====================================================================
print("\n=== CÁC CẶP ĐÃ KHỚP TỐT (score >= 90) - token_set_ratio ===")
count = 0
for i, (orig1, a) in enumerate(zip(df1['Địa chỉ'], n1)):
    result = process.extractOne(a, n2, scorer=fuzz.token_set_ratio)
    if result and result[1] >= 90:
        j = result[2]
        print(f"\n  FILE1: {orig1}")
        print(f"  FILE2: {df2['Thông tin MB đang thuê'].iloc[j]}")
        print(f"  SCORE: {result[1]:.1f}%")
        count += 1
        if count >= 10:
            break

# =====================================================================
# 4. Thử xem địa chỉ trong file 2 có phần trong ngoặc "(Địa chỉ đầu vào: ...)"
# =====================================================================
print("\n\n=== FILE 2 - Thông tin MB đang thuê: PHÂN TÍCH CẤU TRÚC ===")
has_bracket = 0
for v in df2['Thông tin MB đang thuê']:
    if '(' in str(v) and 'a ch' in str(v).lower():
        has_bracket += 1
print(f"  Số dòng có '(Địa chỉ đầu vào:...)': {has_bracket}/{len(df2)}")

# Extract phần trong ngoặc làm địa chỉ thứ 2 để so khớp
def extract_inner_address(s):
    """Lấy địa chỉ trong ngoặc nếu có"""
    if pd.isna(s): return None
    m = re.search(r'\((?:Địa chỉ (?:đầu vào|ban đầu|chủ|gốc)|Đầu vào)[:\s]*([^)]+)\)', str(s), re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return None

df2['addr_inner'] = df2['Thông tin MB đang thuê'].apply(extract_inner_address)
has_inner = df2['addr_inner'].notna().sum()
print(f"  Số dòng tách được địa chỉ trong ngoặc: {has_inner}")
print("\n  Mẫu địa chỉ trong ngoặc:")
for v in df2['addr_inner'].dropna().head(10):
    print(f"    {v}")

# =====================================================================
# 5. So khớp dùng địa chỉ trong ngoặc (inner address)
# =====================================================================
print("\n=== THỬ MATCH DÙNG ĐỊA CHỈ TRONG NGOẶC (inner) ===")
n2_inner = [normalize(v) if v else "" for v in df2['addr_inner']]
n2_outer = n2

matched_inner = 0
matched_either = 0
for a in n1:
    # Try outer first
    r_out = process.extractOne(a, n2_outer, scorer=fuzz.token_set_ratio)
    r_inn = process.extractOne(a, [x for x in n2_inner if x], scorer=fuzz.token_set_ratio)
    
    score_out = r_out[1] if r_out else 0
    score_inn = r_inn[1] if r_inn else 0
    
    if score_inn >= 80:
        matched_inner += 1
    if max(score_out, score_inn) >= 80:
        matched_either += 1

print(f"  Chỉ dùng địa chỉ gốc (outer): {sum(1 for a in n1 if (process.extractOne(a, n2_outer, scorer=fuzz.token_set_ratio) or (None,0))[1] >= 80)}/{ len(n1)}")
print(f"  Chỉ dùng địa chỉ trong ngoặc (inner): {matched_inner}/{len(n1)}")
print(f"  Kết hợp cả 2 (outer OR inner): {matched_either}/{len(n1)}")
