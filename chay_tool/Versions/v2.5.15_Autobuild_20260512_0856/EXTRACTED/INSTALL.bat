@echo off
chcp 65001 >nul
title BỘ CÀI ĐẶT TỰ ĐỘNG - EMAIL DATA EXTRACTOR
echo ============================================================
echo          BỘ CÀI ĐẶT TỰ ĐỘNG - TĐMB TOOL v2.5.15
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

powershell -ExecutionPolicy Bypass -WindowStyle Normal -Command "& {[System.Console]::OutputEncoding = [System.Text.Encoding]::UTF8; $appDir = '%APP_DIR%'; Write-Host '--- Đang chạy Trình kiểm tra Thông minh (Web Installer) ---' -ForegroundColor Cyan; try { $pyPath = Join-Path $appDir 'Python_Embedded'; $pyExe = Join-Path $pyPath 'python.exe'; $pipExe = Join-Path $pyPath 'Scripts\pip.exe'; if (-not (Test-Path $pyExe)) { Write-Host '[1/3] Tải và cài đặt Python Core...' -ForegroundColor Cyan; $pyZip = Join-Path $appDir 'py.zip'; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.10.11/python-3.10.11-embed-amd64.zip' -OutFile $pyZip; Add-Type -AssemblyName System.IO.Compression.FileSystem; if (Test-Path $pyPath) { Remove-Item -Recurse -Force $pyPath }; [System.IO.Compression.ZipFile]::ExtractToDirectory($pyZip, $pyPath); Remove-Item $pyZip; $pth = Join-Path $pyPath 'python310._pth'; (Get-Content $pth) | ForEach-Object { $_ -replace '#import site', 'import site' } | Set-Content $pth; } else { Write-Host '[✓] Python Core đã có sẵn trên hệ thống.' -ForegroundColor Green; } if (-not (Test-Path $pipExe)) { Write-Host '[2/3] Khởi tạo công cụ quản lý thư viện Pip...' -ForegroundColor Cyan; $getpip = Join-Path $pyPath 'get-pip.py'; Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile $getpip; & $pyExe $getpip --no-warn-script-location; Remove-Item $getpip; } else { Write-Host '[✓] Hệ thống Pip đã sẵn sàng.' -ForegroundColor Green; } Write-Host '[3/3] Kiểm tra các gói thư viện của ứng dụng...' -ForegroundColor Cyan; $libCheck = 'import openpyxl, extract_msg, easyocr, bs4, lxml, google.genai, cv2, numpy, PIL'; & $pyExe -c $libCheck 2>$null; if ($LastExitCode -ne 0) { Write-Host '    -> [!] Phát hiện thiếu thư viện. Đang cài đặt bổ sung...' -ForegroundColor Yellow; & $pipExe install --no-cache-dir openpyxl extract_msg easyocr beautifulsoup4 lxml google-genai opencv-python numpy pillow; } else { Write-Host '    -> [✓] Hoàn hảo! Tất cả thư viện đã đầy đủ.' -ForegroundColor Green; } Write-Host '[*] Đang đồng bộ phím tắt ứng dụng ngoài Desktop...' -ForegroundColor Gray; $wsh = New-Object -ComObject WScript.Shell; $desktop = [System.Environment]::GetFolderPath('Desktop'); $sc = $wsh.CreateShortcut((Join-Path $desktop 'Chạy Tool TĐMB.lnk')); $sc.TargetPath = $pyExe; $sc.Arguments = '\"' + (Join-Path $appDir 'email_tool.py') + '\"'; $sc.WorkingDirectory = $appDir; $sc.IconLocation = 'shell32.dll,43'; $sc.Save(); Write-Host '====================================================' -ForegroundColor Green; Write-Host '✅ XỬ LÝ THÀNH CÔNG!' -ForegroundColor Green; Write-Host '👉 Phần mềm đã sẵn sàng trên màn hình Desktop.' -ForegroundColor Green; Write-Host '====================================================' -ForegroundColor Green; } catch { Write-Host '❌ LỖI PHÁT SINH: ' $_ -ForegroundColor Red; pause } }"

echo.
echo [*] Đang dọn dẹp tài nguyên tạm...
echo.
echo ============================================================
echo NHẤN PHÍM BẤT KỲ ĐỂ KẾT THÚC VÀ SỬ DỤNG PHẦN MỀM!
echo ============================================================
pause >nul
