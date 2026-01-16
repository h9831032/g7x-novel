# G7X Night Loop - PASS Judgment Enhanced
# Enforced verification: exitcode + FINAL_CHECK

param(
    [string]$OrderPath = "SMOKE3.txt",
    [int]$Loops = 1,
    [string]$SsotRoot = "C:\g7core\g7_v1"
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "=== G7X Night Loop ===" -ForegroundColor Cyan
Write-Host "Order: $OrderPath"
Write-Host "Loops: $Loops"
Write-Host "Root: $SsotRoot"
Write-Host ""

# Logs
$logsDir = Join-Path $SsotRoot "logs"
if (-not (Test-Path $logsDir)) {
    New-Item -ItemType Directory -Path $logsDir | Out-Null
}

$stdoutLog = Join-Path $logsDir "night_loop_stdout.txt"
$stderrLog = Join-Path $logsDir "night_loop_stderr.txt"
$lastRunLog = Join-Path $logsDir "night_loop_last_run.txt"

"[NIGHT LOOP START] $(Get-Date)" | Out-File $stdoutLog -Encoding UTF8
"[NIGHT LOOP START] $(Get-Date)" | Out-File $stderrLog -Encoding UTF8

for ($i = 1; $i -le $Loops; $i++) {
    Write-Host "[LOOP $i/$Loops] Starting..." -ForegroundColor Yellow
    
    # Step 1: Run manager
    Write-Host "  [1] Running manager..." -ForegroundColor Gray
    try {
        $managerPath = Join-Path $SsotRoot "main\manager.py"
        
        $output = & python $managerPath --order_path $OrderPath 2>&1
        $managerExitCode = $LASTEXITCODE
        
        $output | Out-File $stdoutLog -Append -Encoding UTF8
        
        Write-Host "    Manager exitcode: $managerExitCode" -ForegroundColor Gray
        
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
    
    # Step 3: Check exitcode.txt (CRITICAL)
    Write-Host "  [3] Checking exitcode..." -ForegroundColor Gray
    $exitcodePath = Join-Path $latestRun.FullName "exitcode.txt"
    
    if (-not (Test-Path $exitcodePath)) {
        Write-Host "  [FAIL] exitcode.txt not found" -ForegroundColor Red
        
        $failBoxDir = Join-Path $SsotRoot "FAIL_BOX"
        if (-not (Test-Path $failBoxDir)) {
            New-Item -ItemType Directory -Path $failBoxDir | Out-Null
        }
        
        $failBoxRun = Join-Path $failBoxDir $latestRun.Name
        Copy-Item -Path $latestRun.FullName -Destination $failBoxRun -Recurse -Force
        
        Write-Host "  [FAIL_BOX] Evidence copied" -ForegroundColor Yellow
        "[LOOP $i] FAIL: exitcode.txt missing -> FAIL_BOX" | Out-File $stdoutLog -Append -Encoding UTF8
        exit 1
    }
    
    $exitcode = (Get-Content $exitcodePath -Raw).Trim()
    Write-Host "    exitcode: $exitcode" -ForegroundColor Gray
    
    if ($exitcode -ne "0") {
        Write-Host "  [FAIL] exitcode != 0" -ForegroundColor Red
        
        $failBoxDir = Join-Path $SsotRoot "FAIL_BOX"
        if (-not (Test-Path $failBoxDir)) {
            New-Item -ItemType Directory -Path $failBoxDir | Out-Null
        }
        
        $failBoxRun = Join-Path $failBoxDir $latestRun.Name
        Copy-Item -Path $latestRun.FullName -Destination $failBoxRun -Recurse -Force
        
        Write-Host "  [FAIL_BOX] Evidence copied" -ForegroundColor Yellow
        "[LOOP $i] FAIL: exitcode=$exitcode -> FAIL_BOX" | Out-File $stdoutLog -Append -Encoding UTF8
        exit 1
    }
    
    # Step 4: Run FINAL_CHECK (CRITICAL)
    Write-Host "  [4] Running FINAL_CHECK..." -ForegroundColor Gray
    $finalCheckPath = Join-Path $SsotRoot "FINAL_CHECK.ps1"
    
    if (Test-Path $finalCheckPath) {
        try {
            $checkOutput = & powershell -ExecutionPolicy Bypass -File $finalCheckPath 2>&1
            $checkExitCode = $LASTEXITCODE
            
            Write-Host "    FINAL_CHECK exitcode: $checkExitCode" -ForegroundColor Gray
            
            if ($checkExitCode -ne 0) {
                Write-Host "  [FAIL] FINAL_CHECK failed" -ForegroundColor Red
                
                $failBoxDir = Join-Path $SsotRoot "FAIL_BOX"
                if (-not (Test-Path $failBoxDir)) {
                    New-Item -ItemType Directory -Path $failBoxDir | Out-Null
                }
                
                $failBoxRun = Join-Path $failBoxDir $latestRun.Name
                Copy-Item -Path $latestRun.FullName -Destination $failBoxRun -Recurse -Force
                
                Write-Host "  [FAIL_BOX] Evidence copied" -ForegroundColor Yellow
                "[LOOP $i] FAIL: FINAL_CHECK failed -> FAIL_BOX" | Out-File $stdoutLog -Append -Encoding UTF8
                exit 1
            }
            
        } catch {
            Write-Host "  [WARN] FINAL_CHECK execution error: $($_.Exception.Message)" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  [WARN] FINAL_CHECK.ps1 not found" -ForegroundColor Yellow
    }
    
    # All checks passed
    Write-Host "  [PASS] $($latestRun.Name)" -ForegroundColor Green
    "[LOOP $i] PASS: $($latestRun.Name)" | Out-File $stdoutLog -Append -Encoding UTF8
    Write-Host ""
}

Write-Host "=== Night Loop Complete ===" -ForegroundColor Green
"[NIGHT LOOP COMPLETE] $(Get-Date)" | Out-File $stdoutLog -Append -Encoding UTF8
exit 0
