# [V1.0] 비동기 검증 큐 전용 러너
$SSOT_ROOT = "C:\g7core\g7_v1"
try {
    Write-Host ">>> [QUEUE] Starting Async Verification..." -ForegroundColor Cyan
    python "$SSOT_ROOT\tools\verify\verify_worker_async_v1.py"
    Write-Host ">>> [SUCCESS] ALL REPORTS SEALED." -ForegroundColor Green
} catch {
    Write-Host "!!! [FAIL] Verification Error: $_" -ForegroundColor Red
} finally {
    Read-Host "Audit Done. (엔터 시 종료)"
}