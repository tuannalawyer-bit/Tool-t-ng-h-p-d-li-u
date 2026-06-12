$desktop = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::Desktop);
$ws = New-Object -ComObject WScript.Shell;
$s = $ws.CreateShortcut($desktop + '\TripScheduler Pro.lnk');

# PSScriptRoot trả về thư mục chứa file này (thư mục 'app')
# Split-Path -Parent sẽ trả về thư mục gốc của dự án
$rootDir = Split-Path -Parent $PSScriptRoot;

$s.TargetPath = Join-Path $rootDir 'Chay_Phan_Mem.bat';
$s.WorkingDirectory = $rootDir;
$s.Description = 'TripScheduler Pro - Ung dung phan lich cong tac';
$s.IconLocation = 'shell32.dll,223';
$s.Save();
Write-Host "SHORTCUT_CREATED_SUCCESSFULLY";
