$ErrorActionPreference = "Stop"
try {
    Write-Host ">>> [G7X] Executing Real Factory Weld..." -ForegroundColor Cyan
    python "C:\g7core\g7_v1\main.py"
    python "C:\g7core\g7_v1\tools\report_export.py"
    Write-Host ">>> [SUCCESS] All Proofs Saved." -ForegroundColor Green
} catch {
    Write-Host "!!! [FAIL] Factory Stopped: $($_.Exception.Message)" -ForegroundColor Red
} finally {
    Read-Host "Press Enter to exit"
}