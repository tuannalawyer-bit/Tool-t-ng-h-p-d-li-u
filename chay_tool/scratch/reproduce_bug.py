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

def normalize_addr(s):
    if pd.isna(s): return ""
    s = re.sub(r'\([^)]*\)', '', str(s))
    s = s.lower()
    s = unidecode(s)
    s = re.sub(r'[\W_]+', ' ', s)
    return " ".join(s.split())

a1_raw = df1['Địa chỉ'].iloc[46]
print(f"Row 46: {a1_raw}")
a1_raw = df1['Địa chỉ'].iloc[47]
print(f"Row 47: {a1_raw}")
a1_raw = df1['Địa chỉ'].iloc[61]
print(f"Row 61: {a1_raw}")

def print_match(raw_string):
    a1_norm = normalize_addr(raw_string)
    print(f"\nSearching for: {raw_string}")
    print(f"Normalized: {a1_norm}")

    addr2_outer_list = df2['Thông tin MB đang thuê'].apply(normalize_addr).tolist()

    r_global = process.extractOne(a1_norm, addr2_outer_list, scorer=fuzz.token_set_ratio)
    print(f"Global match: {r_global}")
    if r_global:
        print(f"Matched raw string in df2: {df2['Thông tin MB đang thuê'].iloc[r_global[2]]}")

print_match(df1['Địa chỉ'].iloc[47]) # Thửa đất 1094-1787...
print_match(df1['Địa chỉ'].iloc[61]) # Phố Lâm Hóa...
