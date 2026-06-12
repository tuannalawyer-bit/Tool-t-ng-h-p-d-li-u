@echo off
title May Chu Ban Do Quy Hoach
echo =========================================================
echo      MAY CHU KHOI DONG BAN DO QUY HOACH (ANTIGRAVITY)
echo =========================================================
echo.
echo 1. Dang tu dong mo Trinh duyet...
echo 2. Dang bat may chu tai Cong 8080 de tai du lieu ban do...
echo.
echo [CHU Y]: Hay cu de cua so nay chay ngam de duy tri ban do.
echo          Sau khi xem xong, hay tat no di.
echo.

:: Mo trinh duyet truoc de chuan bi don nhan ket noi tu server
start "" "http://localhost:8080"

:: Chay 1 instance duy nhat cua python tre 8080 de load map on dinh
python -m http.server 8080
pause
