
$ErrorActionPreference = "Stop"
$ROOT = "C:\g7core\g7_v1"
Write-Host ">>> [G7X] Blackbox Auto-Export Started..." -ForegroundColor Cyan

# 검증기 호출 (Python 스크립트 실행)
python "$ROOT\tools\post_verify_all_v2.py"

if (Test-Path "$ROOT\runs\REAL\MASTER_FINAL_EXPORT\verify_report.json") {
    Write-Host ">>> [SUCCESS] Master Seal Verified." -ForegroundColor Green
} else {
    Write-Host ">>> [FAIL] Seal Broken." -ForegroundColor Red
    exit 2
}
Read-Host "Press Enter to exit..."
