import pandas as pd
import sys

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)

path1 = r"D:\OneDrive - WIN\Desktop\công việc thực hiện\Tháng 5\Chuyên đề xây dựng mở mới\danh sach ky hop dong.xlsx"
path2 = r"D:\OneDrive - WIN\Desktop\công việc thực hiện\Tháng 5\Chuyên đề xây dựng mở mới\form tool.xlsx"

df1 = pd.read_excel(path1)
df2 = pd.read_excel(path2, header=2)

codes2 = df2.get('Mã MB', pd.Series()).dropna().astype(str).str.strip().str.upper()

print("=== TÌM MÃ MB TRONG FILE 1 ===")
found = 0
for code2 in codes2:
    if len(code2) < 3: continue # skip very short strings to avoid false positives
    for col in df1.columns:
        # Check string columns
        if df1[col].dtype == 'object':
            mask = df1[col].astype(str).str.contains(code2, case=False, na=False, regex=False)
            if mask.any():
                print(f"\nTìm thấy Mã MB: {code2} ở cột: '{col}' trong File 1.")
                # Print the rows
                matching_rows = df1[mask]
                for idx, row in matching_rows.iterrows():
                    print(f"  Row {idx}: {row['Store code']} | {row['Địa chỉ'][:50]}... | {row[col]}")
                found += 1

if found == 0:
    print("Không tìm thấy mã nào (hoặc các mã tìm thấy trước đó là do Regex Match Groups Warning).")
