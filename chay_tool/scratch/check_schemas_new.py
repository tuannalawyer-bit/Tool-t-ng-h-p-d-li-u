import pandas as pd
import sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PATH1 = r"D:\OneDrive - WIN\Desktop\công việc thực hiện\Tháng 5\Chuyên đề xây dựng mở mới\danh sach ky hop dong.xlsx"
PATH2 = r"D:\OneDrive - WIN\Desktop\công việc thực hiện\Tháng 5\Chuyên đề xây dựng mở mới\form tool.xlsx"

print("--- CHECK SCHEMAS ---")
df1 = pd.read_excel(PATH1)
print("File 1 Columns:", list(df1.columns))
print("File 1 Data Size:", len(df1))

# Form tool has header at row 2 or something? Let's read a few rows to confirm
df2_raw = pd.read_excel(PATH2, nrows=10)
print("\nFile 2 raw rows to verify header:")
print(df2_raw.head(5))
