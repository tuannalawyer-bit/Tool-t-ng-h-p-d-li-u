import pandas as pd
from rapidfuzz import fuzz, process
import re
from unidecode import unidecode
import sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PATH1 = r"D:\OneDrive - WIN\Desktop\công việc thực hiện\Tháng 5\Chuyên đề xây dựng mở mới\danh sach ky hop dong.xlsx"
PATH2 = r"D:\OneDrive - WIN\Desktop\công việc thực hiện\Tháng 5\Chuyên đề xây dựng mở mới\form tool.xlsx"

df1 = pd.read_excel(PATH1)
df2 = pd.read_excel(PATH2, header=2)
df1 = df1.dropna(subset=['Địa chỉ']).reset_index(drop=True)
df2 = df2.dropna(subset=['Thông tin MB đang thuê']).reset_index(drop=True)

for i, addr in enumerate(df1['Địa chỉ']):
    if "1094-1787" in str(addr):
        print(f"Index {i} in df1: {addr}")
        break

for i, addr in enumerate(df1['Địa chỉ']):
    if "Lâm Hóa 1" in str(addr):
        print(f"Index {i} in df1: {addr}")
        break
