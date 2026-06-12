import pandas as pd
import sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
PATH1 = r"D:\OneDrive - WIN\Desktop\công việc thực hiện\Tháng 5\Chuyên đề xây dựng mở mới\danh sach ky hop dong.xlsx"
df1 = pd.read_excel(PATH1)

row = df1[df1['Store code'].astype(str).str.contains('2BPW', na=False)]
print("ROW IN FILE 1:")
for col in row.columns:
    print(f"{col}: {row[col].values[0] if len(row) > 0 else 'NOT FOUND'}")
