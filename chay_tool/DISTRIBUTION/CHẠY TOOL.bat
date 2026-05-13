@echo off
chcp 65001 >nul
title MỞ PHẦN MỀM TĐMB

:: Định vị thư mục cài đặt tập trung
set APP_DIR=%LOCALAPPDATA%\TDMB_Tool
set PY_EXE=%APP_DIR%\Python_Embedded\python.exe

echo ============================================================
echo              HỆ THỐNG KHỞI ĐỘNG PHẦN MỀM
echo ============================================================
echo.

:: Kiểm tra sự tồn tại của lõi Python
if not exist "%PY_EXE%" (
    color 0c
    echo  [!] CẢNH BÁO: Chưa tìm thấy hệ thống lõi.
    echo  👉 Bạn CẦN CHẠY file 'INSTALL.bat' trước ít nhất một lần!
    echo.
    pause
    exit
)

echo [+] Đang khởi động phần mềm, xin vui lòng chờ...
echo.

:: Chuyển vào thư mục ứng dụng và chạy bằng luồng ngầm Python
cd /d "%APP_DIR%"
start "" "%PY_EXE%" "%APP_DIR%\email_tool.py"

echo ✅ Thành công! Cửa sổ phần mềm đang được mở...
echo Tự động đóng cửa sổ này sau 3 giây.
timeout /t 3 >nul
exit
