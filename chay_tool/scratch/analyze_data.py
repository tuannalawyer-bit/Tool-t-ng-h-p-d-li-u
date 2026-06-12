import pandas as pd
import os

file1 = r"D:\OneDrive - WIN\Desktop\công việc thực hiện\Tháng 5\Chuyên đề xây dựng mở mới\danh sach ky hop dong.xlsx"
file2 = r"D:\OneDrive - WIN\Desktop\công việc thực hiện\Tháng 5\Chuyên đề xây dựng mở mới\04. Phụ lục 03_Phân tích dữ liệu mở mới.xlsx"

def analyze_file(path, name):
    print(f"\n--- Analysis of {name} ---")
    try:
        # Try to read the first few rows to see the structure
        df = pd.read_excel(path, nrows=10)
        print("Columns:", df.columns.tolist())
        print("First 5 rows:")
        print(df.head())
    except Exception as e:
        print(f"Error reading {name}: {e}")

analyze_file(file1, "File 1: Danh sach ky hop dong")
analyze_file(file2, "File 2: Phu luc 03")
