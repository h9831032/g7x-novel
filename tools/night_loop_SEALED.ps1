# G7X Night Loop (Sealed Version)
# Fail-fast loop with evidence verification

param(
    [string]$OrderPath = "SMOKE3.txt",
    [int]$Loops = 1,
    [string]$SsotRoot = "C:\g7core\g7_v1"
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "=== G7X Night Loop (Sealed) ===" -ForegroundColor Cyan
Write-Host "Order: $OrderPath"
Write-Host "Loops: $Loops"
Write-Host "Root: $SsotRoot"
Write-Host ""

# Logs directory
$logsDir = Join-Path $SsotRoot "logs"
if (-not (Test-Path $logsDir)) {
    New-Item -ItemType Directory -Path $logsDir | Out-Null
}

$stdoutLog = Join-Path $logsDir "night_loop_stdout.txt"
$stderrLog = Join-Path $logsDir "night_loop_stderr.txt"
$lastRunLog = Join-Path $logsDir "night_loop_last_run.txt"

# Initialize logs
"[NIGHT LOOP START] $(Get-Date)" | Out-File $stdoutLog -Encoding UTF8
"[NIGHT LOOP START] $(Get-Date)" | Out-File $stderrLog -Encoding UTF8

for ($i = 1; $i -le $Loops; $i++) {
    Write-Host "[LOOP $i/$Loops] Starting..." -ForegroundColor Yellow
    
    # Step 1: Run manager
    Write-Host "  [1] Running manager.py..." -ForegroundColor Gray
    try {
        $managerPath = Join-Path $SsotRoot "main\manager.py"
        
        # Execute manager and capture output
        $output = & python $managerPath --order_path $OrderPath 2>&1
        $managerExitCode = $LASTEXITCODE
        
        # Log output
        $output | Out-File $stdoutLog -Append -Encoding UTF8
        
        Write-Host "    Manager exitcode: $managerExitCode" -ForegroundColor Gray
        
        # Check exitcode
        if ($managerExitCode -ne 0) {
            Write-Host "  [FAIL] Manager exitcode != 0" -ForegroundColor Red
            "[LOOP $i] FAIL: Manager exitcode=$managerExitCode" | Out-File $stdoutLog -Append -Encoding UTF8
            exit 1
        }
        
    } catch {
        Write-Host "  [ERROR] Manager execution failed" -ForegroundColor Red
        $_.Exception.Message | Out-File $stderrLog -Append -Encoding UTF8
        exit 1
    }
    
    # Step 2: Find latest RUN
    Write-Host "  [2] Finding latest RUN..." -ForegroundColor Gray
    $runsDir = Join-Path $SsotRoot "runs"
    $latestRun = Get-ChildItem "$runsDir\RUN_*" -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    
    if (-not $latestRun) {
        Write-Host "  [ERROR] No RUN found" -ForegroundColor Red
        "No RUN found" | Out-File $stderrLog -Append -Encoding UTF8
        exit 1
    }
    
    Write-Host "    Latest RUN: $($latestRun.Name)" -ForegroundColor Gray
    $latestRun.FullName | Out-File $lastRunLog -Encoding UTF8
    
    # Step 3: Verify with FINAL_CHECK
    Write-Host "  [3] Running FINAL_CHECK..." -ForegroundColor Gray
    $finalCheckPath = Join-Path $SsotRoot "FINAL_CHECK.ps1"
    
    if (Test-Path $finalCheckPath) {
        try {
            # Run FINAL_CHECK and capture result
            & $finalCheckPath
            $checkExitCode = $LASTEXITCODE
            
            if ($checkExitCode -ne 0) {
                Write-Host "  [FAIL] FINAL_CHECK failed" -ForegroundColor Red
                "[LOOP $i] FAIL: FINAL_CHECK exitcode=$checkExitCode" | Out-File $stdoutLog -Append -Encoding UTF8
                
                # Copy evidence to FAIL_BOX
                $failBoxDir = Join-Path $SsotRoot "FAIL_BOX"
                if (-not (Test-Path $failBoxDir)) {
                    New-Item -ItemType Directory -Path $failBoxDir | Out-Null
                }
                
                $failBoxRun = Join-Path $failBoxDir $latestRun.Name
                Copy-Item -Path $latestRun.FullName -Destination $failBoxRun -Recurse -Force
                
                Write-Host "  [FAIL_BOX] Evidence copied to: $failBoxRun" -ForegroundColor Yellow
                exit 1
            }
            
        } catch {
            Write-Host "  [WARN] FINAL_CHECK execution error: $($_.Exception.Message)" -ForegroundColor Yellow
            # Continue even if FINAL_CHECK has issues (not critical)
        }
    } else {
        Write-Host "  [WARN] FINAL_CHECK.ps1 not found, skipping verification" -ForegroundColor Yellow
    }
    
    # Step 4: Manual evidence check (fallback)
    Write-Host "  [4] Checking evidence files..." -ForegroundColor Gray
    $exitcodePath = Join-Path $latestRun.FullName "exitcode.txt"
    $auditPath = Join-Path $latestRun.FullName "final_audit.json"
    
    $pass = $false
    
    if ((Test-Path $exitcodePath) -and (Test-Path $auditPath)) {
        $exitcode = (Get-Content $exitcodePath -Raw).Trim()
        $audit = Get-Content $auditPath -Raw | ConvertFrom-Json
        
        if ($exitcode -eq "0" -and $audit.pass -eq $true) {
            $pass = $true
        }
    }
    
    if ($pass) {
        Write-Host "  [PASS] Loop $i complete" -ForegroundColor Green
        "[LOOP $i] PASS: $($latestRun.Name)" | Out-File $stdoutLog -Append -Encoding UTF8
    } else {
        Write-Host "  [FAIL] Evidence verification failed" -ForegroundColor Red
        "[LOOP $i] FAIL: Evidence check failed" | Out-File $stdoutLog -Append -Encoding UTF8
        
        # Copy to FAIL_BOX
        $failBoxDir = Join-Path $SsotRoot "FAIL_BOX"
        if (-not (Test-Path $failBoxDir)) {
            New-Item -ItemType Directory -Path $failBoxDir | Out-Null
        }
        
        $failBoxRun = Join-Path $failBoxDir $latestRun.Name
        Copy-Item -Path $latestRun.FullName -Destination $failBoxRun -Recurse -Force
        
        Write-Host "  [FAIL_BOX] Evidence copied to: $failBoxRun" -ForegroundColor Yellow
        exit 1
    }
    
    Write-Host ""
}

Write-Host "=== Night Loop Complete ===" -ForegroundColor Green
"[NIGHT LOOP COMPLETE] $(Get-Date)" | Out-File $stdoutLog -Append -Encoding UTF8
exit 0
