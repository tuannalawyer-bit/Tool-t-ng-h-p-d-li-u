@echo off
title THIET LAP BAN DAU CHO OPENCLAW
echo ==============================================================
echo       KHOI CHAY TRINH CAU HINH BAN DAU CHO OPENCLAW AGENT
echo ==============================================================
echo.
echo [+] Dang chuan bi chay thu thuat onboarding...
echo [!] Huong dan: Trinh duyet hoac cua so lenh se hoi ban cac thong tin:
echo     1. Lua chon Model Provider (Gemini, Ollama, OpenAI...)
echo     2. Nhap API Key cua ban.
echo     3. Cai dat nen tang chay ngam (Daemon).
echo.
echo --------------------------------------------------------------
openclaw onboard --install-daemon
echo --------------------------------------------------------------
echo.
echo [+] Da hoan tat thiet lap onboarding!
echo [*] Ban co the dong cua so nay va su dung file 'MO_GIAO_DIEN_DASHBOARD_OPENCLAW.bat'.
echo.
pause
