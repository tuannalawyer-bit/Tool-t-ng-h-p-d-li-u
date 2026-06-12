@echo off
set "BASE_DIR=%USERPROFILE%\.gemini"
echo --- QUY TRINH KHOI PHUC 2500 TIN NHAN ---
echo.
echo [1/3] Dang tieu diet cac tien trinh...
taskkill /f /im antigravity* /t >nul 2>&1
timeout /t 2 /nobreak >nul
echo [2/3] Dang hoan doi du lieu...
if exist "%BASE_DIR%\antigravity_restore" (
    if exist "%BASE_DIR%\antigravity" rmdir /s /q "%BASE_DIR%\antigravity"
    ren "%BASE_DIR%\antigravity_restore" "antigravity"
    echo    =^> Da khoi phuc 2500 tin nhan.
) else (
    echo Khong tim thay thu muc restore! Co ve ban da thiet lap roi.
)
echo [3/3] Dang sua loi file cau hinh (mcp_config)...
echo { > "%BASE_DIR%\antigravity\mcp_config.json"
echo   "mcpServers": {} >> "%BASE_DIR%\antigravity\mcp_config.json"
echo } >> "%BASE_DIR%\antigravity\mcp_config.json"
echo.
echo ======================================================
echo    DA KHOI PHUC THANH CONG! 
echo    Bay gio ban hay mo lai VS Code. 
echo    Ban se thay 2500+ tin nhan va khong con dau X do.
echo ======================================================
pause