"""
Mô-đun 1: Nhân sự & Hiện diện Cửa hàng (MOD_HR)
Chức năng:
1. Kết nối API OPS tải báo cáo log Chấm công (Check In/Out).
2. Nạp và chuẩn hóa thông tin Danh sách Nhân sự (DSNS), Storelist.
3. Chạy các thuật toán phát hiện gian lận chấm công:
   - checkDupImei: Phát hiện 1 thiết bị (IMEI) chấm công cho nhiều mã nhân viên.
   - checkDistance: Phát hiện chấm công khoảng cách xa cửa hàng.
   - checkUnauthorized: Phát hiện nhân sự chấm công không thuộc Store.
"""

import pandas as pd
import requests
import urllib3
from datetime import datetime, timedelta
import io
import os

# Tắt cảnh báo SSL không an toàn nếu có
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class OPSDownloader:
    """
    Hỗ trợ tự động tải dữ liệu chấm công từ OPS portal sử dụng Cookie xác thực.
    """
    def __init__(self, cookie: str, base_url: str = "https://ops.winmart.vn"):
        self.cookie = cookie
        self.base_url = base_url
        self.session = requests.Session()
        self.session.verify = False  # Bỏ qua check SSL như cấu hình VBA
        
        # Thiết lập User-Agent chuẩn tương tự trình duyệt Edge/Chrome
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,vi-VN;q=0.8",
            "Cookie": self.cookie
        })

    def download_attendance_log(self, site_code: str, days_back: int = 30) -> pd.DataFrame:
        """
        Tải file excel Log chấm công chi tiết cho một Site Code cụ thể.
        """
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
        
        # Replicate URL structure from VBA DownloadOPS_InOut
        url = (
            f"{self.base_url}/bao-cao/bao-cao-check-in-out-chi-tiet"
            f"?app=WinCare&sSite={site_code}&sites={site_code}"
            f"&frda={start_date}&toda={end_date}"
            f"&emplCode=&p=1&isExport=True"
        )
        
        print(f"[OPS] Đang tải dữ liệu từ URL: {url}")
        response = self.session.get(url)
        
        if response.status_code == 200:
            print("[OPS] Tải dữ liệu thành công! Đang phân tích file Excel...")
            # Đọc Excel từ byte response payload
            # Lưu ý: file từ OPS trả về thường có định dạng xlsx chuẩn, sử dụng engine openpyxl
            try:
                df = pd.read_excel(io.BytesIO(response.content))
                return df
            except Exception as e:
                print(f"[Lỗi] Không thể đọc file Excel từ API: {e}")
                # Fallback: Lưu tạm file để debug
                debug_path = f"debug_attendance_{site_code}.xlsx"
                with open(debug_path, "wb") as f:
                    f.write(response.content)
                print(f"[Lỗi] Đã lưu nội dung thô phản hồi vào {debug_path} để kiểm tra.")
                raise e
        else:
            raise Exception(f"[Lỗi] API trả về mã trạng thái {response.status_code}. Có thể Cookie đã hết hạn.")

