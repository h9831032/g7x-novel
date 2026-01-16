# C:\g7core\g7_v1\ignite_manager.ps1
$PythonExe = "C:\Users\00\AppData\Local\Programs\Python\Python310\python.exe"
$Target = "C:\g7core\g7_v1\main\manager.py"

Write-Host "`n[IGNITION] Starting Integrated G7X Manager..." -ForegroundColor Yellow
if (Test-Path $Target) {
    # -u 옵션으로 파이썬 로그가 죽지 않고 실시간으로 나오게 합니다.
    & $PythonExe -u $Target 2>&1 | Out-String -Stream | ForEach-Object { Write-Host "   G7X_MSG: $_" }
} else {
    Write-Host "!!! [FATAL] Manager.py not found at $Target" -ForegroundColor Red
}

Write-Host "`n[FINISH] Process Ended. Check run folders." -ForegroundColor Gray
pause
