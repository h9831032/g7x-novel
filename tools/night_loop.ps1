# G7X Night Loop (venv strict mode)
param(
  [Parameter(Mandatory=$false)]
  [string]$OrderPath = "SMOKE3.txt",
  [Parameter(Mandatory=$false)]
  [int]$Loops = 1,
  [Parameter(Mandatory=$false)]
  [string]$Root = "C:\g7core\g7_v1"
)

$ErrorActionPreference = "Stop"

# CRITICAL: .venv only
$PY = "$Root\.venv\Scripts\python.exe"

if (-not (Test-Path $PY)) {
  Write-Host "[FAIL] .venv not found: $PY"
  exit 1
}

Write-Host ""
Write-Host "=== G7X Night Loop ==="
Write-Host "Order: $OrderPath"
Write-Host "Loops: $Loops"
Write-Host "Root: $Root"
Write-Host "Python: $PY"
Write-Host ""

$RunsRoot = Join-Path $Root "runs"
$FailBox = Join-Path $Root "FAIL_BOX"
New-Item -ItemType Directory -Force -Path $FailBox | Out-Null

for ($i=1; $i -le $Loops; $i++) {
  Write-Host "[LOOP $i/$Loops] Starting..."
  
  # Scan BEFORE
  $beforeRuns = @()
  if (Test-Path $RunsRoot) {
    $beforeRuns = Get-ChildItem $RunsRoot -Directory | Select-Object -ExpandProperty Name
  }
  
  Write-Host "  [1] Running manager..."
  $managerPath = Join-Path $Root "main\manager.py"
  & $PY $managerPath --order_path $OrderPath --ssot_root $Root
  $managerExit = $LASTEXITCODE
  Write-Host "    Manager exitcode: $managerExit"

  if ($managerExit -ne 0) {
    Write-Host "  [FAIL] manager exitcode != 0 (STOP)"
    exit 1
  }

  # Scan AFTER
  $afterRuns = @()
  if (Test-Path $RunsRoot) {
    $afterRuns = Get-ChildItem $RunsRoot -Directory | Select-Object -ExpandProperty Name
  }
  
  # Find NEW RUN
  $newRuns = $afterRuns | Where-Object { $beforeRuns -notcontains $_ }
  
  if ($newRuns.Count -eq 0) {
    Write-Host "  [FAIL] No new RUN created (STOP)"
    exit 1
  }
  
  $latestRunName = $newRuns | Sort-Object -Descending | Select-Object -First 1
  $latestRun = Join-Path $RunsRoot $latestRunName
  
  Write-Host "    Using RUN: $latestRunName"

  Write-Host "  [2] Checking exitcode..."
  $exitFile = Join-Path $latestRun "exitcode.txt"
  if (-not (Test-Path $exitFile)) {
    Write-Host "  [FAIL] exitcode.txt missing"
    Copy-Item $latestRun (Join-Path $FailBox $latestRunName) -Recurse -Force
    exit 1
  }

  $exitVal = (Get-Content $exitFile -ErrorAction SilentlyContinue | Select-Object -First 1).Trim()
  if ($exitVal -ne "0") {
    Write-Host "    exitcode: $exitVal"
    Write-Host "  [FAIL] exitcode != 0"
    Copy-Item $latestRun (Join-Path $FailBox $latestRunName) -Recurse -Force
    exit 1
  }
  Write-Host "    exitcode: 0"

  Write-Host "  [3] Running FINAL_CHECK..."
  $finalCheck = Join-Path $Root "FINAL_CHECK.ps1"
  if (Test-Path $finalCheck) {
    powershell -ExecutionPolicy Bypass -File $finalCheck
    $fc = $LASTEXITCODE
    Write-Host "    FINAL_CHECK exitcode: $fc"
    if ($fc -ne 0) {
      Write-Host "  [FAIL] FINAL_CHECK failed"
      Copy-Item $latestRun (Join-Path $FailBox $latestRunName) -Recurse -Force
      exit 1
    }
  } else {
    Write-Host "    FINAL_CHECK.ps1 not found -> SKIP"
  }

  Write-Host "  [PASS] $latestRunName"
  Write-Host ""
}

Write-Host "=== Night Loop Complete ==="
exit 0