import sys
import os

# Đảm bảo thư mục gốc dự án nằm trong PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.gui import TripSchedulerApp

def main():
    try:
        app = TripSchedulerApp()
        app.mainloop()
    except Exception as e:
        import traceback
        print("Đã xảy ra lỗi hệ thống khi khởi động ứng dụng:")
        traceback.print_exc()
        input("\nNhấn phím Enter để thoát...")

if __name__ == "__main__":
    main()
