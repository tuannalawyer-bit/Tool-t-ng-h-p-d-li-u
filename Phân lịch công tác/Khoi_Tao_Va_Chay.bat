@echo off
setlocal enabledelayedexpansion

echo =====================================================================
echo  TRIPSCHEDULER PRO - CHU TRINH KHOI DONG NHANH 100%% PORTABLE
echo =====================================================================
echo.

:: Di vao thu muc hien tai
cd /d "%~dp0"

:: 1. KIEM TRA KHO TAI NGUYEN NHUNG SAN
echo [*] Dang thiet lap tai nguyen he thong tu kho Portable...

if exist "python_portable\python.exe" (
    echo [+] Tim thay dong co Python Portable khep kin!
    echo [+] Trang thai tai nguyen: Toan ven va San sang 100%% [Khong can cai dat].
    echo.
    goto :deploy_done
)

echo [!] Canh bao: Khong tim thay kho Portable mac dinh. 
echo [*] Dang kich hoat trinh cai dat truyen thong du phong...
echo.

:: --- DU PHONG: LOGIC CAI DAT CUA PHIEN BAN TRUOC ---
set "PYTHON_BIN=python"
!PYTHON_BIN! -c "import sys" >nul 2>&1
if !ERRORLEVEL! EQU 0 goto :python_ok

for /d %%d in ("%LocalAppData%\Programs\Python\Python*") do (
    if exist "%%d\python.exe" (
        set "PYTHON_BIN=%%d\python.exe"
        goto :python_ok
    )
)

echo [LOI] Khong tim thay ca kho Portable va he thong Python cai san tren may!
pause
exit /b

:python_ok
if not exist "venv" (
    echo [*] Dang tao moi truong ao 'venv' du phong...
    "!PYTHON_BIN!" -m venv venv
)
"%~dp0venv\Scripts\pip.exe" install --no-index --find-links="%~dp0wheels" -r requirements.txt --quiet
goto :deploy_done

:deploy_done
:: 2. TU DONG TAO LOI TAT DESKTOP
echo [*] Dang thiet lap loi tat Shortcut ra man hinh Desktop...
powershell -ExecutionPolicy Bypass -File "app\create_shortcut.ps1" >nul 2>&1
echo [+] Da hoan tat dang ky phan mem voi Windows.

echo.
echo =====================================================================
echo  KHOI TAO THANH CONG MY MAN TRONG 1 GIAY!
echo  CHUONG TRINH SE TU DONG KHOI CHAY BAY GIO...
echo =====================================================================
echo.
timeout /t 2 > nul

:: KHOI CHAY UNG DUNG
start "" "%~dp0Chay_Phan_Mem.bat"
exit
