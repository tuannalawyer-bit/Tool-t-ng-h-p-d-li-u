import openpyxl
import os
import sys

# Set encoding for stdout to handle Vietnamese
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

file1 = r"D:\OneDrive - WIN\Desktop\công việc thực hiện\Tháng 5\Chuyên đề xây dựng mở mới\danh sach ky hop dong.xlsx"
file2 = r"D:\OneDrive - WIN\Desktop\công việc thực hiện\Tháng 5\Chuyên đề xây dựng mở mới\04. Phụ lục 03_Phân tích dữ liệu mở mới.xlsx"

output_file = r"d:\Dự án AI\chay_tool\scratch\analysis_results.txt"

def analyze_excel(path, name, f):
    f.write(f"\n--- Analysis of {name} ---\n")
    if not os.path.exists(path):
        f.write("File does not exist\n")
        return
    try:
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        ws = wb.active
        f.write(f"Active Sheet: {ws.title}\n")
        
        # Read first 15 rows to find header
        for i, row in enumerate(ws.iter_rows(max_row=15, values_only=True)):
            f.write(f"Row {i+1}: {str(row)}\n")
            
    except Exception as e:
        f.write(f"Error reading {name}: {str(e)}\n")

with open(output_file, "w", encoding="utf-8") as f:
    analyze_excel(file1, "File 1: Danh sach ky hop dong", f)
    analyze_excel(file2, "File 2: Phu luc 03", f)

    try:
        import pandas
        f.write("\nPandas is available\n")
    except ImportError:
        f.write("\nPandas is NOT available\n")

    try:
        from thefuzz import fuzz
        f.write("thefuzz is available\n")
    except ImportError:
        f.write("thefuzz is NOT available\n")
