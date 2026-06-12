import pandas as pd
import sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

OUTPUT = r"D:\OneDrive - WIN\Desktop\công việc thực hiện\Tháng 5\Chuyên đề xây dựng mở mới\merged_result_v3_ultra_strict.xlsx"

df = pd.read_excel(OUTPUT)

print("--- KIỂM TRA CÁC DÒNG GHÉP ---")

# Kiểm tra xem '2BPW' (Điền Lư) có còn bị khớp sai không
row_2bpw = df[df['Store code'].astype(str).str.contains('2BPW', na=False)]
if len(row_2bpw) > 0:
    print("\nDòng '2BPW' (Điền Lư):")
    print(f"  Địa chỉ Gốc: {row_2bpw['Địa chỉ'].values[0]}")
    print(f"  Trạng thái:  {row_2bpw['MATCH_STATUS'].values[0]}")
    print(f"  Điểm số:     {row_2bpw['MATCH_SCORE (%)'].values[0]}")
    print(f"  Khớp với:    {row_2bpw['TĐG_Thông tin MB đang thuê'].values[0]}")

# Kiểm tra ngẫu nhiên 5 dòng FUZZY để xem có chuẩn xác không
fuzzy_rows = df[df['MATCH_STATUS'] == 'FUZZY'].head(5)
print("\n--- KIỂM TRA 5 DÒNG FUZZY ĐẦU TIÊN ---")
for i, r in fuzzy_rows.iterrows():
    print(f"\nDòng {i}:")
    print(f"  Gốc: {r['Địa chỉ']}")
    print(f"  Khớp: {r['TĐG_Thông tin MB đang thuê']}")
    print(f"  Điểm: {r['MATCH_SCORE (%)']} | Phương thức: {r['MATCH_METHOD']}")
