# G7X REAL30 (3+3)_x5 DAY+NIGHT Night Runner v1
# - DAY: S1~S5 순서 실행 (하나라도 실패 시 중단)
# - NIGHT: S1~S5 순서 실행 (하나라도 실패 시 중단)
# - 각 슬라이스 실행 후 RUN_PATH 출력
# - 오류 감지 시 백오프 딜레이 추가
# - Mode: TEST (슬라이스 파일 사용)

$ErrorActionPreference = "Stop"
$SSOT_ROOT = "C:\g7core\g7_v1"

# Resolve Python path
$venv1 = "$SSOT_ROOT\.venv\Scripts\python.exe"
$venv2 = "$SSOT_ROOT\v1.venv\Scripts\python.exe"

if (Test-Path $venv1) {
    $PY = $venv1
} elseif (Test-Path $venv2) {
    $PY = $venv2
} else {
    Write-Host "[FAIL] Python not found in .venv or v1.venv" -ForegroundColor Red
    Read-Host "Press any key to exit..."
    exit 1
}

Write-Host "[INFO] Using Python: $PY" -ForegroundColor Gray

# 증거팩 수집 변수
$day_runs = @()
$night_runs = @()
$total_exitcode = 0
$slice_delay = 30  # seconds between slices
$error_backoff = 60  # additional delay on error

Write-Host "[REAL30] Starting NIGHT RUNNER (3+3)x5 execution..." -ForegroundColor Cyan
Write-Host ""

# DAY 프로파일: S1~S5 실행
$env:G7_RUN_PROFILE = "DAY"

Write-Host "[REAL30 DAY] Starting DAY profile execution..." -ForegroundColor Yellow
Write-Host ""

for ($i = 1; $i -le 5; $i++) {
    $slice_file = ".\GPTORDER\REAL30_DAY_S$i.txt"

    Write-Host "[DAY S$i] Executing: $slice_file" -ForegroundColor Yellow

    & $PY .\main\manager.py --order_path $slice_file
    $exitcode = $LASTEXITCODE

    Write-Host "[DAY S$i] exitcode=$exitcode" -ForegroundColor $(if ($exitcode -eq 0) { "Green" } else { "Red" })

    if ($exitcode -ne 0) {
        Write-Host "[ERROR] DAY S$i failed. Applying backoff delay: $error_backoff seconds" -ForegroundColor Red
        Start-Sleep -Seconds $error_backoff
        $total_exitcode = 1
        break
    }

    $day_runs += "DAY_S$i"

    if ($i -lt 5) {
        Write-Host "[DELAY] Waiting $slice_delay seconds..." -ForegroundColor Gray
        Start-Sleep -Seconds $slice_delay
    }
    Write-Host ""
}

if ($total_exitcode -eq 0) {
    Write-Host "[DAY] All 5 slices completed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "[DELAY] Profile switch delay: $slice_delay seconds..." -ForegroundColor Gray
    Start-Sleep -Seconds $slice_delay
    Write-Host ""

    # NIGHT 프로파일: S1~S5 실행
    $env:G7_RUN_PROFILE = "NIGHT"

    Write-Host "[REAL30 NIGHT] Starting NIGHT profile execution..." -ForegroundColor Magenta
    Write-Host ""

    for ($i = 1; $i -le 5; $i++) {
        $slice_file = ".\GPTORDER\REAL30_NIGHT_S$i.txt"

        Write-Host "[NIGHT S$i] Executing: $slice_file" -ForegroundColor Magenta

        & $PY .\main\manager.py --order_path $slice_file
        $exitcode = $LASTEXITCODE

        Write-Host "[NIGHT S$i] exitcode=$exitcode" -ForegroundColor $(if ($exitcode -eq 0) { "Green" } else { "Red" })

        if ($exitcode -ne 0) {
            Write-Host "[ERROR] NIGHT S$i failed. Applying backoff delay: $error_backoff seconds" -ForegroundColor Red
            Start-Sleep -Seconds $error_backoff
            $total_exitcode = 1
            break
        }

        $night_runs += "NIGHT_S$i"

        if ($i -lt 5) {
            Write-Host "[DELAY] Waiting $slice_delay seconds..." -ForegroundColor Gray
            Start-Sleep -Seconds $slice_delay
        }
        Write-Host ""
    }

    if ($total_exitcode -eq 0) {
        Write-Host "[NIGHT] All 5 slices completed!" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "REAL30 (3+3)_x5 Execution Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DAY slices completed: $($day_runs.Count)/5" -ForegroundColor Yellow
Write-Host "NIGHT slices completed: $($night_runs.Count)/5" -ForegroundColor Magenta
Write-Host "Total exitcode: $total_exitcode" -ForegroundColor $(if ($total_exitcode -eq 0) { "Green" } else { "Red" })
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# List RUN_PATHs (최근 runs 폴더에서 최신 10개)
if (Test-Path "$SSOT_ROOT\runs") {
    Write-Host "Latest 10 RUN_PATHs:" -ForegroundColor Cyan
    Get-ChildItem "$SSOT_ROOT\runs" -Directory | Sort-Object Name -Descending | Select-Object -First 10 | ForEach-Object {
        Write-Host "  $($_.FullName)" -ForegroundColor Gray
    }
}

Write-Host ""
if ($total_exitcode -eq 0) {
    Write-Host "[SUCCESS] REAL30 (3+3)_x5 completed!" -ForegroundColor Green
} else {
    Write-Host "[FAIL] REAL30 (3+3)_x5 failed. Check logs." -ForegroundColor Red
}

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
Read-Host
exit $total_exitcode
