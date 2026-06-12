import openpyxl
import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

file1 = r"d:\Dự án AI\chay_tool\scratch\temp_file1.xlsx"
output_file = r"d:\Dự án AI\chay_tool\scratch\analysis_file1.txt"

def analyze_excel(path, name, f):
    f.write(f"\n--- Analysis of {name} ---\n")
    try:
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        ws = wb.active
        f.write(f"Active Sheet: {ws.title}\n")
        for i, row in enumerate(ws.iter_rows(max_row=15, values_only=True)):
            f.write(f"Row {i+1}: {str(row)}\n")
    except Exception as e:
        f.write(f"Error reading {name}: {str(e)}\n")

with open(output_file, "w", encoding="utf-8") as f:
    analyze_excel(file1, "File 1: Danh sach ky hop dong", f)
