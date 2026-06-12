import pandas as pd
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

path2 = r"D:\OneDrive - WIN\Desktop\công việc thực hiện\Tháng 5\Chuyên đề xây dựng mở mới\form tool.xlsx"

df2 = pd.read_excel(path2, header=None)
print("Row 2 (header?):")
print(df2.iloc[2].tolist())
print("\nRow 3 (data?):")
print(df2.iloc[3].tolist())
