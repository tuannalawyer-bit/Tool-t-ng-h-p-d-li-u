import pandas as pd
import sys

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)

path1 = r"D:\OneDrive - WIN\Desktop\công việc thực hiện\Tháng 5\Chuyên đề xây dựng mở mới\danh sach ky hop dong.xlsx"
path2 = r"D:\OneDrive - WIN\Desktop\công việc thực hiện\Tháng 5\Chuyên đề xây dựng mở mới\form tool.xlsx"

df1 = pd.read_excel(path1)
df2 = pd.read_excel(path2, header=2)

codes1 = df1.get('Store code', pd.Series()).dropna().astype(str).str.strip().str.upper()

print("=== TÌM STORE CODE CỦA FILE 1 TRONG FILE 2 ===")
found = 0
for code1 in codes1:
    if len(code1) < 3: continue # skip very short strings to avoid false positives
    for col in df2.columns:
        if df2[col].dtype == 'object':
            mask = df2[col].astype(str).str.contains(code1, case=False, na=False, regex=False)
            if mask.any():
                print(f"\nTìm thấy Store Code: {code1} ở cột: '{col}' trong File 2.")
                matching_rows = df2[mask]
                for idx, row in matching_rows.iterrows():
                    print(f"  Row {idx}: {row['Mã MB']} | {str(row[col])[:100]}...")
                found += 1

if found == 0:
    print("Không tìm thấy mã nào.")
