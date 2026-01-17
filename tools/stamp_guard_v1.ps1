# G7X Stamp Guard v1
# Validates that MODEL_STAMP exists in latest RUN output
# Usage: stamp_guard_v1.ps1 [RUN_PATH]

param(
    [Parameter(Mandatory=$false)]
    [string]$RunPath = ""
)

$ErrorActionPreference = "Stop"
$SSOT_ROOT = "C:\g7core\g7_v1"
$RUNS_DIR = "$SSOT_ROOT\runs"

Write-Host "[STAMP_GUARD] Checking for MODEL_STAMP..." -ForegroundColor Cyan

# Find latest RUN if not specified
if (-not $RunPath) {
    if (-not (Test-Path $RUNS_DIR)) {
        Write-Host "[FAIL] Runs directory not found: $RUNS_DIR" -ForegroundColor Red
        exit 1
    }

    $runFolders = Get-ChildItem $RUNS_DIR -Directory | Where-Object { $_.Name -match "^RUN_" } | Sort-Object Name
    if ($runFolders.Count -eq 0) {
        Write-Host "[FAIL] No RUN folders found" -ForegroundColor Red
        exit 1
    }

    $RunPath = $runFolders[-1].FullName
}

Write-Host "[INFO] Checking RUN: $RunPath" -ForegroundColor Gray

# Check RUN path exists
if (-not (Test-Path $RunPath)) {
    Write-Host "[FAIL] RUN path not found: $RunPath" -ForegroundColor Red
    exit 1
}

# Find stdout or run_summary file
$stdoutFile = Join-Path $RunPath "stdout_manager.txt"
$summaryFile = Join-Path $RunPath "run_summary.txt"

$targetFile = $null
if (Test-Path $stdoutFile) {
    $targetFile = $stdoutFile
} elseif (Test-Path $summaryFile) {
    $targetFile = $summaryFile
} else {
    Write-Host "[FAIL] No stdout_manager.txt or run_summary.txt found in RUN folder" -ForegroundColor Red
    exit 1
}

Write-Host "[INFO] Checking file: $targetFile" -ForegroundColor Gray

# Read file content
try {
    $content = Get-Content $targetFile -Raw -Encoding UTF8
} catch {
    Write-Host "[FAIL] Cannot read file: $_" -ForegroundColor Red
    exit 1
}

# Search for MODEL_STAMP
if ($content -match "MODEL_STAMP:") {
    Write-Host "[PASS] MODEL_STAMP found" -ForegroundColor Green
    Write-Host "STAMP_OK: $RunPath" -ForegroundColor Green
    exit 0
} else {
    Write-Host "[FAIL] MODEL_STAMP not found in output" -ForegroundColor Red
    Write-Host "[FAIL] Missing MODEL_STAMP = work invalid" -ForegroundColor Red
    exit 1
}
