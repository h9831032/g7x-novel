$ErrorActionPreference = "Stop"
$ROOT = "C:\g7core\g7_v1"
try {
    Write-Host ">>> [G7X] Nightly Factory Run Starting..." -ForegroundColor Cyan
    # 모든 출력을 파일과 화면에 동시 출력
    python "$ROOT\main.py" 2>&1 | Tee-Object -FilePath "$ROOT\runs\REAL\nightly_stdout.log"
    Write-Host ">>> [SUCCESS] Factory Cycle Completed." -ForegroundColor Green
} catch {
    Write-Host "!!! [FAIL] Factory Halted: $($_.Exception.Message)" -ForegroundColor Red
} finally {
    Read-Host "Press Enter to exit (Safe Guard)" # 창 닫힘 방지
}