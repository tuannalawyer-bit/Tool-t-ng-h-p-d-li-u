import openpyxl
import sys

def print_top():
    sys.stdout.reconfigure(encoding='utf-8')
    wb = openpyxl.load_workbook("Ket_Qua_Phan_Tich_Rui_Ro_Ton_Kho.xlsx")
    ws = wb["Top UU TIEN KIEM TRA"]
    print("=== TOP 10 RANKED STORES AFTER FIX ===")
    for row in ws.iter_rows(min_row=4, max_row=13, values_only=True):
        print(f"Rank {row[0]}: ID={row[1]}, Name={row[2]}, Score={row[3]}, CLKK={row[6]}, Ton={row[4]}")

if __name__ == "__main__":
    print_top()
