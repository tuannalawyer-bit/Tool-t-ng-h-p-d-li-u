import os
import json
import sys
from pyxlsb import open_workbook as open_xlsb

# Force UTF-8 stdout for safety
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

file_path = "Tool check tổng hợp V3.53_1.xlsb"

def analyze_sheets(path):
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return
    
    report = {
        "file_name": os.path.basename(path),
        "file_size_mb": round(os.path.getsize(path) / (1024 * 1024), 2),
        "sheets": []
    }
    
    try:
        with open_xlsb(path) as wb:
            sheet_names = wb.sheets
            
            for sheet_name in sheet_names:
                sheet_info = {
                    "sheet_name": sheet_name,
                    "row_count": 0,
                    "column_headers": [],
                    "sample_rows": []
                }
                
                try:
                    with wb.get_sheet(sheet_name) as sheet:
                        # Count rows efficiently instead of loaded all to list first
                        rows = list(sheet.rows())
                        sheet_info["row_count"] = len(rows)
                        
                        if len(rows) > 0:
                            # Get first non-empty row as potential header
                            first_row = [r.v for r in rows[0]]
                            sheet_info["column_headers"] = [str(x) if x is not None else "" for x in first_row]
                            
                            # Extract sample rows (up to 5)
                            sample_limit = min(6, len(rows))
                            for i in range(1, sample_limit):
                                r_data = [r.v for r in rows[i]]
                                # Clean data types for json serializability
                                clean_data = []
                                for item in r_data:
                                    if item is None:
                                        clean_data.append("")
                                    else:
                                        clean_data.append(item)
                                sheet_info["sample_rows"].append(clean_data)
                except Exception as e:
                    sheet_info["error"] = str(e)
                
                report["sheets"].append(sheet_info)
                
    except Exception as e:
        report["error"] = str(e)
        
    with open("sheet_analysis.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    analyze_sheets(file_path)

if __name__ == "__main__":
    analyze_sheets(file_path)
