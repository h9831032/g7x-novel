# G7X FINAL_CHECK (venv strict mode)

$Root = "C:\g7core\g7_v1"
$PY = "$Root\.venv\Scripts\python.exe"

$pass1 = $false
$pass2 = $false
$pass3 = $false
$pass4 = $false

Write-Host ""
Write-Host "=== G7X Final Check ===" -ForegroundColor Cyan
Write-Host ""

# Check 0: manager path
Write-Host "[Check 0] manager.py path" -ForegroundColor Yellow
$mgr1 = "$Root\manager.py"
$mgr2 = "$Root\main\manager.py"
if ((Test-Path $mgr1) -or (Test-Path $mgr2)) {
  Write-Host "  PASS - manager exists" -ForegroundColor Green
  $pass1 = $true
} else {
  Write-Host "  FAIL - manager missing" -ForegroundColor Red
}

# Check 1: devlog.jsonl
Write-Host ""
Write-Host "[Check 1] devlog.jsonl file" -ForegroundColor Yellow
$devlogPath = "$Root\devlog\devlog.jsonl"
if (Test-Path $devlogPath) {
  $lines = (Get-Content $devlogPath).Count
  Write-Host "  PASS - File exists with $lines lines" -ForegroundColor Green
  $pass2 = $true
} else {
  Write-Host "  FAIL - File not found" -ForegroundColor Red
}

# Check 2: append_devlog in manager.py
Write-Host ""
Write-Host "[Check 2] append_devlog in manager.py" -ForegroundColor Yellow
$managerPath = if (Test-Path $mgr2) { $mgr2 } else { $mgr1 }
if (Test-Path $managerPath) {
  $found = Select-String -Path $managerPath -Pattern "append_devlog|call_devlog_generator" -Quiet
  if ($found) {
    Write-Host "  PASS - devlog call found" -ForegroundColor Green
    $pass3 = $true
  } else {
    Write-Host "  FAIL - devlog call not found" -ForegroundColor Red
  }
} else {
  Write-Host "  FAIL - manager.py not accessible" -ForegroundColor Red
}

# Check 3: ANCHOR_RUN.txt
Write-Host ""
Write-Host "[Check 3] ANCHOR_RUN.txt file" -ForegroundColor Yellow
$anchorPath = "$Root\ANCHOR_RUN.txt"
if (Test-Path $anchorPath) {
  Write-Host "  PASS - File exists" -ForegroundColor Green
  $pass4 = $true
  Get-Content $anchorPath | ForEach-Object { Write-Host "    $_" -ForegroundColor Gray }
} else {
  Write-Host "  FAIL - File not found" -ForegroundColor Red
}

# Final verdict
Write-Host ""
Write-Host "=== Final Verdict ===" -ForegroundColor Cyan
if ($pass1 -and $pass2 -and $pass3 -and $pass4) {
  Write-Host "PASS - All checks complete" -ForegroundColor Green
  exit 0
} else {
  Write-Host "FAIL - Some checks failed" -ForegroundColor Red
  exit 1
}