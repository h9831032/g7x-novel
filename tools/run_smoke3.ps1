$ErrorActionPreference = "Stop"
$PYTHON = "C:\Users\00\PycharmProjects\PythonProject\.venv\Scripts\python.exe"
$ROOT = "C:\g7core\g7_v1"

Write-Host ">>> SMOKE3 IGNITION <<<" -ForegroundColor Cyan

# 1. 실행
& $PYTHON "$ROOT\main\manager.py" "SMOKE3.txt"

# 2. 증거팩 검수
$latest_run = Get-ChildItem "$ROOT\runs" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
$rp = $latest_run.FullName

Write-Host "`n[CHECKING EVIDENCE PACK: $rp]" -ForegroundColor Yellow
$files = @("api_receipt.jsonl", "blackbox_log.jsonl", "stamp_manifest.json", "verify_report.json", "final_audit.json", "exitcode.txt")
foreach ($f in $files) {
    if (Test-Path "$rp\$f") { 
        $lines = (Get-Content "$rp\$f").Count
        Write-Host " - [OK] $f ($lines lines)" -ForegroundColor Green
    } else {
        Write-Host " - [FAIL] $f MISSING" -ForegroundColor Red
        exit 1
    }
}
$raw_count = (Get-ChildItem "$rp\api_raw_*.json").Count
Write-Host " - [OK] api_raw count: $raw_count" -ForegroundColor Green
Write-Host "`n>>> SMOKE3 MISSION COMPLETE <<<" -ForegroundColor Green