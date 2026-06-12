import pandas as pd
import sys, re
from rapidfuzz import fuzz, process
from unidecode import unidecode

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)

path1 = r"D:\OneDrive - WIN\Desktop\công việc thực hiện\Tháng 5\Chuyên đề xây dựng mở mới\danh sach ky hop dong.xlsx"
path2 = r"D:\OneDrive - WIN\Desktop\công việc thực hiện\Tháng 5\Chuyên đề xây dựng mở mới\form tool.xlsx"

df1 = pd.read_excel(path1)
df2 = pd.read_excel(path2, header=2)
df1 = df1.dropna(subset=['Địa chỉ']).reset_index(drop=True)
df2 = df2.dropna(subset=['Thông tin MB đang thuê']).reset_index(drop=True)

ADMIN_WORDS = [
    r'\bthanh pho\b', r'\btp\b', r'\btinh\b', r'\bquan\b', r'\bhuyen\b', r'\bthi xa\b', r'\bthi tran\b', r'\btt\b',
    r'\bphuong\b', r'\bxa\b', r'\bthon\b', r'\bxom\b', r'\bto dan pho\b', r'\btdp\b', r'\bto\b', r'\bkhu vuc\b',
    r'\bkhu\b', r'\bap\b', r'\bduong\b', r'\bpho\b', r'\bngo\b', r'\bhem\b', r'\bso\b', r'\btoa nha\b', r'\bcho\b',
    r'\bkdt\b', r'\bkhu do thi\b', r'\bd\b', r'\bp\b', r'\bq\b', r'\bt\b', r'\bh\b', r'\bx\b', r'\btb\b', r'\btbd\b', r'\btd\b'
]

def normalize_core_name(s):
    if pd.isna(s): return ""
    # Extract inner address if exists
    m = re.search(r'\(([^)]+)\)', str(s))
    if m:
        inner = m.group(1)
        s = re.sub(r'^(?:Địa chỉ (?:đầu vào|ban đầu)|Đầu vào)[:\s]*', '', inner, flags=re.IGNORECASE)
    else:
        # remove bracketed content
        s = re.sub(r'\([^)]*\)', '', str(s))
        
    s = s.lower()
    s = unidecode(s)
    # Remove numbers to see if it helps, OR keep them as they are unique identifiers? KEEP numbers for now.
    s = re.sub(r'[\W_]+', ' ', s)
    
    # Remove administrative words
    for word in ADMIN_WORDS:
        s = re.sub(word, ' ', s)
    
    return " ".join(s.split())

print("=== SO KHỚP CHỈ DÙNG TÊN LÕI (BỎ TỪ HÀNH CHÍNH) ===")
core1 = df1['Địa chỉ'].apply(normalize_core_name).tolist()
core2 = df2['Thông tin MB đang thuê'].apply(normalize_core_name).tolist()

print("\nMẫu Core 1:")
for i in range(5): print(f"  {df1['Địa chỉ'][i]}  -->  {core1[i]}")

print("\nMẫu Core 2:")
for i in range(5): print(f"  {df2['Thông tin MB đang thuê'][i]}  -->  {core2[i]}")

matched = 0
THRESHOLD = 80
for i, c1 in enumerate(core1):
    if not c1: continue
    result = process.extractOne(c1, core2, scorer=fuzz.token_set_ratio)
    if result and result[1] >= THRESHOLD:
        matched += 1

print(f"\nSố lượng khớp (Ngưỡng {THRESHOLD}%): {matched} / {len(core1)} ({matched/len(core1)*100:.1f}%)")
