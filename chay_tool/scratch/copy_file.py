import shutil
import os

src = r"D:\OneDrive - WIN\Desktop\công việc thực hiện\Tháng 5\Chuyên đề xây dựng mở mới\danh sach ky hop dong.xlsx"
dst = r"d:\Dự án AI\chay_tool\scratch\temp_file1.xlsx"

try:
    shutil.copy2(src, dst)
    print("Success")
except Exception as e:
    print(f"Error: {e}")
