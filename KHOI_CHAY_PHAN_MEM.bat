@echo off
title KHOI CHAY SMARTSLIDE STUDIO v1.5
echo ==============================================================
echo    DANG KHOI DONG HE THONG TRO LY SLIDE THONG MINH...
echo ==============================================================
echo.
cd /d "%~dp0"
start "" /b ".\venv\Scripts\pythonw.exe" app_gui.py
echo.
echo [+] DA KICH HOAT UNG DUNG THANH CONG! Giao dien dang hien len...
echo [!] Thong bao: Ban co the dong cua so den nay lai va su dung app binh thuong.
echo ==============================================================
timeout /t 3 >nul
exit
