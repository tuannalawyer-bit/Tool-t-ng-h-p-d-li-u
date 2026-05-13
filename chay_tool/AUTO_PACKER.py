import os
import sys
import shutil
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import zipfile
from datetime import datetime
import re

# --- CẤU HÌNH HỆ THỐNG ---
SOURCE_FILES = ["email_tool.py", "core_logic.py", "form tool.xlsx"]
MONITOR_FILES = ["email_tool.py", "core_logic.py"] # Files giám sát thay đổi
DIST_DIR = "DISTRIBUTION"
VERSIONS_DIR = "Versions"

# Đảm bảo chạy đúng thư mục dự án
APP_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(APP_DIR)

class AutoPackerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TĐMB - AUTO PACKER & RELEASE BUILDER")
        self.root.geometry("580x480")
        self.root.resizable(False, False)
        
        # Dark theme config for window
        self.root.configure(bg="#f0f0f0")
        
        self.is_running = False
        self.monitor_thread = None
        self.last_mtimes = {}
        
        self.setup_ui()
        self.log("Hệ thống sẵn sàng. Nhấn 'BẮT ĐẦU THEO DÕI' để kích hoạt.")
        self.log(f"Thư mục gốc: {APP_DIR}")

    def setup_ui(self):
        # Header Title
        lbl_header = tk.Label(self.root, text="HỆ THỐNG ĐÓNG GÓI TỰ ĐỘNG (CI/CD MINI)", font=("Segoe UI", 14, "bold"), fg="#2c3e50", bg="#f0f0f0")
        lbl_header.pack(pady=(15, 5))

        # Status Indicator
        status_frame = tk.Frame(self.root, bg="#ffffff", bd=1, relief="solid")
        status_frame.pack(pady=5, fill="x", padx=20)
        
        self.status_label = tk.Label(status_frame, text="TRẠNG THÁI: ĐANG DỪNG 🔴", font=("Segoe UI", 12, "bold"), fg="#e74c3c", bg="#ffffff", pady=10)
        self.status_label.pack()

        # Controls Frame
        ctrl_frame = tk.Frame(self.root, bg="#f0f0f0")
        ctrl_frame.pack(pady=15)

        btn_style = {"font": ("Segoe UI", 10, "bold"), "padx": 15, "pady": 8, "cursor": "hand2"}

        self.btn_start = tk.Button(ctrl_frame, text="▶ BẮT ĐẦU THEO DÕI", bg="#2ecc71", fg="white", 
                                    command=self.start_monitoring, **btn_style)
        self.btn_start.grid(row=0, column=0, padx=10)

        self.btn_stop = tk.Button(ctrl_frame, text="⏹ DỪNG LẠI", bg="#bdc3c7", fg="white", state="disabled",
                                   command=self.stop_monitoring, **btn_style)
        self.btn_stop.grid(row=0, column=1, padx=10)

        # Log Area
        log_frame = tk.Frame(self.root, bg="#f0f0f0")
        log_frame.pack(fill="both", expand=True, padx=20, pady=5)
        
        log_label = tk.Label(log_frame, text="Lịch sử tiến trình:", font=("Segoe UI", 9, "italic"), bg="#f0f0f0")
        log_label.pack(anchor="w")
        
        scrollbar = tk.Scrollbar(log_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.txt_log = tk.Text(log_frame, height=12, font=("Consolas", 9), bg="#2d3436", fg="#dfe6e9", 
                               yscrollcommand=scrollbar.set, wrap="word")
        self.txt_log.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.txt_log.yview)
        
        # Manual & Config Frame
        bottom_frame = tk.Frame(self.root, bg="#f0f0f0")
        bottom_frame.pack(pady=(10, 15), fill="x", padx=20)
        
        btn_manual = tk.Button(bottom_frame, text="⚡ Đóng gói Ngay lập tức (Thủ công)", bg="#3498db", fg="white", 
                                font=("Segoe UI", 10, "bold"), pady=8, command=self.do_pack, cursor="hand2")
        btn_manual.pack(side="left", fill="x", expand=True)

    def log(self, message):
        ts = datetime.now().strftime("%H:%M:%S")
        msg = f"[{ts}] {message}\n"
        self.txt_log.config(state="normal")
        self.txt_log.insert(tk.END, msg)
        self.txt_log.see(tk.END)
        self.txt_log.config(state="disabled")

    def start_monitoring(self):
        self.is_running = True
        self.btn_start.config(state="disabled", bg="#bdc3c7")
        self.btn_stop.config(state="normal", bg="#e74c3c")
        self.status_label.config(text="TRẠNG THÁI: ĐANG GIÁM SÁT... 🟢", fg="#27ae60")
        self.log("🚀 Bắt đầu chế độ Auto-Pack. Hệ thống đang canh gác code...")
        
        # Khởi tạo cache mtime hiện tại của các file
        for f in MONITOR_FILES:
            if os.path.exists(f):
                self.last_mtimes[f] = os.path.getmtime(f)
            else:
                self.last_mtimes[f] = 0
        
        # Chạy nền giám sát
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()

    def stop_monitoring(self):
        self.is_running = False
        self.btn_start.config(state="normal", bg="#2ecc71")
        self.btn_stop.config(state="disabled", bg="#bdc3c7")
        self.status_label.config(text="TRẠNG THÁI: ĐANG DỪNG 🔴", fg="#e74c3c")
        self.log("🛑 Đã tắt chế độ giám sát.")

    def monitor_loop(self):
        while self.is_running:
            try:
                changed = False
                for f in MONITOR_FILES:
                    if not os.path.exists(f): continue
                    current_mtime = os.path.getmtime(f)
                    if f not in self.last_mtimes:
                        self.last_mtimes[f] = current_mtime
                    elif current_mtime > self.last_mtimes[f]:
                        self.last_mtimes[f] = current_mtime
                        changed = True
                        
                if changed:
                    self.root.after(0, self.log, "🔔 Phát hiện sửa đổi file! Chờ 5s ổn định để đóng gói...")
                    time.sleep(5) # Cooldown 5 seconds
                    
                    # Kiểm tra lại xem trong lúc chờ có lưu tiếp ko
                    further_change = False
                    for f in MONITOR_FILES:
                         if os.path.exists(f) and os.path.getmtime(f) > self.last_mtimes[f]:
                             further_change = True
                             self.last_mtimes[f] = os.path.getmtime(f)
                    
                    if further_change:
                        self.root.after(0, self.log, "⏳ Vẫn đang có chỉnh sửa. Lùi tiến trình lại...")
                        continue # Chạy lại vòng lặp chờ
                        
                    # Đã ổn định -> Triển khai đóng gói
                    self.root.after(0, self.do_pack)
                
                time.sleep(2) # Quét mỗi 2 giây để tiết kiệm tài nguyên
            except Exception as e:
                self.root.after(0, self.log, f"⚠ LỖI PHÁT SINH: {str(e)}")
                time.sleep(3)

    def get_next_version(self):
        if not os.path.exists(VERSIONS_DIR):
            os.makedirs(VERSIONS_DIR)
            return "2.6.0"
        
        folders = os.listdir(VERSIONS_DIR)
        # Regex tìm các pattern vX.Y hoặc vX.Y.Z
        pattern = re.compile(r"v(\d+)\.(\d+)(\.(\d+))?")
        
        max_major, max_minor, max_patch = 2, 5, 0 # Giá trị cơ sở hiện tại
        
        for f in folders:
            match = pattern.search(f)
            if match:
                try:
                    major = int(match.group(1))
                    minor = int(match.group(2))
                    patch = int(match.group(4)) if match.group(4) else 0
                    
                    if (major, minor, patch) > (max_major, max_minor, max_patch):
                        max_major, max_minor, max_patch = major, minor, patch
                except ValueError:
                    continue
        
        # Tăng Patch lên 1 cho bản Build tự động
        new_patch = max_patch + 1
        return f"{max_major}.{max_minor}.{new_patch}"

    def update_install_bat_version(self, version):
        bat_path = os.path.join(DIST_DIR, "INSTALL.bat")
        if not os.path.exists(bat_path):
            self.log("⚠ Cảnh báo: Không tìm thấy INSTALL.bat trong DISTRIBUTION để cập nhật.")
            return
        
        try:
            with open(bat_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Regex để thay thế linh động version cũ sang mới
            # Tìm format "TĐMB TOOL vX.Y" hoặc "TĐMB TOOL vX.Y.Z"
            new_content = re.sub(r"TĐMB TOOL v\d+\.\d+(\.\d+)?", f"TĐMB TOOL v{version}", content)
            
            with open(bat_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            self.log("📝 Đã cập nhật phiên bản hiển thị trong INSTALL.bat")
        except Exception as e:
            self.log(f"⚠ Không thể sửa INSTALL.bat: {str(e)}")

    def do_pack(self):
        try:
            self.log("🛠 ĐANG BẮT ĐẦU ĐÓNG GÓI DỰ ÁN...")
            
            # Xác định version
            next_ver = self.get_next_version()
            self.log(f"📌 Version dự kiến: v{next_ver}")
            
            # 1. Tạo/Cập nhật thư mục DISTRIBUTION
            if not os.path.exists(DIST_DIR):
                os.makedirs(DIST_DIR)
                
            self.log("📂 1/4 Đang đồng bộ mã nguồn sang thư mục DISTRIBUTION...")
            for f in SOURCE_FILES:
                src_p = os.path.join(APP_DIR, f)
                if os.path.exists(src_p):
                    shutil.copy2(src_p, os.path.join(DIST_DIR, f))
            
            # 2. Cập nhật INSTALL.bat
            self.log("✏ 2/4 Đang ghi đè thông tin phiên bản...")
            self.update_install_bat_version(next_ver)
            
            # 3. Tạo thư mục lưu trữ trong Versions
            dt_str = datetime.now().strftime("%Y%m%d_%H%M")
            ver_folder_name = f"v{next_ver}_Autobuild_{dt_str}"
            target_dir = os.path.join(VERSIONS_DIR, ver_folder_name)
            
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
                
            # 4. Nén Zip
            self.log("🗜 3/4 Đang nén gói cài đặt ZIP...")
            zip_name = f"TDMB_Installer_v{next_ver}.zip"
            zip_final_path = os.path.join(target_dir, zip_name)
            
            with zipfile.ZipFile(zip_final_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root_p, dirs, files in os.walk(DIST_DIR):
                    for file in files:
                        full_path = os.path.join(root_p, file)
                        # Lưu dưới dạng thư mục con gốc để khi giải nén ko bị lộn xộn
                        rel_path = os.path.relpath(full_path, DIST_DIR)
                        zipf.write(full_path, rel_path)
            
            # 5. Đồng bộ ra DISTRIBUTION.zip ở thư mục gốc (Bản mới nhất)
            shutil.copy2(zip_final_path, os.path.join(APP_DIR, "DISTRIBUTION.zip"))
            
            self.log("✨ 4/4 Hoàn tất đồng bộ DISTRIBUTION.zip ở gốc.")
            self.log(f"✅ THÀNH CÔNG! Đã tạo bản build tại:")
            self.log(f"👉 Versions/{ver_folder_name}/{zip_name}")
            self.log("--------------------------------------------------")
            
        except Exception as e:
            self.log(f"❌ LỖI ĐÓNG GÓI: {str(e)}")

if __name__ == "__main__":
    # Thiết lập DPI aware cho font đẹp trên Windows
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
        
    root = tk.Tk()
    app = AutoPackerGUI(root)
    root.mainloop()
