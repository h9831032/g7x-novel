
$ErrorActionPreference = "Stop"
$ROOT = "C:\g7core\g7_v1"
$DEVLOG_DIR = "$ROOT\runs\REAL\DEVLOG"
$SUMMARY_FILE = "$DEVLOG_DIR\summary_latest.txt"

Write-Host ">>> [DEVLOG] Auto-Generating Summary..." -ForegroundColor Cyan

# 최근 로그 읽어서 요약 (가라 아님, 실제 파일 읽기)
$LogFile = "$DEVLOG_DIR\devlog.jsonl"
if (Test-Path $LogFile) {
    $Lines = Get-Content $LogFile
    $Count = $Lines.Count
    $LastLine = $Lines | Select-Object -Last 1
    
    $Summary = @"
--- DEVLOG SUMMARY ---
TIMESTAMP: $(Get-Date)
TOTAL_LOGS: $Count
LAST_ENTRY: $LastLine
STATUS: ACTIVE
NEXT_ACTION: REFILL_BACKLOG
"@
    $Summary | Out-File -FilePath $SUMMARY_FILE -Encoding utf8
    Write-Host ">>> [SUCCESS] Summary Updated at $SUMMARY_FILE" -ForegroundColor Green
} else {
    Write-Host "!!! [FAIL] No devlog found." -ForegroundColor Red
}
