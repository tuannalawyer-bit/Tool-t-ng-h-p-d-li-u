import pandas as pd
import sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

OUTPUT = r"D:\OneDrive - WIN\Desktop\công việc thực hiện\Tháng 5\Chuyên đề xây dựng mở mới\merged_result_v3_ultra_strict_filled.xlsx"

df = pd.read_excel(OUTPUT)

print("--- KIỂM TRA PHIÊN BẢN MỚI (V3_ultra_strict_filled) ---")

# Kiểm tra dòng '2BPW'
row_2bpw = df[df['Store code'].astype(str).str.contains('2BPW', na=False)]
if len(row_2bpw) > 0:
    print("\nDòng '2BPW' (Điền Lư) - Giờ đây đã có dữ liệu gần nhất!")
    print(f"  Địa chỉ Gốc: {row_2bpw['Địa chỉ'].values[0]}")
    print(f"  Trạng thái:  {row_2bpw['MATCH_STATUS'].values[0]} (Vẫn là ĐỎ)")
    print(f"  Điểm số:     {row_2bpw['MATCH_SCORE (%)'].values[0]} %")
    print(f"  Khớp với:    {row_2bpw['TĐG_Thông tin MB đang thuê'].values[0]}")
    print(f"  Phương thức: {row_2bpw['MATCH_METHOD'].values[0]}")
