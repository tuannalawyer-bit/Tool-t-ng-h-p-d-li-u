@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo Dang vao thu muc emails de khoi phuc trang thai...
pushd "emails"

echo Dang xoa trang thai "done_" va "failed_" cua cac file...
for %%f in (done_*.msg) do (
    set "filename=%%~nxf"
    setlocal enabledelayedexpansion
    ren "%%f" "!filename:done_=!"
    endlocal
)

for %%f in (failed_*.msg) do (
    set "filename=%%~nxf"
    setlocal enabledelayedexpansion
    ren "%%f" "!filename:failed_=!"
    endlocal
)

popd

echo.
echo Da xoa xong! Ban co the chay lai tool de trich xuat lai tu dau.
timeout /t 2 > nul
exit
