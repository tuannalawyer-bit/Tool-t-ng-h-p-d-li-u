import os

# Cấu hình Hệ thống
APP_NAME = "TripScheduler Pro - Phân Lịch Công Tác Tối Ưu"
VERSION = "1.6.1"

# Quy tắc năng suất làm việc
NEAR_RADIUS_KM = 20.0        # Ngưỡng Nội thành (<= 20km)
MAX_NEAR_STORES_PER_DAY = 3  # Nội thành đi tối đa 3 CH/ngày
MAX_FAR_STORES_PER_DAY = 2   # Ngoại thành đi tối đa 2 CH/ngày

# Trọng số chi phí thời gian cho 1 CH (đơn vị: Ngày)
WEIGHT_NEAR = 1.0 / MAX_NEAR_STORES_PER_DAY  # 0.333
WEIGHT_FAR = 1.0 / MAX_FAR_STORES_PER_DAY    # 0.5

# API Routing (OSRM - Đổi sang chế độ Đi bộ /foot/ để chính xác tuyệt đối)
OSRM_URL_ROUTE = "https://router.project-osrm.org/route/v1/foot/"
OSRM_URL_TABLE = "https://router.project-osrm.org/table/v1/foot/"

# Thông số Nhận diện sông ngòi & Rào cản vật lý
RIVER_DETOUR_RATIO = 3.5      # Ngưỡng tỷ lệ (Đường bộ / Chim bay) báo hiệu có sông cắt qua
RIVER_PENALTY_FACTOR = 2.5    # Hệ số phạt nhân khoảng cách đường bộ để ép thuật toán không đi qua sông

# Hệ số uốn lượn (dùng dự phòng khi offline để nhân khoảng cách chim bay)
ROAD_WINDING_FACTOR = 1.3

# Mảng màu dùng để vẽ đường đi trên bản đồ cho các nhân viên khác nhau
COLOR_PALETTE = [
    'blue', 'green', 'red', 'purple', 'orange', 'darkred', 
    'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue',
    'darkpurple', 'white', 'pink', 'lightblue', 'lightgreen', 
    'gray', 'black', 'lightgray'
]

# Thư mục lưu tệp
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# Tên file mẫu mặc định
EXCEL_TEMPLATE_NAME = "mau_phan_lich.xlsx"
EXCEL_TEMPLATE_PATH = os.path.join(TEMPLATES_DIR, EXCEL_TEMPLATE_NAME)
