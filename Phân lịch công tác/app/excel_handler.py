import os
import logging
import pandas as pd
import tempfile
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from app.config import EXCEL_TEMPLATE_PATH, EXCEL_TEMPLATE_NAME

logger = logging.getLogger(__name__)

def create_default_template():
    """Tạo tệp mẫu Excel mặc định nếu chưa tồn tại"""
    directory = os.path.dirname(EXCEL_TEMPLATE_PATH)
    if not os.path.exists(directory):
        os.makedirs(directory)
        
    if not os.path.exists(EXCEL_TEMPLATE_PATH):
        wb = Workbook()
        ws = wb.active
        ws.title = "Danh sách Cửa hàng"
        
        # Tạo tiêu đề
        headers = ["Mã CH", "Tên CH", "Latitude", "Longitude", "Địa chỉ", "Ghi chú"]
        ws.append(headers)
        
        # Dữ liệu mẫu (tọa độ khu vực Hà Nội làm ví dụ)
        sample_data = [
            ["CH001", "Cửa hàng Tràng Tiền", 21.0256, 105.8525, "Tràng Tiền, Hoàn Kiếm, Hà Nội", "Mẫu gần"],
            ["CH002", "Cửa hàng Láng Hạ", 21.0152, 105.8115, "88 Láng Hạ, Đống Đa, Hà Nội", "Mẫu gần"],
            ["CH003", "Cửa hàng Cầu Giấy", 21.0362, 105.7905, "Cầu Giấy, Hà Nội", "Mẫu gần"],
            ["CH004", "Cửa hàng Sơn Tây", 21.1355, 105.5023, "Thị xã Sơn Tây, Hà Nội", "Mẫu xa (>20km)"],
            ["CH005", "Cửa hàng Hòa Lạc", 20.9978, 105.5335, "Thạch Thất, Hà Nội", "Mẫu xa (>20km)"],
            ["CH006", "Cửa hàng Mỹ Đình", 21.0285, 105.7782, "Nam Từ Liêm, Hà Nội", "Mẫu gần"],
            ["CH007", "Cửa hàng Gia Lâm", 21.0358, 105.9010, "Long Biên, Hà Nội", "Mẫu gần"],
            ["CH008", "Cửa hàng Đông Anh", 21.1366, 105.8471, "Đông Anh, Hà Nội", "Mẫu xa"],
        ]
        
        for row in sample_data:
            ws.append(row)
            
        # Định dạng header
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        header_font = Font(color="FFFFFF", bold=True)
        
        for col_idx in range(1, len(headers) + 1):
            cell = ws.cell(row=1, column=col_idx)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")
            
        # Tự động điều chỉnh độ rộng cột
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            ws.column_dimensions[column_letter].width = max(max_length + 3, 12)
            
        wb.save(EXCEL_TEMPLATE_PATH)
        print(f"Da tao thanh cong file mau tai {EXCEL_TEMPLATE_PATH}")

