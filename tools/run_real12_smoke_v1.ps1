# G7X REAL12 Smoke Run v1
# - DAY 1회 + NIGHT 1회
# - 성공 시 RUN_PATH 2개 출력

$ErrorActionPreference = "Stop"
$SSOT_ROOT = "C:\g7core\g7_v1"
$PY = "$SSOT_ROOT\.venv\Scripts\python.exe"

Write-Host "[SMOKE] Starting REAL12 Smoke Test..." -ForegroundColor Cyan
Write-Host ""

# DAY 실행
Write-Host "[DAY] Running REAL12 smoke test..." -ForegroundColor Yellow
$env:G7_RUN_PROFILE = "DAY"
& $PY .\main\manager.py --order_path .\GPTORDER\REAL_WORK_12_001.txt

$day_exitcode = $LASTEXITCODE
Write-Host "[DAY] exitcode=$day_exitcode" -ForegroundColor $(if ($day_exitcode -eq 0) { "Green" } else { "Red" })

if ($day_exitcode -ne 0) {
    Write-Host "[FAIL] DAY smoke test failed. Stopping." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit $day_exitcode
}

Write-Host ""

# NIGHT 실행
Write-Host "[NIGHT] Running REAL12 smoke test..." -ForegroundColor Magenta
$env:G7_RUN_PROFILE = "NIGHT"
& $PY .\main\manager.py --order_path .\GPTORDER\REAL_WORK_12_001.txt

$night_exitcode = $LASTEXITCODE
Write-Host "[NIGHT] exitcode=$night_exitcode" -ForegroundColor $(if ($night_exitcode -eq 0) { "Green" } else { "Red" })

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "REAL12 Smoke Test Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DAY exitcode: $day_exitcode" -ForegroundColor Yellow
Write-Host "NIGHT exitcode: $night_exitcode" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Cyan

if ($day_exitcode -eq 0 -and $night_exitcode -eq 0) {
    Write-Host "[SUCCESS] REAL12 Smoke Test PASSED!" -ForegroundColor Green
    $final_exitcode = 0
} else {
    Write-Host "[FAIL] REAL12 Smoke Test FAILED!" -ForegroundColor Red
    $final_exitcode = 1
}

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
Read-Host
exit $final_exitcode
