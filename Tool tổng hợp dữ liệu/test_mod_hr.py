"""
Kịch bản Kiểm thử Độc lập cho Mô-đun 1 (MOD_HR)
"""
import pandas as pd
import sys
from mod_hr_check import HRAnalyst

def run_test():
    # Đảm bảo console in được tiếng Việt
    sys.stdout.reconfigure(encoding='utf-8')
    print("=== BẮT ĐẦU KỊCH BẢN KIỂM THỬ MÔ-ĐUN 1 ===")

    # 1. Tạo dữ liệu giả định (Mock Data)
    print("\n[1] Tạo dữ liệu Mock Data...")
    
    # Giả lập danh sách nhân sự đã đăng ký tại Store (Site Code: 2070)
    dsns_data = {
        'CH': ['2070', '2070', '2070'],
        'Họ tên': ['Nguyễn Văn A', 'Trần Thị B', 'Lê Văn C'],
        'Mã NV': ['NV001', 'NV002', 'NV003'],
        'Chức vụ': ['CHT', 'CHP', 'Thu ngân']
    }
    df_dsns = pd.DataFrame(dsns_data)
    print("Danh sách nhân sự (DSNS) Store 2070:")
    print(df_dsns)

    # Giả lập Storelist
    storelist_data = {
        'CH': ['2070'],
        'Tên cửa hàng': ['WM+ Lê Duẩn'],
        'Vĩ độ': [21.0267],
        'Kinh độ': [105.8416]
    }
    df_store = pd.DataFrame(storelist_data)

    # Giả lập Log chấm công có cài cắm "LỖI VI PHẠM"
    attendance_data = {
        'Mã nhân viên': [
            'NV001',  # Hợp lệ
            'NV002',  # VI PHẠM 1: Cùng dùng IMEI với NV001
            'NV003',  # VI PHẠM 2: Chấm xa (150m)
            'NV999'   # VI PHẠM 3: Nhân viên lạ, không thuộc Store này
        ],
        'Tên nhân viên': [
            'Nguyễn Văn A',
            'Trần Thị B',
            'Lê Văn C',
            'Người lạ Ơi'
        ],
        'Mã site': ['2070', '2070', '2070', '2070'],
        'Loại': ['IN', 'IN', 'IN', 'IN'],
        'Thời gian': ['2026-05-14 08:00', '2026-05-14 08:05', '2026-05-14 08:10', '2026-05-14 08:15'],
        'Khoảng cách(mét)': [15, 20, 150, 10], # NV003 chấm cách 150m > 100m
        'Imei': [
            'IMEI_SHARE_123', 
            'IMEI_SHARE_123', # Trùng IMEI của NV001
            'IMEI_RIENG_3', 
            'IMEI_LA_9'
        ]
    }
    df_att = pd.DataFrame(attendance_data)
    print("\nLog chấm công ghi nhận (Cài cắm vi phạm):")
    print(df_att)

    # 2. Khởi tạo bộ phân tích HRAnalyst
    print("\n[2] Khởi tạo HRAnalyst và chạy phân tích...")
    analyst = HRAnalyst(store_list_df=df_store, dsns_df=df_dsns, attendance_df=df_att)
    
    # Chạy tất cả các kiểm tra với khoảng cách ngưỡng 100m
    results = analyst.run_all_checks(distance_threshold=100)

    # 3. Xác thực kết quả
    print("\n[3] KẾT QUẢ PHÂN TÍCH CHI TIẾT:")
    
    print("\n❌ PHÁT HIỆN TRÙNG IMEI (THUẬT TOÁN 1):")
    df_dup = results['duplicate_imei']
    if not df_dup.empty:
        print(df_dup.to_string(index=False))
    else:
        print("Đạt (Không phát hiện lỗi)")

    print("\n❌ PHÁT HIỆN CHẤM CÔNG XA > 100M (THUẬT TOÁN 2):")
    df_dist = results['distance_violation']
    if not df_dist.empty:
        print(df_dist.to_string(index=False))
    else:
        print("Đạt (Không phát hiện lỗi)")

    print("\n❌ PHÁT HIỆN NHÂN SỰ LẠ NGOÀI DSNS (THUẬT TOÁN 3):")
    df_unauth = results['unauthorized_staff']
    if not df_unauth.empty:
        print(df_unauth.to_string(index=False))
    else:
        print("Đạt (Không phát hiện lỗi)")

    print("\n" + "="*50)
    print("KỊCH BẢN KIỂM THỬ HOÀN TẤT THÀNH CÔNG.")
    print("="*50)

if __name__ == "__main__":
    run_test()