def read_store_list(file_path):
    """Đọc danh sách cửa hàng từ Excel và tự động nhận diện cột thông minh"""
    try:
        df = pd.read_excel(file_path)
        # Lưu lại danh sách tên cột gốc ban đầu
        df.attrs['original_cols'] = list(df.columns)
        
        # Tạo bản copy chuẩn hóa chữ thường không dấu để dò cột
        cols = [str(c).strip() for c in df.columns]
        df.columns = cols
        
        # Bộ ánh xạ thông dụng
        lat_map = ['vĩ độ', 'vi do', 'latitude', 'lat', 'y']
        lon_map = ['kinh độ', 'kinh do', 'longitude', 'lon', 'x']
        code_map = ['mã sap', 'ma sap', 'mã ch', 'ma ch', 'storecode', 'code', 'id']
        name_map = ['tên cửa hàng', 'ten cua hang', 'tên ch', 'ten ch', 'name']
        addr_map = ['địa chỉ ch', 'dia chi ch', 'địa chỉ', 'dia chi', 'address']
        
        found_lat, found_lon = None, None
        found_code, found_name, found_addr = None, None, None
        
        # Lớp ưu tiên 1: Khớp hoàn toàn (Chính xác tuyệt đối để tránh nhầm lẫn)
        for col in df.columns:
            c_low = str(col).lower().strip()
            
            if not found_lat and c_low in ['vĩ độ', 'vi do', 'latitude', 'lat', 'y']:
                found_lat = col
            elif not found_lon and c_low in ['kinh độ', 'kinh do', 'longitude', 'lon', 'lng', 'x']:
                found_lon = col
            elif not found_code and c_low in ['mã sap', 'ma sap', 'mã ch', 'ma ch', 'storecode', 'code', 'id']:
                found_code = col
            elif not found_name and c_low in ['tên cửa hàng', 'ten cua hang', 'tên ch', 'ten ch', 'name', 'storename']:
                found_name = col
            elif not found_addr and c_low in ['địa chỉ ch', 'dia chi ch', 'địa chỉ', 'dia chi', 'address']:
                found_addr = col

        # Lớp ưu tiên 2: Khớp một phần nhưng LOẠI TRỪ các từ khóa cực ngắn (chỉ dùng từ khóa an toàn)
        if not found_lat:
            for col in df.columns:
                c_low = str(col).lower().strip()
                if any(x in c_low for x in ['vĩ độ', 'vi do', 'latitude']):
                    found_lat = col
                    break
        if not found_lon:
            for col in df.columns:
                c_low = str(col).lower().strip()
                if any(x in c_low for x in ['kinh độ', 'kinh do', 'longitude']):
                    found_lon = col
                    break
        if not found_code:
            for col in df.columns:
                c_low = str(col).lower().strip()
                if any(x in c_low for x in ['mã sap', 'ma sap', 'mã ch', 'ma ch']):
                    found_code = col
                    break
        if not found_name:
            for col in df.columns:
                c_low = str(col).lower().strip()
                if any(x in c_low for x in ['tên cửa hàng', 'ten cua hang', 'tên ch', 'ten ch']):
                    found_name = col
                    break
                
        if not found_lat or not found_lon:
            logger.error("Không thể tìm thấy cột chứa dữ liệu tọa độ!")
            raise ValueError("Không tìm thấy cột tọa độ Vĩ độ/Kinh độ. Hãy chắc chắn bảng Excel có chứa cột 'Vĩ độ' và 'Kinh độ'.")
            
        logger.info(f"Dò cột thành công -> Vĩ độ: [{found_lat}], Kinh độ: [{found_lon}], Mã CH: [{found_code}], Tên CH: [{found_name}]")
            
        # Chuẩn hóa kiểu số cho tọa độ
        df['Latitude'] = pd.to_numeric(df[found_lat], errors='coerce')
        df['Longitude'] = pd.to_numeric(df[found_lon], errors='coerce')
        
        # Điền các cột phụ trợ cho module Solver
        df['StoreCode'] = df[found_code] if found_code else df.index.astype(str)
        df['Name'] = df[found_name] if found_name else ("CH_" + df.index.astype(str))
        df['Address'] = df[found_addr] if found_addr else ""
        
        # Tạo mã định danh dòng gốc để mapping ngược lúc xuất file
        df['__temp_id__'] = df.index
        
        # Loại bỏ dòng không có tọa độ hợp lệ
        valid_df = df.dropna(subset=['Latitude', 'Longitude']).copy()
        
        # Truyền lại thuộc tính sang dataframe mới sau khi dropna
        valid_df.attrs['original_cols'] = df.attrs['original_cols']
        valid_df.attrs['found_code'] = found_code
        valid_df.attrs['found_name'] = found_name
        
        if valid_df.empty:
            raise ValueError("Tất cả các dòng đều không có tọa độ hợp lệ!")
            
        return valid_df
    except Exception as e:
        raise Exception(f"Lỗi đọc Excel: {str(e)}")

