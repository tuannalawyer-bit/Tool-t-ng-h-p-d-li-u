@echo off
chcp 65001 >nul
title CHAY PHAN MEM
set APP_DIR=%LOCALAPPDATA%\TDMB_Tool
set PY_EXE=%APP_DIR%\Python_Embedded\python.exe
if not exist "%PY_EXE%" (
    color 0c
    echo =============================================
    echo [!] CHUA TIM THAY HE THONG LOI!
    echo Hay chay file 'INSTALL.bat' truoc do it nhat 1 lan.
    echo =============================================
    pause
    exit
)
echo [+] Dang khoi dong phan mem...
cd /d "%APP_DIR%"
start "" "%PY_EXE%" "email_tool.py"
exit