class HRAnalyst:
    """
    Xử lý phân tích logic vi phạm nhân sự và chấm công.
    """
    def __init__(self, store_list_df: pd.DataFrame = None, dsns_df: pd.DataFrame = None, attendance_df: pd.DataFrame = None):
        self.store_list_df = self._normalize_headers(store_list_df) if store_list_df is not None else None
        self.dsns_df = self._normalize_headers(dsns_df) if dsns_df is not None else None
        self.attendance_df = self._normalize_headers(attendance_df) if attendance_df is not None else None

    @staticmethod
    def _normalize_headers(df: pd.DataFrame) -> pd.DataFrame:
        """Chuẩn hóa tên cột: loại bỏ khoảng trắng thừa, chuyển sang chữ viết thường để so khớp dễ hơn."""
        if df is None:
            return None
        df = df.copy()
        df.columns = [str(col).strip().lower() for col in df.columns]
        return df

    @classmethod
    def load_from_excel(cls, file_path: str, site_code: str = None):
        """
        Nạp dữ liệu cục bộ từ file Excel (.xlsb hoặc .xlsx).
        """
        print(f"[HR] Đang đọc file dữ liệu: {file_path}")
        engine = 'pyxlsb' if file_path.endswith('.xlsb') else 'openpyxl'
        
        try:
            # Đọc bảng danh sách nhân sự
            print("[HR] Đang nạp sheet DSNS...")
            dsns = pd.read_excel(file_path, sheet_name='DSNS', engine=engine)
            
            # Đọc bảng Storelist 
            print("[HR] Đang nạp sheet Storelist...")
            storelist = pd.read_excel(file_path, sheet_name='Storelist', engine=engine)
            
            # Đọc log chấm công mẫu (nếu có dữ liệu mẫu sẵn)
            print("[HR] Đang nạp sheet Chấm công...")
            attendance = pd.read_excel(file_path, sheet_name='Chấm công', engine=engine)
            
            analyst = cls(storelist, dsns, attendance)
            
            if site_code:
                analyst.filter_by_site(site_code)
                
            return analyst
        except Exception as e:
            print(f"[Lỗi] Không thể nạp dữ liệu từ file Excel: {e}")
            raise e

    def filter_by_site(self, site_code: str):
        """
        Lọc dữ liệu của DSNS và Storelist theo Site Code cụ thể để tập trung xử lý.
        """
        site_str = str(site_code).strip()
        
        if self.store_list_df is not None:
            # Giả định cột 'ch' là cột chứa mã cửa hàng
            if 'ch' in self.store_list_df.columns:
                self.store_list_df = self.store_list_df[self.store_list_df['ch'].astype(str).str.contains(site_str, na=False)]
                
        if self.dsns_df is not None:
            if 'ch' in self.dsns_df.columns:
                self.dsns_df = self.dsns_df[self.dsns_df['ch'].astype(str).str.contains(site_str, na=False)]
                
        # Log chấm công có thể có 'mã site'
        if self.attendance_df is not None:
            site_col = 'mã site' if 'mã site' in self.attendance_df.columns else 'ma site'
            if site_col in self.attendance_df.columns:
                self.attendance_df = self.attendance_df[self.attendance_df[site_col].astype(str).str.contains(site_str, na=False)]

    def check_duplicate_imei(self) -> pd.DataFrame:
        """
        [Thuật toán 1] Phát hiện trùng lặp IMEI:
        Nhóm tất cả log chấm công theo IMEI, lọc các IMEI có nhiều hơn 1 Mã nhân viên khác nhau sử dụng.
        """
        if self.attendance_df is None or self.attendance_df.empty:
            print("[Cảnh báo] Không có dữ liệu Chấm công để phân tích IMEI.")
            return pd.DataFrame()
            
        df = self.attendance_df.copy()
        
        # Xác định tên cột chính xác
        col_imei = next((c for c in df.columns if 'imei' in c), None)
        col_mnv = next((c for c in df.columns if 'mã nhân viên' in c or 'ma nv' in c or 'ma nhan vien' in c), None)
        col_ten = next((c for c in df.columns if 'tên nhân viên' in c or 'ho ten' in c or 'ten nhan vien' in c), None)
        col_time = next((c for c in df.columns if 'thời gian' in c or 'thoi gian' in c), None)
        
        if not col_imei or not col_mnv:
            print(f"[Lỗi] Không tìm thấy các cột IMEI hoặc Mã nhân viên. Cột hiện có: {list(df.columns)}")
            return pd.DataFrame()
            
        # Làm sạch dữ liệu IMEI (Bỏ rỗng, ép kiểu chuỗi, bỏ khoảng trắng)
        df[col_imei] = df[col_imei].astype(str).str.strip()
        # Bỏ các giá trị rỗng hoặc không xác định
        df = df[~df[col_imei].isin(['', 'nan', 'None', '0'])]
        
        # Lấy bảng unique IMEI + Mã nhân viên
        cols_to_keep = [col_imei, col_mnv]
        if col_ten: cols_to_keep.append(col_ten)
        
        unique_users_per_imei = df[cols_to_keep].drop_duplicates()
        
        # Đếm số lượng nhân viên trên mỗi IMEI
        imei_counts = unique_users_per_imei.groupby(col_imei)[col_mnv].nunique().reset_index(name='so_nv_dung_chung')
        
        # Lọc ra các IMEI dùng chung bởi từ 2 người trở lên
        duplicate_imeis = imei_counts[imei_counts['so_nv_dung_chung'] > 1]
        
        if duplicate_imeis.empty:
            print("[Phân tích] Hoàn hảo! Không phát hiện dấu hiệu dùng chung IMEI.")
            return pd.DataFrame(columns=['imei', 'ma_nhan_vien', 'ten_nhan_vien', 'so_nv_dung_chung'])
            
        # Kết nối lại thông tin tên nhân viên cho chi tiết
        result = pd.merge(duplicate_imeis, unique_users_per_imei, on=col_imei, how='left')
        
        # Thêm chi tiết log để User dễ track
        # Sắp xếp lại cho trực quan
        result = result.sort_values(by=['so_nv_dung_chung', col_imei], ascending=[False, True])
        
        # Rename thân thiện hơn
        rename_dict = {
            col_imei: 'IMEI',
            col_mnv: 'Mã Nhân viên Trùng',
            'so_nv_dung_chung': 'Số NV cùng dùng IMEI này'
        }
        if col_ten: rename_dict[col_ten] = 'Họ và Tên'
        result = result.rename(columns=rename_dict)
        
        print(f"[Cảnh báo] Phát hiện {duplicate_imeis.shape[0]} thiết bị IMEI có hành vi dùng chung cho nhiều nhân sự!")
        return result

    def check_distance_violation(self, threshold_meters: int = 100) -> pd.DataFrame:
        """
        [Thuật toán 2] Phát hiện chấm công khoảng cách xa:
        Lọc các dòng log chấm công có khoảng cách (mét) vượt quá ngưỡng cho phép.
        """
        if self.attendance_df is None or self.attendance_df.empty:
            return pd.DataFrame()
            
        df = self.attendance_df.copy()
        
        col_dist = next((c for c in df.columns if 'khoảng cách' in c or 'khoang cach' in c), None)
        col_mnv = next((c for c in df.columns if 'mã nhân viên' in c or 'ma nv' in c), None)
        col_ten = next((c for c in df.columns if 'tên nhân viên' in c or 'ho ten' in c), None)
        col_time = next((c for c in df.columns if 'thời gian' in c or 'thoi gian' in c), None)
        col_type = next((c for c in df.columns if 'loại' in c or 'loai' in c), None) # In / Out
        
        if not col_dist:
            print("[Lỗi] Không tìm thấy cột 'Khoảng cách' trong log chấm công.")
            return pd.DataFrame()
            
        # Chuyển đổi kiểu dữ liệu cột khoảng cách
        df[col_dist] = pd.to_numeric(df[col_dist], errors='coerce')
        
        # Lọc các vi phạm
        violations = df[df[col_dist] > threshold_meters].copy()
        
        if violations.empty:
            return pd.DataFrame()
            
        # Chọn lọc các cột quan trọng đưa ra báo cáo
        report_cols = []
        for col in [col_mnv, col_ten, col_time, col_type, col_dist]:
            if col: report_cols.append(col)
            
        result = violations[report_cols].sort_values(by=col_dist, ascending=False)
        
        # Rename
        rename_map = {}
        if col_mnv: rename_map[col_mnv] = 'Mã NV'
        if col_ten: rename_map[col_ten] = 'Họ tên'
        if col_time: rename_map[col_time] = 'Thời gian'
        if col_type: rename_map[col_type] = 'Loại'
        if col_dist: rename_map[col_dist] = 'Khoảng cách vi phạm (m)'
        
        result = result.rename(columns=rename_map)
        print(f"[Cảnh báo] Phát hiện {len(result)} trường hợp chấm công xa cửa hàng (> {threshold_meters}m)!")
        return result

    def check_unauthorized_staff(self) -> pd.DataFrame:
        """
        [Thuật toán 3] Phát hiện nhân viên lạ:
        Lọc danh sách nhân viên chấm công có mặt trong Attendance nhưng KHÔNG có tên trong DSNS của Store.
        """
        if self.attendance_df is None or self.dsns_df is None:
            print("[Cảnh báo] Không đủ dữ liệu DSNS và Chấm công để kiểm tra Nhân sự ngoài.")
            return pd.DataFrame()
            
        df_att = self.attendance_df.copy()
        df_dsns = self.dsns_df.copy()
        
        att_mnv = next((c for c in df_att.columns if 'mã nhân viên' in c or 'ma nv' in c), None)
        dsns_mnv = next((c for c in df_dsns.columns if 'mã nv' in c or 'ma nv' in c or 'ma_nv' in c), None)
        att_ten = next((c for c in df_att.columns if 'tên nhân viên' in c or 'ho ten' in c), None)
        
        if not att_mnv or not dsns_mnv:
            print("[Lỗi] Không thể so khớp do thiếu cột Mã Nhân Viên.")
            return pd.DataFrame()
            
        # Lấy list distinct NV chấm công
        staff_attendance = df_att[[att_mnv, att_ten]].drop_duplicates() if att_ten else df_att[[att_mnv]].drop_duplicates()
        staff_attendance[att_mnv] = staff_attendance[att_mnv].astype(str).str.strip()
        
        # Lấy list mã NV được duyệt tại Store
        authorized_staff = set(df_dsns[dsns_mnv].astype(str).str.strip().unique())
        
        # Lọc
        unauthorized = staff_attendance[~staff_attendance[att_mnv].isin(authorized_staff)]
        
        if unauthorized.empty:
            return pd.DataFrame()
            
        # Rename cho trực quan
        rename_map = {att_mnv: 'Mã NV chấm công nhưng không thuộc DSNS'}
        if att_ten: rename_map[att_ten] = 'Họ tên ghi nhận'
        unauthorized = unauthorized.rename(columns=rename_map)
        
        print(f"[Cảnh báo] Phát hiện {len(unauthorized)} nhân sự chấm công nhưng không đăng ký trên DSNS cửa hàng!")
        return unauthorized

    def run_all_checks(self, distance_threshold: int = 100) -> dict:
        """Chạy trọn gói các bước phân tích của Mô-đun 1."""
        print("\n" + "="*50)
        print("BẮT ĐẦU KHỞI CHẠY PHÂN TÍCH MÔ-ĐUN 1 (MOD_HR)")
        print("="*50)
        
        result = {
            'duplicate_imei': self.check_duplicate_imei(),
            'distance_violation': self.check_distance_violation(distance_threshold),
            'unauthorized_staff': self.check_unauthorized_staff()
        }
        print("="*50)
        print("HOÀN TẤT CHẠY MÔ-ĐUN 1.\n")
        return result
