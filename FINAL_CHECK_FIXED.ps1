# G7X Final Check Script (ASCII Only, Encoding Fixed)
# UTF-8 with BOM to prevent encoding issues

$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host ""
Write-Host "=== G7X Final Seal Verification ===" -ForegroundColor Cyan
Write-Host ""

$allPass = $true

# Check 1 - devlog.jsonl file exists
Write-Host "[Check 1] devlog.jsonl file existence" -ForegroundColor Yellow
$devlogJsonl = "C:\g7core\g7_v1\devlog\devlog.jsonl"
if (Test-Path $devlogJsonl) {
    $lines = (Get-Content $devlogJsonl).Count
    Write-Host "  [PASS] devlog.jsonl exists ($lines lines)" -ForegroundColor Green
} else {
    Write-Host "  [FAIL] devlog.jsonl missing" -ForegroundColor Red
    $allPass = $false
}

# Check 2 - append_devlog welded in manager.py
Write-Host ""
Write-Host "[Check 2] append_devlog welded in manager.py" -ForegroundColor Yellow
$managerPath = "C:\g7core\g7_v1\main\manager.py"
$hasAppendDevlog = Select-String -Path $managerPath -Pattern "append_devlog" -Quiet
if ($hasAppendDevlog) {
    Write-Host "  [PASS] append_devlog found in manager.py" -ForegroundColor Green
    Select-String -Path $managerPath -Pattern "append_devlog" -Context 1, 0 | Select-Object -First 2
} else {
    Write-Host "  [FAIL] append_devlog not found in manager.py" -ForegroundColor Red
    $allPass = $false
}

# Check 3 - ANCHOR_RUN.txt file
Write-Host ""
Write-Host "[Check 3] ANCHOR_RUN.txt file check" -ForegroundColor Yellow
$anchorPath = "C:\g7core\g7_v1\ANCHOR_RUN.txt"
if (Test-Path $anchorPath) {
    Write-Host "  [PASS] ANCHOR_RUN.txt exists" -ForegroundColor Green
    Get-Content $anchorPath | ForEach-Object { Write-Host "    $_" -ForegroundColor Gray }
} else {
    Write-Host "  [FAIL] ANCHOR_RUN.txt missing" -ForegroundColor Red
    $allPass = $false
}

# Check 4 - generate_devlog.py exists
Write-Host ""
Write-Host "[Check 4] generate_devlog.py file check" -ForegroundColor Yellow
$devlogPyPath = "C:\g7core\g7_v1\tools\generate_devlog.py"
if (Test-Path $devlogPyPath) {
    Write-Host "  [PASS] generate_devlog.py exists" -ForegroundColor Green
} else {
    Write-Host "  [FAIL] generate_devlog.py missing" -ForegroundColor Red
    $allPass = $false
}

# Check 5 - Today's devlog txt file
Write-Host ""
Write-Host "[Check 5] Today's devlog txt file check" -ForegroundColor Yellow
$today = Get-Date -Format "yyyyMMdd"
$devlogTxtPath = "C:\g7core\g7_v1\devlog\devlog_$today.txt"
if (Test-Path $devlogTxtPath) {
    $size = (Get-Item $devlogTxtPath).Length
    Write-Host "  [PASS] devlog_$today.txt exists ($size bytes)" -ForegroundColor Green
} else {
    Write-Host "  [WARN] devlog_$today.txt not found (may not have run today)" -ForegroundColor Yellow
}

# Final verdict
Write-Host ""
Write-Host "=== Final Verdict ===" -ForegroundColor Cyan
if ($allPass) {
    Write-Host "[PASS] Complete seal - Main auto integration complete" -ForegroundColor Green
    exit 0
} else {
    Write-Host "[FAIL] Incomplete - Some items missing" -ForegroundColor Red
    exit 1
}
