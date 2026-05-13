import openpyxl
import os
import json

path = r"D:\chạy tool\chạy tool\form tool.xlsx"
data = []

if os.path.exists(path):
    try:
        wb = openpyxl.load_workbook(path)
        ws = wb['01. Thẩm định giá & HSPL']
        
        headers = [str(ws.cell(row=3, column=c).value).strip() for c in range(1, 20)]
        
        # Scan rows from DATA_START_ROW to max_row
        for r in range(4, ws.max_row + 1):
            row_ma = ws.cell(row=r, column=5).value
            if not row_ma: continue
            
            missing_cols = []
            for c in range(1, 20):
                cell = ws.cell(row=r, column=c)
                # Check for solid yellow fill pattern
                if cell.fill and cell.fill.fgColor and cell.fill.fgColor.rgb == '00FFFF00':
                    col_name = headers[c-1] if c-1 < len(headers) else f"Col {c}"
                    missing_cols.append(col_name)
            
            if missing_cols:
                data.append({
                    "row": r,
                    "ma_mb": str(row_ma),
                    "missing_fields": missing_cols
                })
                
        output_json = r"d:\Dự án AI\chay_tool\yellow_diagnosis.json"
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        with open(r"d:\Dự án AI\chay_tool\yellow_error.txt", 'w') as ef: ef.write(str(e))
