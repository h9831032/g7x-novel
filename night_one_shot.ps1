# G7X Night One Shot (Unattended execution)
param(
  [Parameter(Mandatory=$false)]
  [string]$OrderPath = "REAL_WORK_120_C.txt",
  [Parameter(Mandatory=$false)]
  [int]$Expected = 120,
  [Parameter(Mandatory=$false)]
  [string]$Root = "C:\g7core\g7_v1"
)

$ErrorActionPreference = "Stop"

# CRITICAL: .venv only
$PY = "$Root\.venv\Scripts\python.exe"

Write-Host ""
Write-Host "=== G7X Night One Shot ==="
Write-Host "Order: $OrderPath"
Write-Host "Expected: $Expected"
Write-Host "Root: $Root"
Write-Host ""

# Step 0: Python version check
Write-Host "[0] Python version check..."
if (-not (Test-Path $PY)) {
  Write-Host "[FAIL] .venv not found: $PY"
  exit 1
}

& $PY -V
if ($LASTEXITCODE -ne 0) {
  Write-Host "[FAIL] Python version check failed"
  exit 1
}
Write-Host ""

# Step 1: Manager execution
Write-Host "[1] Running manager..."
$managerPath = Join-Path $Root "main\manager.py"
& $PY $managerPath --order_path $OrderPath --ssot_root $Root
$managerExit = $LASTEXITCODE

Write-Host "    Manager exitcode: $managerExit"
if ($managerExit -ne 0) {
  Write-Host "[FAIL] Manager execution failed"
  exit $managerExit
}
Write-Host ""

# Step 2: Check run pack
Write-Host "[2] Running check_run_pack..."
$checkPath = Join-Path $Root "tools\check_run_pack.py"
& $PY $checkPath --latest --expected $Expected
$checkExit = $LASTEXITCODE

Write-Host "    check_run_pack exitcode: $checkExit"
if ($checkExit -ne 0) {
  Write-Host "[FAIL] check_run_pack failed"
  exit $checkExit
}
Write-Host ""

# Step 3: FINAL_CHECK
Write-Host "[3] Running FINAL_CHECK..."
$finalCheck = Join-Path $Root "FINAL_CHECK.ps1"
if (Test-Path $finalCheck) {
  powershell -ExecutionPolicy Bypass -File $finalCheck
  $fcExit = $LASTEXITCODE
  
  Write-Host "    FINAL_CHECK exitcode: $fcExit"
  if ($fcExit -ne 0) {
    Write-Host "[FAIL] FINAL_CHECK failed"
    exit $fcExit
  }
} else {
  Write-Host "    FINAL_CHECK.ps1 not found -> SKIP"
}
Write-Host ""

Write-Host "=== Night One Shot Complete - ALL PASS ==="
exit 0