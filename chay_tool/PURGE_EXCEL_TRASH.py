import openpyxl
import os

path = r"D:\chạy tool\chạy tool\form tool.xlsx"

if os.path.exists(path):
    try:
        wb = openpyxl.load_workbook(path)
        ws = wb['01. Thẩm định giá & HSPL']
        
        # We want to keep row 4 to 82. Delete starting from 83.
        # Find the actual length
        max_r = ws.max_row
        if max_r >= 83:
            count_to_del = max_r - 83 + 1
            ws.delete_rows(83, amount=count_to_del)
            
        wb.save(path)
        # Also save in alternate path just to be perfectly persistent
        alt_path = r"d:\Dự án AI\chay_tool\form tool.xlsx"
        wb.save(alt_path)
    except Exception as e:
        pass
