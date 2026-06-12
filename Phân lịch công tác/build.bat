@echo off
chcp 65001 > nul
echo =====================================================================
echo 📦 TIẾN TRÌNH ĐÓNG GÓI ỨNG DỤNG TRIPSCHEDULER PRO THÀNH FILE EXE 📦
echo =====================================================================

:: Đi vào thư mục chứa file bat
cd /d "%~dp0"

:: Sử dụng đường dẫn tương đối đến môi trường ảo để tránh lỗi font chữ Tiếng Việt
set PYTHON_EXE=..\venv\Scripts\python.exe
set PYINSTALLER_EXE=..\venv\Scripts\pyinstaller.exe

if not exist "%PYTHON_EXE%" (
    echo [LỖI] Không tìm thấy môi trường ảo Python tại: ..\venv
    echo Vui lòng kiểm tra lại thư mục venv nằm cạnh thư mục dự án.
    pause
    exit /b
)

echo.
echo [1/3] Đang cài đặt/Cập nhật thư viện PyInstaller trong venv...
"%PYTHON_EXE%" -m pip install pyinstaller --quiet

echo.
echo [2/3] Đang khởi chạy đóng gói phần mềm bằng PyInstaller...
echo Vui lòng chờ trong giây lát (quá trình này có thể mất 1-2 phút)...
echo.

:: Lệnh build độc lập:
:: -w: Không hiện màn hình console CMD màu đen khi bật phần mềm
:: -F: Gom tất cả thành 1 file EXE duy nhất
:: --collect-all: Thu thập đầy đủ data/thư viện phụ trợ cho customtkinter và folium
:: --add-data: Bao gồm thư mục templates mẫu vào file exe
"%PYINSTALLER_EXE%" --noconfirm --onedir --windowed ^
    --name "TripSchedulerPro" ^
    --add-data "templates;templates" ^
    --collect-all customtkinter ^
    --collect-all folium ^
    --collect-all jinja2 ^
    --collect-all openpyxl ^
    --collect-all pandas ^
    "run.py"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo =====================================================================
    echo ✅ ĐÓNG GÓI THÀNH CÔNG!
    echo Tệp tin ứng dụng nằm trong thư mục: dist\TripSchedulerPro\TripSchedulerPro.exe
    echo Bạn có thể nén cả thư mục "TripSchedulerPro" này gửi sang máy khác để chạy.
    echo =====================================================================
) else (
    echo.
    echo ❌ [LỖI] Tiến trình đóng gói thất bại. Xem log lỗi phía trên.
)

pause
