# DEVLOG Auto-generation Deployment and Test v2

param(
  [Parameter(Mandatory=$false)]
  [string]$Root = "C:\g7core\g7_v1"
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host ""
Write-Host "=== DEVLOG Auto-generation Deploy and Test v2 ===" -ForegroundColor Cyan
Write-Host "Root: $Root"
Write-Host "Script Dir: $ScriptDir"
Write-Host ""

$PY = "$Root\.venv\Scripts\python.exe"

if (-not (Test-Path $PY)) {
  Write-Host "[FAIL] .venv not found: $PY" -ForegroundColor Red
  exit 1
}

Write-Host "[Step 1] Deploy devlog_writer.py" -ForegroundColor Yellow
$devlogWriter = Join-Path $Root "tools\devlog_writer.py"
$sourceDevlog = Join-Path $ScriptDir "devlog_writer.py"

if (Test-Path $sourceDevlog) {
  Copy-Item $sourceDevlog $devlogWriter -Force
  if (Test-Path $devlogWriter) {
    Write-Host "  [OK] Deployed: $devlogWriter" -ForegroundColor Green
  } else {
    Write-Host "  [FAIL] Deploy failed: $devlogWriter" -ForegroundColor Red
    exit 1
  }
} else {
  Write-Host "  [FAIL] Source not found: $sourceDevlog" -ForegroundColor Red
  exit 1
}

Write-Host ""
Write-Host "[Step 2] Patch manager.py" -ForegroundColor Yellow
$managerPath = Join-Path $Root "main\manager.py"
$sourcePatch = Join-Path $ScriptDir "patch_manager_devlog.py"

if (Test-Path $sourcePatch) {
  & $PY $sourcePatch $managerPath
  if ($LASTEXITCODE -ne 0) {
    Write-Host "  [FAIL] Patch failed" -ForegroundColor Red
    exit 1
  }
  Write-Host "  [OK] Patched: $managerPath" -ForegroundColor Green
} else {
  Write-Host "  [FAIL] Source not found: $sourcePatch" -ForegroundColor Red
  exit 1
}

Write-Host ""
Write-Host "[Step 3] Deploy test orders" -ForegroundColor Yellow
$gptorderDir = Join-Path $Root "GPTORDER"

$sourceTest5 = Join-Path $ScriptDir "TEST_DEVLOG_5.txt"
if (Test-Path $sourceTest5) {
  $destTest5 = Join-Path $gptorderDir "TEST_DEVLOG_5.txt"
  Copy-Item $sourceTest5 $destTest5 -Force
  if (Test-Path $destTest5) {
    Write-Host "  [OK] Deployed: TEST_DEVLOG_5.txt" -ForegroundColor Green
  } else {
    Write-Host "  [FAIL] Deploy failed: TEST_DEVLOG_5.txt" -ForegroundColor Red
    exit 1
  }
}

$sourceTestFail = Join-Path $ScriptDir "TEST_DEVLOG_FAIL.txt"
if (Test-Path $sourceTestFail) {
  $destTestFail = Join-Path $gptorderDir "TEST_DEVLOG_FAIL.txt"
  Copy-Item $sourceTestFail $destTestFail -Force
  if (Test-Path $destTestFail) {
    Write-Host "  [OK] Deployed: TEST_DEVLOG_FAIL.txt" -ForegroundColor Green
  } else {
    Write-Host "  [FAIL] Deploy failed: TEST_DEVLOG_FAIL.txt" -ForegroundColor Red
    exit 1
  }
}

Write-Host ""
Write-Host "[Step 4] Test 1 - Normal Execution" -ForegroundColor Yellow
& $PY (Join-Path $Root "main\manager.py") --order_path "TEST_DEVLOG_5.txt" --ssot_root $Root
$exit1 = $LASTEXITCODE
Write-Host "  Exitcode: $exit1" -ForegroundColor $(if ($exit1 -eq 0) { "Green" } else { "Yellow" })

Write-Host ""
Write-Host "[Step 5] Verify DEVLOG files (Test 1)" -ForegroundColor Yellow
$devlogDir = Join-Path $Root "DEVLOG"
$today = Get-Date -Format "yyyy-MM-dd"
$dailyReport = Join-Path $devlogDir "$today\DAILY_REPORT_$today.txt"

$files = @(
  (Join-Path $devlogDir "EVIDENCE_LATEST.json"),
  (Join-Path $devlogDir "DELTA_TODAY.json"),
  (Join-Path $devlogDir "NEXT_TOMORROW.json"),
  (Join-Path $devlogDir "INTEGRATION_MAP.json"),
  $dailyReport
)

$allExist = $true
foreach ($file in $files) {
  if (Test-Path $file) {
    Write-Host "  [OK] $file" -ForegroundColor Green
  } else {
    Write-Host "  [MISSING] $file" -ForegroundColor Red
    $allExist = $false
  }
}

Write-Host ""
if ($allExist) {
  Write-Host "[PASS] All 5 DEVLOG files generated" -ForegroundColor Green
} else {
  Write-Host "[FAIL] Some DEVLOG files missing" -ForegroundColor Red
  exit 1
}

Write-Host ""
Write-Host "[Step 6] Display DAILY_REPORT sample" -ForegroundColor Yellow
if (Test-Path $dailyReport) {
  Get-Content $dailyReport | Select-Object -First 20
} else {
  Write-Host "  [WARN] DAILY_REPORT not found" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Deployment and Test Complete ===" -ForegroundColor Cyan
exit 0
