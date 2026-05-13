@echo off
chcp 65001 >nul
title BỘ CÀI ĐẶT TỰ ĐỘNG - EMAIL DATA EXTRACTOR
echo ============================================================
echo          BỘ CÀI ĐẶT TỰ ĐỘNG - TĐMB TOOL v2.5.1
echo ============================================================
echo [*] Bắt đầu quá trình cài đặt thông minh...
echo [*] Quá trình sẽ tự động tải và cấu hình hệ thống ngầm.
echo [*] Xin vui lòng KHÔNG ĐÓNG cửa sổ này cho đến khi hoàn tất.
echo.

set APP_DIR=%LOCALAPPDATA%\TDMB_Tool
echo [+] Vị trí cài đặt: %APP_DIR%
if not exist "%APP_DIR%" mkdir "%APP_DIR%"

echo [+] Đang sao chép mã nguồn ứng dụng...
copy /Y "email_tool.py" "%APP_DIR%\" >nul
copy /Y "core_logic.py" "%APP_DIR%\" >nul
copy /Y "form tool.xlsx" "%APP_DIR%\" >nul

echo [+] Khởi động trình tải xuống thông minh (Web Installer)...
echo.

powershell -ExecutionPolicy Bypass -WindowStyle Normal -Command "& {[System.Console]::OutputEncoding = [System.Text.Encoding]::UTF8; $appDir = '%APP_DIR%'; Write-Host '--- Đang tải và cài đặt ---' -ForegroundColor Cyan; try { $pyZip = Join-Path $appDir 'py.zip'; $pyPath = Join-Path $appDir 'Python_Embedded'; if (-not (Test-Path $pyPath)) { Write-Host '[1/4] Tải xuống Embedded Python...'; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.10.11/python-3.10.11-embed-amd64.zip' -OutFile $pyZip; Write-Host '[2/4] Đang giải nén Python...'; Add-Type -AssemblyName System.IO.Compression.FileSystem; [System.IO.Compression.ZipFile]::ExtractToDirectory($pyZip, $pyPath); Remove-Item $pyZip; $pth = Join-Path $pyPath 'python310._pth'; (Get-Content $pth) | ForEach-Object { $_ -replace '#import site', 'import site' } | Set-Content $pth; Write-Host '    - Cài đặt Pip...'; $getpip = Join-Path $pyPath 'get-pip.py'; Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile $getpip; & (Join-Path $pyPath 'python.exe') $getpip --no-warn-script-location; Remove-Item $getpip; } else { Write-Host '[1/2] Python đã tồn tại, bỏ qua bước tải.' } Write-Host '[3/4] Đang tự động cài đặt Thư viện (ngầm)...'; $pip = Join-Path $pyPath 'Scripts\pip.exe'; & $pip install --no-cache-dir openpyxl extract_msg easyocr beautifulsoup4 lxml google-genai opencv-python numpy pillow; Write-Host '[4/4] Tạo Shortcut màn hình Desktop...'; $wsh = New-Object -ComObject WScript.Shell; $desktop = [System.Environment]::GetFolderPath('Desktop'); $sc = $wsh.CreateShortcut((Join-Path $desktop 'Chạy Tool TĐMB.lnk')); $sc.TargetPath = Join-Path $pyPath 'python.exe'; $sc.Arguments = '\"' + (Join-Path $appDir 'email_tool.py') + '\"'; $sc.WorkingDirectory = $appDir; $sc.IconLocation = 'shell32.dll,43'; $sc.Save(); Write-Host '====================================================' -ForegroundColor Green; Write-Host '✅ CÀI ĐẶT THÀNH CÔNG RỰC RỠ!' -ForegroundColor Green; Write-Host '👉 Bạn có thể mở phần mềm ngay từ màn hình Desktop.' -ForegroundColor Green; Write-Host '====================================================' -ForegroundColor Green; } catch { Write-Host '❌ LỖI TRONG QUÁ TRÌNH CÀI ĐẶT: ' $_ -ForegroundColor Red; pause } }"

echo.
echo [*] Đang dọn dẹp tài nguyên tạm...
echo.
echo ============================================================
echo NHẤN PHÍM BẤT KỲ ĐỂ KẾT THÚC VÀ SỬ DỤNG PHẦN MỀM!
echo ============================================================
pause >nul
