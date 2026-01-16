# G7X Night Queue (Complete - queue list based)
param(
  [Parameter(Mandatory=$false)]
  [string]$Root = "C:\g7core\g7_v1",
  [Parameter(Mandatory=$false)]
  [string]$QueueFile = "night_queue_list.txt"
)

$ErrorActionPreference = "Stop"

$PY = "$Root\.venv\Scripts\python.exe"

if (-not (Test-Path $PY)) {
  Write-Host "[FAIL] .venv not found: $PY"
  exit 1
}

Write-Host ""
Write-Host "=== G7X Night Queue ==="
Write-Host "Root: $Root"
Write-Host "Python: $PY"
Write-Host "Queue: $QueueFile"
Write-Host ""

$ManagerPath = Join-Path $Root "main\manager.py"
$QueuePath = Join-Path $Root "GPTORDER" $QueueFile
$GptorderDir = Join-Path $Root "GPTORDER"

if (-not (Test-Path $QueuePath)) {
  Write-Host "[FAIL] Queue file not found: $QueuePath"
  exit 1
}

$queueOrders = Get-Content $QueuePath | Where-Object { $_.Trim() -ne "" }

Write-Host "Queue contains $($queueOrders.Count) orders"
Write-Host ""

$queueIndex = 1
foreach ($orderFile in $queueOrders) {
  $orderFile = $orderFile.Trim()
  
  Write-Host "[QUEUE $queueIndex/$($queueOrders.Count)] Executing: $orderFile"
  
  & $PY $ManagerPath --order_path $orderFile --ssot_root $Root
  $exitcode = $LASTEXITCODE
  Write-Host "    Exitcode: $exitcode"
  Write-Host ""
  
  if ($exitcode -ne 0) {
    Write-Host "[WARN] Order $orderFile failed with exitcode $exitcode"
    Write-Host ""
  }
  
  $today = Get-Date -Format "yyyyMMdd"
  $retryFiles = Get-ChildItem -Path $GptorderDir -Filter "RETRY_WORK_$today*.txt" -ErrorAction SilentlyContinue
  
  if ($retryFiles.Count -gt 0) {
    $latestRetry = $retryFiles | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    
    Write-Host "[RETRY] Found retry file: $($latestRetry.Name)"
    Write-Host "[RETRY] Executing retry missions..."
    
    & $PY $ManagerPath --order_path $latestRetry.Name --ssot_root $Root
    $retryExitcode = $LASTEXITCODE
    Write-Host "    Retry exitcode: $retryExitcode"
    Write-Host ""
  }
  
  $queueIndex++
}

Write-Host "=== Night Queue Complete ==="
exit 0
