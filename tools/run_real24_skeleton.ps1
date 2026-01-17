# G7X REAL24 Runner Skeleton v1
# Executes a REAL24 order file with full evidence validation

param(
    [Parameter(Mandatory=$false)]
    [string]$OrderFile = "",

    [Parameter(Mandatory=$false)]
    [ValidateSet("DAY", "NIGHT")]
    [string]$Profile = "DAY"
)

$ErrorActionPreference = "Stop"
$SSOT_ROOT = "C:\g7core\g7_v1"
$PYTHON = "$SSOT_ROOT\.venv\Scripts\python.exe"

# Validation
if (-not (Test-Path $PYTHON)) {
    Write-Host "[FAIL] Python not found: $PYTHON" -ForegroundColor Red
    exit 1
}

if (-not $OrderFile) {
    Write-Host "[FAIL] OrderFile parameter required" -ForegroundColor Red
    Write-Host "Usage: run_real24_skeleton.ps1 -OrderFile GPTORDER/REAL24.txt [-Profile DAY|NIGHT]" -ForegroundColor Yellow
    exit 1
}

$OrderPath = Join-Path $SSOT_ROOT $OrderFile
if (-not (Test-Path $OrderPath)) {
    Write-Host "[FAIL] Order file not found: $OrderPath" -ForegroundColor Red
    exit 1
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "G7X REAL24 Runner Skeleton v1" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Order File: $OrderFile" -ForegroundColor Gray
Write-Host "Profile: $Profile" -ForegroundColor Gray
Write-Host "Python: $PYTHON" -ForegroundColor Gray
Write-Host ""

# Set profile environment variable
$env:G7_RUN_PROFILE = $Profile

# Step 1: Compiler Guard (pre-flight check)
Write-Host "[STEP 1/5] Running compiler guard..." -ForegroundColor Yellow
& $PYTHON "$SSOT_ROOT\main\pipeline\compiler_guard_v1.py" $OrderPath
if ($LASTEXITCODE -ne 0) {
    Write-Host "[FAIL] Compiler guard failed" -ForegroundColor Red
    exit 1
}
Write-Host "[PASS] Compiler guard OK" -ForegroundColor Green
Write-Host ""

# Step 2: Execute manager.py
Write-Host "[STEP 2/5] Executing manager.py (Profile=$Profile)..." -ForegroundColor Yellow
$ManagerOutput = & $PYTHON "$SSOT_ROOT\main\manager.py" $OrderPath 2>&1
$ManagerExitCode = $LASTEXITCODE

# Display manager output
Write-Host $ManagerOutput

# Extract RUN_PATH from output
$RunPath = $null
foreach ($line in $ManagerOutput -split "`n") {
    if ($line -match "TARGET_RUN_PATH:(.+)") {
        $RunPath = $matches[1].Trim()
        break
    }
}

if (-not $RunPath) {
    Write-Host "[FAIL] Could not extract RUN_PATH from manager output" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[INFO] RUN_PATH: $RunPath" -ForegroundColor Cyan
Write-Host "[INFO] Manager exitcode: $ManagerExitCode" -ForegroundColor Cyan
Write-Host ""

# Step 3: Check run artifacts
Write-Host "[STEP 3/5] Checking run artifacts..." -ForegroundColor Yellow
& $PYTHON "$SSOT_ROOT\tools\check_run_artifacts_v1.py"
if ($LASTEXITCODE -ne 0) {
    Write-Host "[FAIL] Run artifacts check failed" -ForegroundColor Red
    exit 1
}
Write-Host "[PASS] Run artifacts OK" -ForegroundColor Green
Write-Host ""

# Step 4: Error log check
Write-Host "[STEP 4/5] Checking error logs..." -ForegroundColor Yellow
& $PYTHON "$SSOT_ROOT\tools\error_log_check_v1.py"
if ($LASTEXITCODE -ne 0) {
    Write-Host "[FAIL] Error log check failed" -ForegroundColor Red
    exit 1
}
Write-Host "[PASS] Error log OK" -ForegroundColor Green
Write-Host ""

# Step 5: Final verdict
Write-Host "[STEP 5/5] Final verdict..." -ForegroundColor Yellow

$ExitcodeFile = Join-Path $RunPath "exitcode.txt"
if (Test-Path $ExitcodeFile) {
    $FinalExitcode = [int](Get-Content $ExitcodeFile -Raw).Trim()
    Write-Host "Final exitcode: $FinalExitcode" -ForegroundColor Gray

    if ($FinalExitcode -eq 0) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "REAL24 RUN PASSED" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "RUN_PATH: $RunPath" -ForegroundColor Cyan
        exit 0
    } else {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Red
        Write-Host "REAL24 RUN FAILED" -ForegroundColor Red
        Write-Host "========================================" -ForegroundColor Red
        Write-Host "RUN_PATH: $RunPath" -ForegroundColor Cyan
        Write-Host "Exitcode: $FinalExitcode" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[FAIL] exitcode.txt not found in RUN folder" -ForegroundColor Red
    exit 1
}
