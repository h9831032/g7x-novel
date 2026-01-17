# G7X Python Path Resolver v1
# Resolves python.exe path from .venv or v1.venv with FAIL_FAST

param(
    [string]$RootPath = "C:\g7core\g7_v1"
)

$ErrorActionPreference = "Stop"

# Check .venv first
$venv1 = Join-Path $RootPath ".venv\Scripts\python.exe"
if (Test-Path $venv1) {
    Write-Output $venv1
    exit 0
}

# Check v1.venv as fallback
$venv2 = Join-Path $RootPath "v1.venv\Scripts\python.exe"
if (Test-Path $venv2) {
    Write-Output $venv2
    exit 0
}

# FAIL_FAST: Neither found
Write-Host "[FAIL] Python path not found. Checked:" -ForegroundColor Red
Write-Host "  - $venv1" -ForegroundColor Red
Write-Host "  - $venv2" -ForegroundColor Red
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
Read-Host
exit 1
