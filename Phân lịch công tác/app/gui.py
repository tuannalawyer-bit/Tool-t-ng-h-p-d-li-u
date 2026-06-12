import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
from app.config import APP_NAME, VERSION, EXCEL_TEMPLATE_PATH
from app.excel_handler import create_default_template, read_store_list, export_results_and_open
from app.solver import optimize_schedule
from app.map_viewer import generate_interactive_map

import sys
import logging
import datetime

# ============ CẤU HÌNH HỆ THỐNG GHI NHẬT KÝ (LOGGING) ============
LOG_FILE = "he_thong_phan_lich.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8', mode='a'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("App")

# Hook bẫy lỗi toàn diện: Đảm bảo mọi sự cố sập app đều được ghi lại chi tiết trong log
def handle_uncaught_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.critical("💥 LỖI NGHIÊM TRỌNG KHIẾN ỨNG DỤNG SẬP:", exc_info=(exc_type, exc_value, exc_traceback))
    messagebox.showerror(
        "Sự cố Hệ thống", 
        f"Phần mềm vừa gặp một sự cố nghiêm trọng và không thể tự khôi phục.\n\n"
        f"👉 Toàn bộ vết lỗi kỹ thuật đã được ghi tự động vào tệp:\n'{LOG_FILE}'\n\n"
        f"Vui lòng gửi tệp này cho kỹ thuật viên để phân tích."
    )

sys.excepthook = handle_uncaught_exception
# ==============================================================

class TripSchedulerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # 1. Cài đặt cửa sổ ứng dụng
        self.title(f"{APP_NAME} v{VERSION}")
        self.geometry("1100x680")
        ctk.set_appearance_mode("System")  # Lấy chế độ sáng/tối của Windows
        ctk.set_default_color_theme("blue") # Chủ đề xanh hiện đại
        
        logger.info(f"🟢 KHỞI ĐỘNG ỨNG DỤNG THÀNH CÔNG: {APP_NAME} v{VERSION}")
        
        # Biến lưu trữ dữ liệu
        self.input_file_path = ""
        self.stores_df = None
        self.results = None
        self.hotel_lat = 21.0285  # Tọa độ mặc định (Hà Nội)
        self.hotel_lon = 105.8542
        self.excel_path = None
        self.map_path = None
        
        # Đảm bảo file mẫu tồn tại
        create_default_template()
        
        # 2. Xây dựng bố cục chính (Grid 1x2: Sidebar + Main Content)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # --- CỘT TRÁI: SIDEBAR CẤU HÌNH ---
        self.sidebar_frame = ctk.CTkFrame(self, width=320, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(10, weight=1) # Đẩy cài đặt theme xuống đáy
        
        # Tiêu đề Sidebar
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="CẤU HÌNH ĐỢT ĐI", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 20))
        
        # Khai báo Tọa độ Khách sạn / Văn phòng
        self.coord_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.coord_frame.grid(row=1, column=0, padx=20, pady=(10, 20), sticky="ew")
        
        self.lbl_hotel = ctk.CTkLabel(self.coord_frame, text="📍 Vị trí Khách sạn / Văn phòng:", anchor="w")
        self.lbl_hotel.pack(fill="x", pady=(0, 5))
        
        # Vĩ độ
        self.lat_entry = ctk.CTkEntry(self.coord_frame, placeholder_text="Vĩ độ (Latitude)")
        self.lat_entry.insert(0, str(self.hotel_lat))
        self.lat_entry.pack(fill="x", pady=5)
        
        # Kinh độ
        self.lon_entry = ctk.CTkEntry(self.coord_frame, placeholder_text="Kinh độ (Longitude)")
        self.lon_entry.insert(0, str(self.hotel_lon))
        self.lon_entry.pack(fill="x", pady=5)
        
        # Số lượng nhân viên (Nhập số thay vì kéo tay giới hạn 10)
        self.lbl_staff = ctk.CTkLabel(self.sidebar_frame, text="👥 Số lượng nhân sự đi công tác:", anchor="w")
        self.lbl_staff.grid(row=2, column=0, padx=20, pady=(10, 0), sticky="w")
        
        self.staff_entry = ctk.CTkEntry(self.sidebar_frame, placeholder_text="Nhập số lượng (VD: 3)")
        self.staff_entry.insert(0, "2")
        self.staff_entry.grid(row=3, column=0, padx=20, pady=(5, 15), sticky="ew")
        
        # Nút nạp danh sách
        self.btn_import = ctk.CTkButton(self.sidebar_frame, text="📂 Chọn Tệp Cửa Hàng (Excel)", command=self.open_file_dialog, height=40, fg_color="#1F6AA5")
        self.btn_import.grid(row=5, column=0, padx=20, pady=10, sticky="ew")
        
        self.lbl_file_name = ctk.CTkLabel(self.sidebar_frame, text="Chưa chọn file...", text_color="gray", wraplength=260)
        self.lbl_file_name.grid(row=6, column=0, padx=20, pady=(0, 20))
        
        self.btn_download_tpl = ctk.CTkButton(self.sidebar_frame, text="📥 Tải File Excel Mẫu", command=self.open_template_file, fg_color="gray", hover_color="#555555")
        self.btn_download_tpl.grid(row=7, column=0, padx=20, pady=10, sticky="ew")
        
        # Chế độ hiển thị Dark/Light
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Giao diện:", anchor="w")
        self.appearance_mode_label.grid(row=11, column=0, padx=20, pady=(10, 0), sticky="w")
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["System", "Light", "Dark"], command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=12, column=0, padx=20, pady=(5, 20), sticky="ew")
        
        # --- CỘT PHẢI: MAIN DASHBOARD ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(3, weight=1) # Khung báo cáo chiếm toàn bộ không gian thừa
        
        # Header chính
        self.title_lbl = ctk.CTkLabel(self.main_frame, text="🏠 Bảng Điều Khiển Phân Lịch Tối Ưu", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_lbl.grid(row=0, column=0, padx=10, pady=(10, 20), sticky="w")
        
        # Nút bắt đầu
        self.btn_run = ctk.CTkButton(
            self.main_frame, 
            text="⚡ BẮT ĐẦU PHÂN LỊCH CÔNG TÁC ⚡", 
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50, 
            fg_color="#2b9348", 
            hover_color="#007f5f",
            state="disabled",
            command=self.start_solving_thread
        )
        self.btn_run.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        # Progress Bar & Status
        self.progress_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.progress_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame)
        self.progress_bar.pack(fill="x", pady=(0, 5))
        self.progress_bar.set(0)
        
        self.lbl_status = ctk.CTkLabel(self.progress_frame, text="Trạng thái: Hãy chọn tệp Excel đầu vào...", text_color="#a3a3a3")
        self.lbl_status.pack(anchor="w")
        
        # Khung kết quả (Textbox & Stats)
        self.results_tabview = ctk.CTkTabview(self.main_frame)
        self.results_tabview.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")
        self.results_tabview.add("📋 Báo Cáo Kết Quả")
        self.results_tabview.add("ℹ Hướng dẫn Sử dụng")
        
        # Nội dung tab Hướng dẫn
        self.txt_guide = ctk.CTkTextbox(self.results_tabview.tab("ℹ Hướng dẫn Sử dụng"), font=ctk.CTkFont(size=13))
        self.txt_guide.pack(fill="both", expand=True, padx=10, pady=10)
        self.txt_guide.insert("0.0", """HƯỚNG DẪN SỬ DỤNG PHẦN MỀM PHÂN LỊCH CÔNG TÁC

Bước 1: Tải tệp mẫu
- Nhấn nút "📥 Tải File Excel Mẫu" để lấy file định dạng chuẩn. Điền Mã cửa hàng, Tên cửa hàng, Tọa độ (Vĩ độ, Kinh độ) và Địa chỉ vào tệp.

Bước 2: Khai báo đợt công tác
- Nhập tọa độ Khách sạn hoặc Văn phòng làm việc làm điểm xuất phát/kết thúc hàng ngày.
- Kéo thanh trượt để cài đặt số lượng nhân sự tham gia đi công tác.

Bước 3: Chọn tệp đầu vào
- Nhấn "📂 Chọn Tệp Cửa Hàng (Excel)" và tìm chọn tệp bạn vừa chuẩn bị. Hệ thống sẽ đọc số lượng cửa hàng hợp lệ.

Bước 4: Tính toán & Phân chia
- Nhấn nút "⚡ BẮT ĐẦU PHÂN LỊCH CÔNG TÁC ⚡". Thuật toán sẽ phân cụm địa lý và tối ưu hóa chuỗi đường đi thông minh.
- Sau khi chạy xong, bảng tóm tắt kết quả sẽ hiện ra.

Bước 5: Khai thác Kết quả
- Click "Mở Kết quả trên Excel": Windows tự bật file Excel chứa lộ trình từng ngày. Hãy thực hiện thao tác "Save As" để lưu lại.
- Click "Xem Bản Đồ Trực Quan": Bản đồ đường đi thực tế sẽ tự động mở trên trình duyệt web của bạn.
""")
        self.txt_guide.configure(state="disabled")
        
        # Nội dung tab Báo cáo
        self.report_frame = ctk.CTkFrame(self.results_tabview.tab("📋 Báo Cáo Kết Quả"), fg_color="transparent")
        self.report_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.txt_report = ctk.CTkTextbox(self.report_frame, font=ctk.CTkFont(family="Courier", size=13))
        self.txt_report.pack(fill="both", expand=True, pady=(0, 15))
        self.txt_report.insert("0.0", "Chưa có dữ liệu phân chia. Vui lòng chạy thuật toán...")
        self.txt_report.configure(state="disabled")
        
        # Khung các nút thao tác sau khi giải xong
        self.action_frame = ctk.CTkFrame(self.report_frame, fg_color="transparent")
        self.action_frame.pack(fill="x")
        self.action_frame.grid_columnconfigure(0, weight=1)
        self.action_frame.grid_columnconfigure(1, weight=1)
        
        self.btn_open_excel = ctk.CTkButton(self.action_frame, text="📊 Mở Excel Kết Quả", command=self.open_excel_report, height=45, fg_color="#8338ec", state="disabled")
        self.btn_open_excel.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        
        self.btn_open_map = ctk.CTkButton(self.action_frame, text="🗺 Xem Bản Đồ Đường Đi", command=self.open_map, height=45, fg_color="#ff006e", state="disabled")
        self.btn_open_map.grid(row=0, column=1, padx=(10, 0), sticky="ew")
        
    # ============ CÁC HÀM XỬ LÝ SỰ KIỆN UI ============
        
    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)
        
    def open_template_file(self):
        try:
            os.startfile(EXCEL_TEMPLATE_PATH)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể mở file mẫu. Đang tạo lại...\n{str(e)}")
            create_default_template()
            
    def open_file_dialog(self):
        file_types = [("Excel Files", "*.xlsx *.xls")]
        path = filedialog.askopenfilename(title="Chọn tệp chứa danh sách cửa hàng", filetypes=file_types)
        
        if path:
            self.input_file_path = path
            self.lbl_file_name.configure(text=os.path.basename(path), text_color="#52b788")
            self.lbl_status.configure(text="Đang kiểm tra định dạng file Excel...")
            
            try:
                logger.info(f"📂 Người dùng chọn nạp tệp Excel: {path}")
                self.stores_df = read_store_list(path)
                num_stores = len(self.stores_df)
                logger.info(f"✅ Tải Excel thành công! Tổng số dòng có tọa độ: {num_stores} dòng.")
                self.lbl_status.configure(text=f"✅ Đã tải thành công {num_stores} cửa hàng từ file Excel.", text_color="#2b9348")
                self.btn_run.configure(state="normal")
                
                # Chuyển sang tab báo cáo để chuẩn bị ghi
                self.results_tabview.set("📋 Báo Cáo Kết Quả")
            except Exception as e:
                logger.error(f"❌ Lỗi đọc file Excel người dùng cung cấp: {str(e)}")
                self.lbl_status.configure(text=f"❌ Lỗi đọc file: {str(e)}", text_color="#d90429")
                self.btn_run.configure(state="disabled")
                messagebox.showerror("Lỗi file Excel", str(e))

    def start_solving_thread(self):
        """Chạy thuật toán tối ưu trong luồng nền tránh đứng đơ UI"""
        # Đọc tọa độ nhập vào
        try:
            self.hotel_lat = float(self.lat_entry.get())
            self.hotel_lon = float(self.lon_entry.get())
        except ValueError:
            messagebox.showerror("Lỗi nhập liệu", "Vĩ độ và Kinh độ khách sạn phải là số hợp lệ!")
            return
            
        try:
            num_staff = int(self.staff_entry.get())
            if num_staff <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Lỗi nhập liệu", "Số lượng nhân sự phải là một số nguyên dương lớn hơn 0!")
            return
        
        logger.info(f"⚡ BẮT ĐẦU TIẾN TRÌNH PHÂN LỊCH MỚI:")
        logger.info(f"  - Khách sạn tọa độ: ({self.hotel_lat}, {self.hotel_lon})")
        logger.info(f"  - Số lượng nhân sự đăng ký: {num_staff}")
        logger.info(f"  - Tổng số cửa hàng cần đi: {len(self.stores_df)}")
        
        # Vô hiệu hóa nút nhấn để tránh click lặp lại
        self.btn_run.configure(state="disabled")
        self.btn_import.configure(state="disabled")
        self.btn_open_excel.configure(state="disabled")
        self.btn_open_map.configure(state="disabled")
        self.lbl_status.configure(text="🚀 Đang khởi động tiến trình tối ưu hóa...", text_color="#1F6AA5")
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start()
        
        # Khởi chạy Thread
        thread = threading.Thread(target=self.run_optimizer, args=(num_staff,))
        thread.daemon = True
        thread.start()
        
    def safe_update_status(self, msg, color=None):
        """Hàm cập nhật giao diện trạng thái an toàn từ Thread khác"""
        def _do_update():
            try:
                self.lbl_status.configure(text=msg)
                if color:
                    self.lbl_status.configure(text_color=color)
            except:
                pass
        self.after(0, _do_update)

    def run_optimizer(self, num_staff):
        try:
            import time
            self.safe_update_status("⚙️ Đang khởi động thuật toán Core VRP...")
            logger.info("🔄 [Thread 1] Chạy thuật toán tối ưu hóa VRP core...")
            time.sleep(0.25)
            
            # Định nghĩa hàm truyền tin từ solver lên GUI
            def update_gui_step(msg):
                self.safe_update_status(msg)
                time.sleep(0.25) # Tạo độ trễ nhỏ trực quan để người dùng theo dõi được các bước
                
            # Gọi giải thuật có truyền callback
            self.results, processed_df = optimize_schedule(
                self.hotel_lat, self.hotel_lon, self.stores_df, num_staff, 
                status_cb=update_gui_step
            )
            
            self.safe_update_status("📊 Bước 4/4: Đang thiết lập và đóng gói Excel chi tiết...")
            logger.info("🔄 [Thread 2] Xuất kết quả sang Excel tạm...")
            time.sleep(0.25)
            self.excel_path = export_results_and_open(self.results, self.stores_df)
            logger.info(f"  -> File Excel tạm sẵn sàng tại: {self.excel_path}")
            
            self.safe_update_status("🗺️ Đang tổng hợp và dựng bản đồ luồng Folium trực quan...")
            logger.info("🔄 [Thread 3] Sinh bản đồ Folium tĩnh...")
            time.sleep(0.25)
            self.map_path = generate_interactive_map(self.hotel_lat, self.hotel_lon, self.results)
            logger.info(f"  -> Bản đồ tạm sẵn sàng tại: {self.map_path}")
            
            # Cập nhật giao diện khi hoàn tất thành công
            logger.info("🎉 Giải toán và dựng tài nguyên nền HOÀN TẤT THÀNH CÔNG.")
            time.sleep(0.1)
            self.after(0, self.on_solve_success)
            
        except Exception as e:
            logger.error(f"❌ LỖI TRONG LUỒNG TỐI ƯU NỀN (Background Worker):", exc_info=True)
            # Cập nhật lỗi
            import traceback
            error_msg = traceback.format_exc()
            self.after(0, lambda: self.on_solve_failure(str(e)))
            
    def on_solve_success(self):
        self.progress_bar.stop()
        self.progress_bar.configure(mode="determinate")
        self.progress_bar.set(1.0)
        self.lbl_status.configure(text="🎉 Hoàn tất lập lịch công tác tối ưu!", text_color="#2b9348")
        
        self.btn_run.configure(state="normal")
        self.btn_import.configure(state="normal")
        self.btn_open_excel.configure(state="normal")
        self.btn_open_map.configure(state="normal")
        
        # Hiển thị báo cáo lên TextBox
        self.render_report_text()
        
    def on_solve_failure(self, error_txt):
        self.progress_bar.stop()
        self.progress_bar.configure(mode="determinate")
        self.progress_bar.set(0.0)
        self.lbl_status.configure(text=f"❌ Lỗi giải toán: {error_txt}", text_color="#d90429")
        
        self.btn_run.configure(state="normal")
        self.btn_import.configure(state="normal")
        
        messagebox.showerror("Lỗi tiến trình", f"Đã phát sinh lỗi khi thực hiện phân bổ:\n{error_txt}")
        
    def render_report_text(self):
        """Kết xuất chuỗi định dạng báo cáo lên giao diện"""
        if not self.results:
            return
            
        summary = self.results['summary']
        
        report = []
        report.append("=================================================================")
        report.append(f"📊 BÁO CÁO TÓM TẮT KẾT QUẢ PHÂN LỊCH")
        report.append("=================================================================")
        report.append(f"{'Nhân sự':<18} | {'Số CH':<8} | {'Số Ngày':<10} | {'Tổng Quãng Đường':<20}")
        report.append("-" * 65)
        
        tot_dist = 0
        tot_days = 0
        tot_stores = 0
        
        for item in summary:
            emp = item['Nhân viên']
            stores = item['Số cửa hàng']
            days = item['Số ngày đi']
            dist = item['Tổng quãng đường (km)']
            
            tot_dist += dist
            tot_days += days
            tot_stores += stores
            
            report.append(f"{emp:<18} | {stores:<8} | {days:<10} | {dist:<20,.2f} km")
            
        report.append("-" * 65)
        report.append(f"{'TỔNG CỘNG':<18} | {tot_stores:<8} | {tot_days:<10} | {tot_dist:<20,.2f} km")
        
        # Tính chênh lệch tải trọng
        distances = [item['Tổng quãng đường (km)'] for item in summary]
        if len(distances) > 1:
            diff = max(distances) - min(distances)
            report.append(f"⚖️ Độ chênh lệch quãng đường lớn nhất giữa các nhân viên: {diff:.2f} km")
            
        report.append("\n💡 Click các nút phía dưới để mở dữ liệu chi tiết Excel hoặc xem Bản đồ.")
        
        report_str = "\n".join(report)
        
        self.txt_report.configure(state="normal")
        self.txt_report.delete("0.0", "end")
        self.txt_report.insert("0.0", report_str)
        self.txt_report.configure(state="disabled")
        
    def open_excel_report(self):
        if self.excel_path and os.path.exists(self.excel_path):
            logger.info(f"🚀 Người dùng bấm xem Excel -> Đang khởi chạy tệp: {self.excel_path}")
            self.lbl_status.configure(text="🚀 Đang khởi động Microsoft Excel...")
            try:
                os.startfile(self.excel_path)
                self.lbl_status.configure(text="✅ Excel đã mở ngay lập tức! Hãy lưu lại bằng Save As.", text_color="#2b9348")
            except Exception as e:
                logger.error(f"Không thể mở Excel qua hệ thống: {str(e)}")
                messagebox.showerror("Lỗi", f"Không thể mở Excel: {str(e)}")
        else:
            logger.warning("Người dùng bấm mở Excel nhưng không tìm thấy file excel_path hợp lệ.")
            messagebox.showerror("Chưa có dữ liệu", "Tệp tin Excel chưa sẵn sàng hoặc đã bị xóa tạm thời!")
                
    def open_map(self):
        if self.map_path and os.path.exists(self.map_path):
            logger.info(f"🚀 Người dùng bấm xem Bản đồ -> Đang mở trình duyệt web tệp: {self.map_path}")
            self.lbl_status.configure(text="🚀 Đang mở Bản đồ trên Trình duyệt của bạn...")
            try:
                import webbrowser
                webbrowser.open('file://' + os.path.realpath(self.map_path))
                self.lbl_status.configure(text="✅ Đã mở bản đồ tức thì trên trình duyệt web.", text_color="#2b9348")
            except Exception as e:
                logger.error(f"Không thể mở trình duyệt web: {str(e)}")
                messagebox.showerror("Lỗi", f"Không thể mở trình duyệt: {str(e)}")
        else:
            logger.warning("Người dùng bấm xem Bản đồ nhưng không thấy file map_path hợp lệ.")
            messagebox.showerror("Chưa có dữ liệu", "Bản đồ chưa được dựng sẵn thành công!")
