import openpyxl
import os

file1 = r"D:\OneDrive - WIN\Desktop\công việc thực hiện\Tháng 5\Chuyên đề xây dựng mở mới\danh sach ky hop dong.xlsx"
file2 = r"D:\OneDrive - WIN\Desktop\công việc thực hiện\Tháng 5\Chuyên đề xây dựng mở mới\04. Phụ lục 03_Phân tích dữ liệu mở mới.xlsx"

def analyze_excel(path, name):
    print(f"\n--- Analysis of {name} ---")
    if not os.path.exists(path):
        print("File does not exist")
        return
    try:
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        ws = wb.active
        print(f"Active Sheet: {ws.title}")
        
        # Read first 5 rows
        for i, row in enumerate(ws.iter_rows(max_row=10, values_only=True)):
            print(f"Row {i+1}: {row}")
            
    except Exception as e:
        print(f"Error reading {name}: {e}")

analyze_excel(file1, "File 1: Danh sach ky hop dong")
analyze_excel(file2, "File 2: Phu luc 03")

try:
    import pandas
    print("\nPandas is available")
except ImportError:
    print("\nPandas is NOT available")

try:
    from thefuzz import fuzz
    print("thefuzz is available")
except ImportError:
    print("thefuzz is NOT available")
