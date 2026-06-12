import pandas as pd
import sys

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)

path1 = r"D:\OneDrive - WIN\Desktop\công việc thực hiện\Tháng 5\Chuyên đề xây dựng mở mới\danh sach ky hop dong.xlsx"
path2 = r"D:\OneDrive - WIN\Desktop\công việc thực hiện\Tháng 5\Chuyên đề xây dựng mở mới\form tool.xlsx"

df1 = pd.read_excel(path1)
df2 = pd.read_excel(path2, header=2)
df1 = df1.dropna(subset=['Địa chỉ']).reset_index(drop=True)
df2 = df2.dropna(subset=['Thông tin MB đang thuê']).reset_index(drop=True)

# Pick an address from File 1 that we know failed matching
addr_to_search = "Thôn Dụ Nghĩa" # from previous output
print(f"=== SEARCHING MANUALLY FOR: {addr_to_search} ===")
for i, addr2 in enumerate(df2['Thông tin MB đang thuê']):
    if "nghĩa" in str(addr2).lower() or "nghia" in str(addr2).lower() or "dụ" in str(addr2).lower() or "du" in str(addr2).lower():
        print(f"Row {i} in File 2: {addr2}")