def export_results_and_open(results, stores_df):
    """
    Xuất kết quả tối ưu DỰA TRÊN TỆP GỐC CỦA KHÁCH HÀNG:
    - Giữ nguyên toàn bộ các cột gốc của khách hàng.
    - Điền tên nhân sự vào cột 'Người phụ trách' (nếu có) hoặc thêm mới.
    - Bổ sung cột 'Ngày công tác' và 'Thứ tự ghé thăm'.
    """
    # 1. TẠO DATAFRAME ĐẦU RA DỰA TRÊN TỆP GỐC
    output_df = stores_df.copy()
    orig_cols = stores_df.attrs.get('original_cols', list(stores_df.columns))
    
    # Dò tìm xem có cột "Người phụ trách" sẵn trong file gốc không
    assignee_col = None
    for col in orig_cols:
        if str(col).lower().strip() in ['người phụ trách', 'nguoi phu trach', 'phụ trách', 'phu trach']:
            assignee_col = col
            break
            
    if not assignee_col:
        assignee_col = 'Người phụ trách'
        output_df[assignee_col] = ""
        
    # Khởi tạo các cột lịch trình mới
    col_day = 'Ngày công tác'
    col_seq = 'Thứ tự ghé thăm trong ngày'
    col_dist = 'Quãng đường ngày (km)'
    
    output_df[col_day] = ""
    output_df[col_seq] = ""
    output_df[col_dist] = ""
    
    # Đảm bảo các cột đích chấp nhận chuỗi văn bản (object) để tránh lỗi Pandas float64 Dtype crash
    output_df[assignee_col] = output_df[assignee_col].astype(object)
    output_df[col_day] = output_df[col_day].astype(object)
    output_df[col_seq] = output_df[col_seq].astype(object)
    output_df[col_dist] = output_df[col_dist].astype(object)
    
    # 2. ĐIỀN THÔNG TIN LẬP LỊCH DỰA TRÊN INDEX GỐC (__temp_id__)
    mapped_indices = set()
    for staff_id, staff_data in results['staff_schedules'].items():
        staff_name = f"Nhân viên {staff_id + 1}"
        
        for route in staff_data['Routes']:
            day = route['Day']
            day_dist = route['Distance']
            
            for seq, store in enumerate(route['Stores']):
                orig_idx = store.get('__temp_id__')
                if orig_idx is not None and orig_idx in output_df.index:
                    output_df.at[orig_idx, assignee_col] = staff_name
                    output_df.at[orig_idx, col_day] = f"Ngày {day}"
                    output_df.at[orig_idx, col_seq] = seq + 1
                    if seq == 0:
                        output_df.at[orig_idx, col_dist] = day_dist
                    mapped_indices.add(orig_idx)
                        
    # Sắp xếp kết quả cho đẹp: Theo Người phụ trách -> Ngày -> Thứ tự đi
    # Tạo bản sao chỉ chứa các cột gốc và các cột mới được bổ sung (loại bỏ biến rác của hệ thống)
    final_columns = list(orig_cols)
    if assignee_col not in final_columns:
        final_columns.append(assignee_col)
    
    final_columns.extend([col_day, col_seq, col_dist])
    
    # Lọc lại chỉ lấy các cột mong muốn
    report_df = output_df[final_columns].copy()
    
    # Xử lý sắp xếp an toàn (chuyển sang string/number tạm thời để sort)
    report_df['__sort_day__'] = report_df[col_day].astype(str)
    report_df['__sort_seq__'] = pd.to_numeric(report_df[col_seq], errors='coerce').fillna(999)
    
    # Đưa những dòng ĐÃ ĐƯỢC PHÂN CÔNG lên trên cùng, sort theo lịch
    report_df = report_df.sort_values(
        by=[assignee_col, '__sort_day__', '__sort_seq__'], 
        ascending=[True, True, True]
    )
    
    # Xóa cột sort trung gian
    report_df = report_df.drop(columns=['__sort_day__', '__sort_seq__'])
    
    # 3. GHI DỮ LIỆU RA EXCEL QUA OPENPYXL ĐỂ ĐỊNH DẠNG ĐẸP
    wb = Workbook()
    
    # --- Sheet 1: Báo cáo tổng hợp ---
    ws_summary = wb.active
    ws_summary.title = "Tóm tắt đợt công tác"
    
    header_fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True)
    border_thin = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
    
    summary_headers = ["Nhân sự phân bổ", "Tổng số Cửa hàng", "Tổng số ngày đi", "Tổng Quãng đường (km)"]
    ws_summary.append(summary_headers)
    
    for col_idx in range(1, len(summary_headers) + 1):
        cell = ws_summary.cell(row=1, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")
        cell.border = border_thin
        
    for item in results['summary']:
        row_data = [item['Nhân viên'], item['Số cửa hàng'], item['Số ngày đi'], item['Tổng quãng đường (km)']]
        ws_summary.append(row_data)
        for col_idx in range(1, len(row_data) + 1):
            cell = ws_summary.cell(row=ws_summary.max_row, column=col_idx)
            cell.border = border_thin
            if col_idx > 1:
                cell.alignment = Alignment(horizontal="right")
                
    # --- Sheet 2: Bản gốc bổ sung lịch trình ---
    ws_detail = wb.create_sheet(title="Kế hoạch Phân bổ chi tiết")
    
    # Ghi Headers cho Sheet chi tiết
    ws_detail.append(list(report_df.columns))
    detail_header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    
    for col_idx in range(1, len(report_df.columns) + 1):
        cell = ws_detail.cell(row=1, column=col_idx)
        cell.fill = detail_header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")
        cell.border = border_thin
        
    # Ghi Dữ liệu
    for r_idx, row in enumerate(report_df.values, start=2):
        ws_detail.append(list(row))
        for c_idx in range(1, len(row) + 1):
            cell = ws_detail.cell(row=r_idx, column=c_idx)
            cell.border = border_thin
            
            # Tô màu nhấn mạnh các cột mới bổ sung ở cuối bảng để khách hàng dễ nhận biết
            # 3 cột cuối + cột Người phụ trách
            col_name = report_df.columns[c_idx-1]
            if col_name in [assignee_col, col_day, col_seq, col_dist]:
                cell.fill = PatternFill(start_color="EBF1DE", end_color="EBF1DE", fill_type="solid") # Màu xanh lá nhạt
                
    # Tự căn chỉnh độ rộng cột
    for ws in [ws_summary, ws_detail]:
        for column in ws.columns:
            max_len = 0
            col_letter = column[0].column_letter
            for cell in column:
                if cell.value:
                    val_str = str(cell.value)
                    if len(val_str) > max_len:
                        max_len = len(val_str)
            ws.column_dimensions[col_letter].width = min(max(max_len + 3, 10), 35)
            
    # Lưu file tạm và trả về đường dẫn để UI xử lý
    fd, path = tempfile.mkstemp(suffix='.xlsx', prefix='Ket_Qua_Lap_Lich_')
    os.close(fd)
    
    wb.save(path)
    return path
