Write-Host "===================================================================" -ForegroundColor Cyan
Write-Host "            OLLAMA OFFLINE AI - BO TAI DAT SIEU TOC                 " -ForegroundColor Cyan
Write-Host "===================================================================" -ForegroundColor Cyan
Write-Host ""

$targetPath = Join-Path $pwd "OllamaSetup.exe"
$downloadUrl = "https://ollama.com/download/OllamaSetup.exe"

if (Test-Path $targetPath) {
    Write-Host "[+] Tim thay file tai ve co san: $targetPath" -ForegroundColor Green
} else {
    Write-Host "[*] Dang tien hanh tai bo cai dat tu Ollama.com..." -ForegroundColor Yellow
    Write-Host "    URL: $downloadUrl" -ForegroundColor Gray
    try {
        # Use native BITS or WebClient to gracefully handle system proxy
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest -Uri $downloadUrl -OutFile $targetPath -UseBasicParsing
        Write-Host "[+] Tai ve thanh cong! Luu tai: $targetPath" -ForegroundColor Green
    } catch {
        Write-Host "[!] Loi khi tai: $_" -ForegroundColor Red
        Write-Host "[-] Vui long tu tai tai: https://ollama.com/download" -ForegroundColor Yellow
        pause
        exit
    }
}

Write-Host ""
Write-Host "[*] Dang kich hoat trinh cai dat Ollama len man hinh cua ban..." -ForegroundColor Yellow
Write-Host "    Vui long an nut 'Install' tren hop thoai vua xuat hien." -ForegroundColor Gray
Write-Host ""

# Launch the installer visibly
Start-Process -FilePath $targetPath -Wait

Write-Host "===================================================================" -ForegroundColor Cyan
Write-Host "[+] KICH HOAT THANH CONG! OLLAMA DA DUOC CAI DAT." -ForegroundColor Green
Write-Host "===================================================================" -ForegroundColor Cyan
pause
