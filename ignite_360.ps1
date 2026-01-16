# C:\g7core\g7_v1\ignite_360.ps1
$PythonExe = "C:\Users\00\AppData\Local\Programs\Python\Python310\python.exe"
$Target = "C:\g7core\g7_v1\main\manager.py"
$env:PYTHONPATH = "C:\g7core\g7_v1"

Write-Host "`n[STEP 1] Building 3-Truck Logistics..." -ForegroundColor Cyan
pwsh -File C:\g7core\g7_v1\tools\make_real360.ps1

Write-Host "`n[STEP 2] Launching 360-Unit Full Proof Factory..." -ForegroundColor Yellow
# -u 옵션으로 로그 실시간 강제 출력
& $PythonExe -u $Target --verify_all 2>&1 | Out-String -Stream | ForEach-Object { Write-Host "   G7X_MSG: $_" }

Write-Host "`n[FINISH] Commercial Operation Ended." -ForegroundColor Gray
pause