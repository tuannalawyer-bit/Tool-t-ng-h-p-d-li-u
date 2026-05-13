import openpyxl
import os

paths = [
    r"D:\chạy tool\chạy tool\form tool.xlsx",
    r"d:\Dự án AI\chay_tool\form tool.xlsx"
]

for p in paths:
    if os.path.exists(p):
        try:
            wb = openpyxl.load_workbook(p)
            sheet_names = ["01. Thẩm định giá & HSPL"]
            for sn in sheet_names:
                if sn in wb.sheetnames:
                    ws = wb[sn]
                    ws.delete_cols(13)
            wb.save(p)
        except:
            pass
