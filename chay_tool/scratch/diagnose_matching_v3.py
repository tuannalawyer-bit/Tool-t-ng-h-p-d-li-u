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

def normalize(s):
    if pd.isna(s): return ""
    s = str(s).lower()
    s = unidecode(s)
    s = re.sub(r'[\W_]+', ' ', s)
    return " ".join(s.split())

# =====================================================================
# 1. Hiểu rõ cấu trúc thực tế của dữ liệu trong ngoặc
# =====================================================================
print("=== XEMM 10 GIÁ TRỊ ĐẦY ĐỦ CỦA 'Thông tin MB đang thuê' (File 2) ===")
for i, v in enumerate(df2['Thông tin MB đang thuê'].head(10)):
    print(f"\n  [{i}] RAW: {repr(v)}")

print("\n\n=== TÌM PATTERN NGOẶC ĐƠN TRONG FILE 2 ===")
for i, v in enumerate(df2['Thông tin MB đang thuê']):
    s = str(v)
    if '(' in s:
        print(f"  [{i}] {s[:200]}")
        if i > 20:
            break

# =====================================================================
# 2. Chiến lược mới: Tách phần cuối địa chỉ (Tỉnh/Huyện/Xã) làm key
# =====================================================================
print("\n=== PHÂN TÍCH CÁC THÀNH PHẦN ĐỊA CHỈ ===")
def extract_tinh(addr):
    """Trích xuất tên tỉnh từ địa chỉ"""
    addr_n = normalize(addr)
    # Pattern: last token after "tinh/tp/thanh pho"
    m = re.search(r'(?:tinh|thanh pho|tp)\s+(\w+(?:\s+\w+)?)\s*$', addr_n)
    if m:
        return m.group(1)
    parts = addr_n.split()
    return parts[-1] if parts else ""

def extract_last_components(addr, n=3):
    """Lấy n thành phần cuối của địa chỉ sau khi tách bằng dấu phẩy"""
    if pd.isna(addr): return []
    parts = [p.strip() for p in str(addr).split(',')]
    return parts[-n:] if len(parts) >= n else parts

print("\n  File 1 - 5 địa chỉ và các thành phần cuối:")
for v in df1['Địa chỉ'].head(5):
    parts = extract_last_components(v, 3)
    print(f"    ADDR: {v}")
    print(f"    PARTS: {parts}\n")

print("\n  File 2 - 5 địa chỉ và các thành phần cuối:")
for v in df2['Thông tin MB đang thuê'].head(5):
    parts = extract_last_components(v, 3)
    print(f"    ADDR: {v}")
    print(f"    PARTS: {parts}\n")

# =====================================================================
# 3. Chiến lược: Dùng "Tỉnh" làm filter trước, sau đó fuzzy trong nhóm tỉnh
# =====================================================================
print("\n=== TEST CHIẾN LƯỢC: NHÓM THEO TỈNH + FUZZY TRONG NHÓM ===")

# Lấy tỉnh từ File 1 (đã có cột sẵn)
print("  Columns Tỉnh trong File 1:", [c for c in df1.columns if 'tỉnh' in c.lower() or 'tinh' in c.lower()])
print("  Cột Tỉnh/TP/Quận - sample:", df1['Tỉnh/TP/Quận'].head(10).tolist())

# Lấy tỉnh từ File 2
print("  Cột Tỉnh trong File 2 - sample:", df2['Tỉnh'].head(10).tolist())

# Normalize tỉnh để so khớp
tinh1 = df1['Tỉnh/TP/Quận'].apply(lambda x: normalize(str(x).split('/')[0]))
tinh2 = df2['Tỉnh'].apply(normalize)

print("\n  Tỉnh unique File 1:", sorted(tinh1.unique())[:15])
print("\n  Tỉnh unique File 2:", sorted(tinh2.unique())[:15])

# Đếm tỉnh trùng nhau
tinh1_set = set(tinh1.unique())
tinh2_set = set(tinh2.unique())
print(f"\n  Số tỉnh trong File 1: {len(tinh1_set)}")
print(f"  Số tỉnh trong File 2: {len(tinh2_set)}")
print(f"  Số tỉnh trùng nhau: {len(tinh1_set & tinh2_set)}")
print(f"  Tỉnh trùng: {sorted(tinh1_set & tinh2_set)}")

# Test chiến lược: filter theo tỉnh, rồi fuzzy trong nhóm
matched_tinh_strategy = 0
total = 0
for idx1, row1 in df1.iterrows():
    tinh_val = normalize(str(row1['Tỉnh/TP/Quận']).split('/')[0])
    addr1_n = normalize(row1['Địa chỉ'])
    
    # Lấy tập con df2 cùng tỉnh
    df2_subset = df2[tinh2 == tinh_val]
    
    if len(df2_subset) == 0:
        continue
    
    total += 1
    n2_sub = [normalize(v) for v in df2_subset['Thông tin MB đang thuê']]
    
    result = process.extractOne(addr1_n, n2_sub, scorer=fuzz.token_set_ratio)
    if result and result[1] >= 75:
        matched_tinh_strategy += 1

print(f"\n=> Chiến lược lọc theo tỉnh + fuzzy 75%: {matched_tinh_strategy}/{total} ({matched_tinh_strategy/total*100:.1f}% của nhóm có tỉnh khớp)")
print(f"   (Tổng file 1: {len(df1)} dòng)")
