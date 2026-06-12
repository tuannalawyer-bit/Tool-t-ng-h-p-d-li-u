@echo off
cd /d "%~dp0"

:: 1. QUET UU TIEN TUYET DOI: Bo Python Portable nhung san (Chien luoc Zero-Admin)
if exist "python_portable\pythonw.exe" (
    start "" "python_portable\pythonw.exe" "run.py"
    exit
)

:: 2. QUET DU PHONG: Moi truong ao tai cho (Cho cac ban cu hoac moi truong cu)
if exist "venv\Scripts\pythonw.exe" (
    start "" "venv\Scripts\pythonw.exe" "run.py"
    exit
)

:: 3. QUET DU PHONG 2: Moi truong ao thu muc cha (Cho may DEV lap trinh)
if exist "..\venv\Scripts\pythonw.exe" (
    start "" "..\venv\Scripts\pythonw.exe" "run.py"
    exit
)

:: 4. PHUONG AN KHAN CAP: Bao loi neu thieu tai nguyen
echo ===============================================================
echo [LOI] Khong tim thay he thong Python kha dung!
echo ===============================================================
echo.
echo Vui long click dup chay tep tin "Khoi_Tao_Va_Chay.bat" truoc
echo de he thong tu dong chuan bi tai nguyen va cau hinh nhe!
echo.
pause
exit
