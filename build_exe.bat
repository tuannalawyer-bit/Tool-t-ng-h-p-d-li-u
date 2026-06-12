@echo off
echo ==============================================================
echo    SMARTSLIDE STUDIO - HE THONG DONG GOI PHAN MEM (.EXE)
echo ==============================================================
echo.
echo Buoc 1: Dang cai dat PyInstaller...
call .\venv\Scripts\activate
pip install pyinstaller

echo.
echo Buoc 2: Dang tien hanh dong goi ung dung (Che do khong hien cua so lenh CMD)...
pyinstaller --noconsole --onefile --name "SmartSlide_Studio" ^
  --add-data "templates;templates" ^
  app_gui.py

echo.
echo ==============================================================
echo   HOAN TAT! Tep tin SmartSlide_Studio.exe nam trong thu muc 'dist'
echo ==============================================================
pause
