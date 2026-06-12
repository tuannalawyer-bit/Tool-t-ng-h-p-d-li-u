import pandas as pd
import sys
import io

# Force UTF-8 output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def inspect_file(path):
    print(f"\n--- Inspecting {path} ---")
    try:
        df = pd.read_excel(path, nrows=5)
        print("Columns:", df.columns.tolist())
        print("Head:\n", df.head())
    except Exception as e:
        print(f"Error reading {path}: {e}")

path1 = r"D:\OneDrive - WIN\Desktop\công việc thực hiện\Tháng 5\Chuyên đề xây dựng mở mới\danh sach ky hop dong.xlsx"
path2 = r"D:\OneDrive - WIN\Desktop\công việc thực hiện\Tháng 5\Chuyên đề xây dựng mở mới\form tool.xlsx"

inspect_file(path1)
inspect_file(path2)
