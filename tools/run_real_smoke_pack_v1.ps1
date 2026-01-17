# G7X REAL Smoke Pack v1
# '실전 최소 확인' 팩
# - REAL12 TEST 1회
# - REAL24 DAY S1 1회
# - REAL36 DAY S1 1회
# - 각 실행 후 artifacts 자동 검사

$ErrorActionPreference = "Stop"
$SSOT_ROOT = "C:\g7core\g7_v1"

# Resolve Python path
if (Test-Path "$SSOT_ROOT\tools\_resolve_python_path.ps1") {
    $PY = & "$SSOT_ROOT\tools\_resolve_python_path.ps1" -RootPath $SSOT_ROOT
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[FAIL] Python resolver failed." -ForegroundColor Red
        Read-Host "Press any key to exit..."
        exit 1
    }
} else {
    $venv1 = "$SSOT_ROOT\.venv\Scripts\python.exe"
    if (Test-Path $venv1) {
        $PY = $venv1
    } else {
        Write-Host "[FAIL] Python not found" -ForegroundColor Red
        Read-Host "Press any key to exit..."
        exit 1
    }
}

$artifact_checker = "$SSOT_ROOT\tools\check_run_artifacts_v1.py"
$total_exitcode = 0
$runs_completed = 0

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "G7X REAL Smoke Pack v1" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: REAL12
Write-Host "[TEST 1/3] Running REAL12..." -ForegroundColor Yellow
& $PY .\main\manager.py --order_path .\GPTORDER\TEST_REAL12_VERIFY.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "[TEST 1/3] REAL12 PASS" -ForegroundColor Green
    $runs_completed++

    # Check artifacts
    if (Test-Path $artifact_checker) {
        Write-Host "[ARTIFACTS] Checking REAL12 artifacts..." -ForegroundColor Gray
        & $PY $artifact_checker
    }
} else {
    Write-Host "[TEST 1/3] REAL12 FAIL (exitcode=$LASTEXITCODE)" -ForegroundColor Red
    $total_exitcode = 1
}

Write-Host ""
Start-Sleep -Seconds 15

# Test 2: REAL24 DAY S1
Write-Host "[TEST 2/3] Running REAL24 DAY S1..." -ForegroundColor Yellow
& $PY .\main\manager.py --order_path .\GPTORDER\REAL24_DAY_S1.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "[TEST 2/3] REAL24 DAY S1 PASS" -ForegroundColor Green
    $runs_completed++

    # Check artifacts
    if (Test-Path $artifact_checker) {
        Write-Host "[ARTIFACTS] Checking REAL24 artifacts..." -ForegroundColor Gray
        & $PY $artifact_checker
    }
} else {
    Write-Host "[TEST 2/3] REAL24 DAY S1 FAIL (exitcode=$LASTEXITCODE)" -ForegroundColor Red
    $total_exitcode = 1
}

Write-Host ""
Start-Sleep -Seconds 15

# Test 3: REAL36 DAY S1
Write-Host "[TEST 3/3] Running REAL36 DAY S1..." -ForegroundColor Yellow
& $PY .\main\manager.py --order_path .\GPTORDER\REAL36_DAY_S1.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "[TEST 3/3] REAL36 DAY S1 PASS" -ForegroundColor Green
    $runs_completed++

    # Check artifacts
    if (Test-Path $artifact_checker) {
        Write-Host "[ARTIFACTS] Checking REAL36 artifacts..." -ForegroundColor Gray
        & $PY $artifact_checker
    }
} else {
    Write-Host "[TEST 3/3] REAL36 DAY S1 FAIL (exitcode=$LASTEXITCODE)" -ForegroundColor Red
    $total_exitcode = 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "REAL Smoke Pack Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Tests completed: $runs_completed/3" -ForegroundColor $(if ($runs_completed -eq 3) { "Green" } else { "Red" })
Write-Host "Overall exitcode: $total_exitcode" -ForegroundColor $(if ($total_exitcode -eq 0) { "Green" } else { "Red" })
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($total_exitcode -eq 0) {
    Write-Host "[SUCCESS] All smoke tests passed!" -ForegroundColor Green
} else {
    Write-Host "[FAIL] Some smoke tests failed." -ForegroundColor Red
}

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
Read-Host
exit $total_exitcode
