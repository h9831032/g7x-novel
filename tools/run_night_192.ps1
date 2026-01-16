$ErrorActionPreference = "Stop"
$ROOT = "C:\g7core\g7_v1"
try {
    Write-Host ">>> [G7X] Initializing Night Run (192 Tasks / 80% Load)..." -ForegroundColor Cyan
    
    # 1. 600개 백로그 씨앗 뿌리기 (없으면 생성)
    if ((Get-ChildItem "$ROOT\backlog\cards\*.json").Count -lt 600) {
        Write-Host "   [INIT] Seeding 600 Backlog Cards..." -ForegroundColor Yellow
        python "$ROOT\tools\backlog_seed_600.py"
    }

    # 2. 메인 엔진 가동 (192개 처리)
    python "$ROOT\main.py"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ">>> [SUCCESS] Night Run Completed & Verified." -ForegroundColor Green
    } else {
        throw "Main Engine ExitCode: $LASTEXITCODE"
    }

    # 3. DevLog 요약 갱신
    powershell -File "$ROOT\tools\devlog_scheduler.ps1"

} catch {
    Write-Host "!!! [FAIL] CRITICAL ERROR: $($_.Exception.Message)" -ForegroundColor Red
} finally {
    Write-Host "`n===================================================="
    Read-Host "Press Enter to close window (Mandatory Check)"
}
