import pandas as pd
import sys, io, re
from rapidfuzz import fuzz, process

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

path1 = r"D:\OneDrive - WIN\Desktop\công việc thực hiện\Tháng 5\Chuyên đề xây dựng mở mới\danh sach ky hop dong.xlsx"
path2 = r"D:\OneDrive - WIN\Desktop\công việc thực hiện\Tháng 5\Chuyên đề xây dựng mở mới\form tool.xlsx"

df1 = pd.read_excel(path1)
df2 = pd.read_excel(path2, header=2)

print("=== PHÂN TÍCH GÓC NHÌN MỚI: TÌM KIẾM CÁC ĐIỂM NEO KHÁC NGOÀI ĐỊA CHỈ ===")

# 1. DIỆN TÍCH THUÊ
print("\n--- 1. Diện Tích Thuê (DTT) ---")
col_dtt_1 = 'Diện tích thuê\n(m2)'
col_dtt_2 = 'DTT'

if col_dtt_1 in df1.columns and col_dtt_2 in df2.columns:
    dtt_1_vals = df1[col_dtt_1].dropna().astype(str).str.replace(',', '.').apply(lambda x: re.sub(r'[^\d.]', '', x))
    dtt_2_vals = df2[col_dtt_2].dropna().astype(str).str.replace(',', '.').apply(lambda x: re.sub(r'[^\d.]', '', x))
    
    # Convert to float for comparison
    dtt_1_vals = pd.to_numeric(dtt_1_vals, errors='coerce').dropna()
    dtt_2_vals = pd.to_numeric(dtt_2_vals, errors='coerce').dropna()
    
    overlap_dtt = set(dtt_1_vals).intersection(set(dtt_2_vals))
    print(f"Số lượng DTT duy nhất File 1: {len(set(dtt_1_vals))}")
    print(f"Số lượng DTT duy nhất File 2: {len(set(dtt_2_vals))}")
    print(f"Số lượng DTT trùng nhau: {len(overlap_dtt)}")
    print(f"Mẫu DTT trùng: {list(overlap_dtt)[:10]}")
    
    # How unique is DTT? If a DTT value is unique in both files, it's a strong anchor!
    dtt_1_counts = dtt_1_vals.value_counts()
    dtt_2_counts = dtt_2_vals.value_counts()
    
    unique_dtt_1 = set(dtt_1_counts[dtt_1_counts == 1].index)
    unique_dtt_2 = set(dtt_2_counts[dtt_2_counts == 1].index)
    unique_overlap = unique_dtt_1.intersection(unique_dtt_2)
    print(f"Số lượng DTT ĐỘC NHẤT ở cả 2 file (Có thể dùng làm key 1-1): {len(unique_overlap)}")

# 2. SỐ ĐIỆN THOẠI CHỦ NHÀ
print("\n--- 2. Số Điện Thoại (SĐT) ---")
def extract_phones(text):
    if pd.isna(text): return []
    # Find sequences of 9 to 11 digits
    phones = re.findall(r'\b(?:0|\+84)[0-9]{8,10}\b', str(text).replace('.', '').replace(' ', '').replace('-', ''))
    return phones

phones_1 = set()
for p in df1.get('Số điện thoại', []):
    phones_1.update(extract_phones(p))

phones_2 = set()
for p in df2.get('Thông tin BCT', []):
    phones_2.update(extract_phones(p))

overlap_phones = phones_1.intersection(phones_2)
print(f"Số SĐT tìm thấy File 1: {len(phones_1)}")
print(f"Số SĐT tìm thấy File 2: {len(phones_2)}")
print(f"Số SĐT trùng nhau: {len(overlap_phones)}")
if overlap_phones:
    print(f"Mẫu SĐT trùng: {list(overlap_phones)[:5]}")

# 3. NHÂN SỰ PHỤ TRÁCH
print("\n--- 3. Nhân sự phụ trách ---")
col_ns_1 = 'TF phụ trách'
col_ns_2 = 'CV TKMB/PTML'

if col_ns_1 in df1.columns and col_ns_2 in df2.columns:
    ns_1 = set(df1[col_ns_1].dropna().astype(str).str.lower().str.strip())
    ns_2 = set(df2[col_ns_2].dropna().astype(str).str.lower().str.strip())
    
    overlap_ns = ns_1.intersection(ns_2)
    print(f"Số nhân sự File 1: {len(ns_1)}")
    print(f"Số nhân sự File 2: {len(ns_2)}")
    print(f"Số nhân sự trùng: {len(overlap_ns)}")

# 4. TÌM KIẾM TRONG MÃ MẶT BẰNG
print("\n--- 4. Phân tích Store Code vs Mã MB chi tiết hơn ---")
codes1 = df1.get('Store code', pd.Series()).dropna().astype(str).str.strip().str.upper()
codes2 = df2.get('Mã MB', pd.Series()).dropna().astype(str).str.strip().str.upper()
# Is it possible that "Mã MB" in file 2 appears ANYWHERE in file 1 (e.g. in Ghi chú)?
found_in_notes = 0
for code2 in codes2:
    # check if code2 is in any column of df1
    mask = df1.astype(str).apply(lambda x: x.str.contains(code2, case=False, na=False)).any(axis=1)
    if mask.any():
        found_in_notes += 1
print(f"Số Mã MB của File 2 xuất hiện ở BẤT KỲ ĐÂU trong File 1: {found_in_notes}")

# 5. CHIỀU DÀI MẶT TIỀN vs GIÁ THUÊ (Correlations?)
# Not direct keys, but let's check values
