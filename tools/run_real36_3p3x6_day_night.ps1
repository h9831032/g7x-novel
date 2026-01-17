# G7X REAL36 (3+3)_x6 DAY+NIGHT 실행 스크립트 v1
# - DAY: S1~S6 순서 실행 (하나라도 실패 시 중단)
# - NIGHT: S1~S6 순서 실행 (하나라도 실패 시 중단)
# - 각 슬라이스 실행 후 RUN_PATH 출력
# - Mode: TEST | REAL (카탈로그 선택)

param(
    [ValidateSet("TEST", "REAL")]
    [string]$Mode = "TEST"
)

$ErrorActionPreference = "Stop"
$SSOT_ROOT = "C:\g7core\g7_v1"

# Resolve Python path using resolver
$PY = & "$SSOT_ROOT\tools\_resolve_python_path.ps1" -RootPath $SSOT_ROOT
if ($LASTEXITCODE -ne 0) {
    Write-Host "[FAIL] Python resolver failed. Exiting." -ForegroundColor Red
    Read-Host "Press any key to exit..."
    exit 1
}

# 증거팩 수집 변수
$day_runs = @()
$night_runs = @()
$total_exitcode = 0

Write-Host "[MODE] Running with Mode=$Mode" -ForegroundColor Cyan

Write-Host "[REAL36_3P3X6] Starting DAY profile execution..." -ForegroundColor Cyan
Write-Host ""

# DAY 프로파일: S1~S6 실행
$env:G7_RUN_PROFILE = "DAY"

for ($i = 1; $i -le 6; $i++) {
    if ($Mode -eq "REAL") {
        # REAL 모드: REAL36_REAL_A.txt 사용 (36개 미션을 6개씩)
        $order_file = ".\GPTORDER\REAL36_REAL_A.txt"
        $start_line = (($i - 1) * 6) + 1
        $end_line = $i * 6

        # 임시 슬라이스 생성
        $temp_slice = ".\GPTORDER\TEMP_REAL36_DAY_S$i.txt"
        Get-Content $order_file | Select-Object -Skip ($start_line - 1) -First 6 | Set-Content $temp_slice
        $slice_file = $temp_slice
    } else {
        # TEST 모드: 기존 슬라이스 파일 사용
        $slice_file = ".\GPTORDER\REAL36_DAY_S$i.txt"
    }

    Write-Host "[DAY S$i] Executing: $slice_file" -ForegroundColor Yellow

    & $PY .\main\manager.py --order_path $slice_file
    $exitcode = $LASTEXITCODE

    # RUN_PATH 추출 (stdout에서 TARGET_RUN_PATH: 라인 찾기)
    # Note: 실제로는 $stdout을 캡처해야 하지만, manager.py가 이미 출력함
    Write-Host "[DAY S$i] exitcode=$exitcode" -ForegroundColor $(if ($exitcode -eq 0) { "Green" } else { "Red" })

    if ($exitcode -ne 0) {
        Write-Host "[FAIL] DAY S$i failed with exitcode=$exitcode. Stopping DAY execution." -ForegroundColor Red
        $total_exitcode = 1
        break
    }

    $day_runs += "DAY_S$i"
    Write-Host ""
}

if ($total_exitcode -eq 0) {
    Write-Host "[DAY] All 6 slices completed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "[REAL36_3P3X6] Starting NIGHT profile execution..." -ForegroundColor Cyan
    Write-Host ""

    # NIGHT 프로파일: S1~S6 실행
    $env:G7_RUN_PROFILE = "NIGHT"

    for ($i = 1; $i -le 6; $i++) {
        if ($Mode -eq "REAL") {
            # REAL 모드: REAL36_REAL_A.txt 사용
            $order_file = ".\GPTORDER\REAL36_REAL_A.txt"
            $start_line = (($i - 1) * 6) + 1

            # 임시 슬라이스 생성
            $temp_slice = ".\GPTORDER\TEMP_REAL36_NIGHT_S$i.txt"
            Get-Content $order_file | Select-Object -Skip ($start_line - 1) -First 6 | Set-Content $temp_slice
            $slice_file = $temp_slice
        } else {
            # TEST 모드: 기존 슬라이스 파일 사용
            $slice_file = ".\GPTORDER\REAL36_NIGHT_S$i.txt"
        }

        Write-Host "[NIGHT S$i] Executing: $slice_file" -ForegroundColor Magenta

        & $PY .\main\manager.py --order_path $slice_file
        $exitcode = $LASTEXITCODE

        Write-Host "[NIGHT S$i] exitcode=$exitcode" -ForegroundColor $(if ($exitcode -eq 0) { "Green" } else { "Red" })

        if ($exitcode -ne 0) {
            Write-Host "[FAIL] NIGHT S$i failed with exitcode=$exitcode. Stopping NIGHT execution." -ForegroundColor Red
            $total_exitcode = 1
            break
        }

        $night_runs += "NIGHT_S$i"
        Write-Host ""
    }

    if ($total_exitcode -eq 0) {
        Write-Host "[NIGHT] All 6 slices completed successfully!" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "REAL36 (3+3)_x6 Execution Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DAY slices completed: $($day_runs.Count)/6" -ForegroundColor Yellow
Write-Host "NIGHT slices completed: $($night_runs.Count)/6" -ForegroundColor Magenta
Write-Host "Total exitcode: $total_exitcode" -ForegroundColor $(if ($total_exitcode -eq 0) { "Green" } else { "Red" })
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($total_exitcode -eq 0) {
    Write-Host "[SUCCESS] REAL36 (3+3)_x6 completed!" -ForegroundColor Green
} else {
    Write-Host "[FAIL] REAL36 (3+3)_x6 failed. Check logs above." -ForegroundColor Red
}

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
Read-Host
exit $total_exitcode
