# C:\g7core\g7_v1\ignite_v29_FINAL.ps1
$TargetFile = "C:\g7core\g7_v1\engine\basic_engine_v29.py"
Write-Host "`n[DIAGNOSIS] Starting Forced Discovery..." -ForegroundColor Cyan

# 1. 파이썬 실행 파일 찾기
$PythonExe = (Get-Command python.exe -ErrorAction SilentlyContinue).Source
if (-not $PythonExe) { $PythonExe = (Get-Command py.exe -ErrorAction SilentlyContinue).Source }

if ($PythonExe) {
    Write-Host ">>> Found Python at: $PythonExe" -ForegroundColor Green
} else {
    Write-Host "!!! CRITICAL: Python NOT FOUND in System PATH." -ForegroundColor Red
    Write-Host "Please type 'where python' in your terminal and tell me the result." -ForegroundColor Yellow
    exit
}

# 2. 엔진 시동
Write-Host "`n[IGNITION] Launching G7X Engine v29.0..." -ForegroundColor Yellow
try {
    & $PythonExe -u $TargetFile 2>&1 | Out-String -Stream | ForEach-Object { Write-Host "   PYTHON: $_" }
} catch {
    Write-Host "!!! EXECUTION ERROR: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n[FINISH] Process Ended." -ForegroundColor Gray