import pandas as pd
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

path2 = r"D:\OneDrive - WIN\Desktop\công việc thực hiện\Tháng 5\Chuyên đề xây dựng mở mới\form tool.xlsx"

print(f"\n--- Detailed Inspecting {path2} ---")
df2 = pd.read_excel(path2, header=None)
print("First 5 rows (raw):")
print(df2.head(10))
