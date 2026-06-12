# build_setup.ps1
# Script tu dong hoa viec xay dung file TripSchedulerPro_Setup.exe
# Phien ban 100% ASCII Safe - Mien nhiem loi font chu he thong

$ErrorActionPreference = "Stop"

# 1. Xac dinh thu muc lam viec goc
$scriptDir = $PSScriptRoot
$rootDir = Split-Path -Parent $scriptDir

Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "=== BAT DAU QUY TRINH DUC BO CAI DAT 1-CLICK ===" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan

# CHIEN LUOC CHONG LOI UNICODE:
# Dung toan bo khong gian build tai thu muc TEMP he thong (ASCII 100%)
$buildTemp = Join-Path $env:TEMP "TripSchedulerPro_BuildWorkspace"
if (Test-Path $buildTemp) { Remove-Item $buildTemp -Recurse -Force }
New-Item -ItemType Directory -Path $buildTemp | Out-Null

# 2. Nen toan bo ma nguon sach cua du an (Loai tru venv va file rac)
Write-Host "[1/4] Dang quet va nen cau truc thu muc du an vao file ZIP..." -ForegroundColor Yellow
$zipPath = Join-Path $buildTemp "Phan_Lich_Source.zip"

# Tao danh sach loai tru thong minh
$filesToZip = Get-ChildItem -Path $rootDir -Recurse | Where-Object {
    $_.FullName -notmatch "venv" -and
    $_.FullName -notmatch "build_temp" -and
    $_.FullName -notmatch "\.git" -and
    $_.FullName -notmatch "__pycache__" -and
    $_.FullName -notmatch "wheels" -and
    $_.FullName -notmatch "Backup_TripScheduler" -and
    $_.FullName -notmatch "\.zip$" -and
    $_.FullName -notmatch "TripSchedulerPro_Setup.exe"
}

# Zip thu cong
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip = [System.IO.Compression.ZipFile]::Open($zipPath, "Create")
try {
    foreach ($f in $filesToZip) {
        if (-not $_.PSIsContainer) {
            if ($f.Attributes -match "Directory") { continue }
            $relPath = $f.FullName.Substring($rootDir.Length + 1)
            [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip, $f.FullName, $relPath) | Out-Null
        }
    }
}
finally {
    $zip.Dispose()
}
Write-Host "[+] Da sinh tep ZIP sach tai thu muc he thong." -ForegroundColor Green

# 3. Tao file moi khoi chay Bootstrap.bat
Write-Host "[2/4] Dang tao tep dieu phoi Bootstrap.bat..." -ForegroundColor Yellow
$bootstrapPath = Join-Path $buildTemp "Bootstrap.bat"
$bootstrapContent = @"
@echo off
echo ===========================================================
echo  DANG GIAI NEN BO CAI DAT TRIPSCHEDULER PRO...
echo ===========================================================
echo [*] Vui long cho doi giay lat...
set "TARGET_DIR=%APPDATA%\TripSchedulerPro"
if not exist "%TARGET_DIR%" mkdir "%TARGET_DIR%"
:: Dung PowerShell de giai nen bao toan 100% cac thu muc con
powershell -Command "Expand-Archive -Path 'Phan_Lich_Source.zip' -DestinationPath '%TARGET_DIR%' -Force"
cd /d "%TARGET_DIR%"
:: Bat trinh cai dat tu dong venv va shortcut
start "" "Khoi_Tao_Va_Chay.bat"
"@
[System.IO.File]::WriteAllLines($bootstrapPath, $bootstrapContent)

# 4. Tao file chi thi cau hinh SED cho Microsoft IExpress Compiler
Write-Host "[3/4] Dang thiet lap ban do chi thi SED (Microsoft Standard)..." -ForegroundColor Yellow
$sedPath = Join-Path $buildTemp "iexpress.sed"
# Dich den tam thoi trong thu muc Temp de IExpress khong gap loi unicode
$tempExe = Join-Path $buildTemp "TripSchedulerPro_Setup.exe"
$finalExe = Join-Path $rootDir "TripSchedulerPro_Setup.exe"

# Cu phap SED Microsoft quy chuan tuyet doi
$sedContent = @"
[Version]
Class=IEXPRESS
SEDVersion=3
[Options]
PackagePurpose=InstallApp
ShowInstallProgramWindow=0
HideExtractAnimation=0
UseLongFileName=1
InsideCompressed=0
CAB_FixedSize=0
CAB_ResvCodeSigning=0
RebootMode=N
InstallPrompt=%InstallPrompt%
DisplayLicense=%DisplayLicense%
FinishMessage=%FinishMessage%
TargetName=%TargetName%
FriendlyName=%FriendlyName%
AppLaunched=%AppLaunched%
PostInstallCmd=%PostInstallCmd%
SourceFiles=SourceFiles
[Strings]
InstallPrompt=
DisplayLicense=
FinishMessage=
TargetName=$tempExe
FriendlyName=TripScheduler Pro Setup
AppLaunched=cmd.exe /c Bootstrap.bat
PostInstallCmd=<None>
FILE0="Phan_Lich_Source.zip"
FILE1="Bootstrap.bat"
[SourceFiles]
SourceFiles0=$buildTemp\
[SourceFiles0]
%FILE0%=
%FILE1%=
"@

# Ghi de o bang ma mac dinh ANSI cua he thong de IExpress de dang doc hieu
[System.IO.File]::WriteAllText($sedPath, $sedContent, [System.Text.Encoding]::Default)

# 5. Trieu goi IExpress.exe dong goi
Write-Host "[4/4] Dang thuc thi trinh bien dich Microsoft IExpress Compiler..." -ForegroundColor Yellow
$iexpress = Join-Path $env:windir "System32\iexpress.exe"

# KET PHAT SANG KIEN: Chuyen thuc thu ve Temp de trinh IExpress legacy khong bi loi tham so duong dan tuyet doi
$originalDir = Get-Location
Set-Location $buildTemp

# Khoi chay IExpress (/N: Build) bang duong dan tuong doi
$process = Start-Process -FilePath $iexpress -ArgumentList "/N", "/Q", "iexpress.sed" -PassThru -Wait
Start-Sleep -Seconds 3 # Cho he dieu hanh dong handle tep tin

# Quay tro lai thu muc goc
Set-Location $originalDir

# 6. Kiem chung va Di chuyen tep ve thu muc Du an dich
if (Test-Path $tempExe) {
    if (Test-Path $finalExe) { Remove-Item $finalExe -Force }
    Move-Item -Path $tempExe -Destination $finalExe -Force
    
    Write-Host "====================================================" -ForegroundColor Green
    Write-Host "SUCCESSFULLY GENERATED SINGLE INSTALLER SETUP!" -ForegroundColor Green
    Write-Host "Location: $finalExe" -ForegroundColor Green
    Write-Host "====================================================" -ForegroundColor Green
} else {
    Write-Host "ERROR: IExpress refused to compile. Check temporary files." -ForegroundColor Red
}

# Don dep vung nho tam he thong
if (Test-Path $buildTemp) { Remove-Item $buildTemp -Recurse -Force }
