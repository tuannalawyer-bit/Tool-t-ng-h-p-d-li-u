import openpyxl
import json
import os

wb = openpyxl.load_workbook(r'D:\chạy tool\chạy tool\form tool.xlsx')
ws = wb['01. Thẩm định giá & HSPL']

def get_r(idx):
    return [str(ws.cell(row=idx, column=c).value) for c in range(1, 20)]

data = {
    "HEADERS_R3": get_r(3),
    "ROW_4": get_r(4),
    "ROW_83": get_r(83)
}

with open(r'd:\Dự án AI\chay_tool\diagnosis_out.txt', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4, ensure_ascii=False)
