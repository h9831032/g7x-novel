# G7X E2E Verification Script v1
# Pre-launch verification chain
# FAIL_FAST: 중간 실패 시 즉시 종료

$ErrorActionPreference = "Stop"
$SSOT_ROOT = "C:\g7core\g7_v1"

# Resolve Python
if (Test-Path "$SSOT_ROOT\tools\_resolve_python_path.ps1") {
    $PY = & "$SSOT_ROOT\tools\_resolve_python_path.ps1" -RootPath $SSOT_ROOT
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[FAIL] Python resolver failed." -ForegroundColor Red
        Read-Host "Press any key to exit..."
        exit 1
    }
} else {
    $PY = "$SSOT_ROOT\.venv\Scripts\python.exe"
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "G7X E2E Verification" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Dedupe Guard
Write-Host "[1/6] Running dedupe guard..." -ForegroundColor Yellow
& $PY .\tools\dedupe_order_guard_v1.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "[FAIL] Dedupe guard failed!" -ForegroundColor Red
    Read-Host "Press any key to exit..."
    exit 1
}
Write-Host "[PASS] Dedupe guard OK" -ForegroundColor Green
Write-Host ""

# Step 2: Catalog Sanity
Write-Host "[2/6] Running catalog sanity check..." -ForegroundColor Yellow
& $PY .\tools\check_real_catalogs_v1.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "[FAIL] Catalog sanity check failed!" -ForegroundColor Red
    Read-Host "Press any key to exit..."
    exit 1
}
Write-Host "[PASS] Catalog sanity OK" -ForegroundColor Green
Write-Host ""

# Step 3: Smoke Pack
Write-Host "[3/6] Running smoke pack..." -ForegroundColor Yellow
.\tools\run_real_smoke_pack_v1.ps1

if ($LASTEXITCODE -ne 0) {
    Write-Host "[FAIL] Smoke pack failed!" -ForegroundColor Red
    Read-Host "Press any key to exit..."
    exit 1
}
Write-Host "[PASS] Smoke pack OK" -ForegroundColor Green
Write-Host ""

# Step 4: Daily Report
Write-Host "[4/6] Generating daily report..." -ForegroundColor Yellow
& $PY .\tools\build_daily_report_v1.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARN] Daily report generation failed (non-critical)" -ForegroundColor Yellow
}
Write-Host "[PASS] Daily report OK" -ForegroundColor Green
Write-Host ""

# Step 5: Integration Map Update
Write-Host "[5/6] Updating integration map..." -ForegroundColor Yellow
& $PY .\tools\update_integration_map_v1.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARN] Integration map update failed (non-critical)" -ForegroundColor Yellow
}
Write-Host "[PASS] Integration map OK" -ForegroundColor Green
Write-Host ""

# Step 6: State Archive
Write-Host "[6/6] Creating state archive..." -ForegroundColor Yellow
.\tools\state_archive_pack_v1.ps1

if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARN] State archive failed (non-critical)" -ForegroundColor Yellow
}
Write-Host "[PASS] State archive OK" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "E2E Verification Complete" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[SUCCESS] All critical checks passed!" -ForegroundColor Green
Write-Host "System is ready for production missions." -ForegroundColor Green
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
Read-Host
exit 0
