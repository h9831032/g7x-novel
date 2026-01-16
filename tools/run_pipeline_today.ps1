# C:\g7core\g7_v1\tools\run_pipeline_today.ps1
$root = "C:\g7core\g7_v1"
$run_id = "RUN_" + (Get-Date -Format "yyyyMMdd_HHmmss")
$target = "20260107_PATCH"
$run_dir = "$root\runs\REAL\$run_id"

# 인코딩 가드
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

try {
    if (!(Test-Path $run_dir)) { New-Item -ItemType Directory -Force -Path $run_dir | Out-Null }
    
    Write-Host "--- STAGE 0: PYTHON PATH VALIDATION ---" -ForegroundColor Gray
    $real_py = "$env:LOCALAPPDATA\Programs\Python\Python310\python.exe"
    if (!(Test-Path $real_py)) { $real_py = "python.exe" }
    Write-Host "Real Python Target: $real_py"

    Write-Host "--- STAGE 1: ORDER GENERATION (UNIT=120) ---" -ForegroundColor Cyan
    & $real_py "$root\tools\create_orders_quick240.py" --mode production --target $target --unit 120
    if ($LASTEXITCODE -ne 0) { throw "Stage 1 failed." }

    Write-Host "--- STAGE 2: MAIN EXECUTION (STUB) ---" -ForegroundColor Cyan
    & $real_py -u "$root\main.py" --mode production --target $target --run_id $run_id > "$run_dir\stdout.txt" 2> "$run_dir\stderr.txt"
    $LASTEXITCODE | Out-File -FilePath "$run_dir\exitcode.txt"

    Write-Host "--- STAGE 3: AUDIT ---" -ForegroundColor Cyan
    & $real_py "$root\tools\devlog_manager.py" --run_id $run_id

    Write-Host "--- STAGE 4: HASH ---" -ForegroundColor Cyan
    $files = "$root\main.py", "$root\tools\create_orders_quick240.py", "$root\tools\devlog_manager.py", "$PSCommandPath"
    foreach ($f in $files) {
        if (Test-Path $f) { Get-FileHash -Algorithm SHA1 $f | Out-File -Append -FilePath "$run_dir\hash_manifest.txt" -Encoding utf8 }
    }

    Write-Host "`n[PASS] EVIDENCE PACK CREATED AT: $run_dir" -ForegroundColor Green
    if (Test-Path "$run_dir\verify_report.json") { Get-Content "$run_dir\verify_report.json" | ConvertFrom-Json | Format-List }
}
catch {
    Write-Host "`n[CRITICAL_FAIL] $($_.Exception.Message)" -ForegroundColor Red
}
finally {
    Write-Host "`n[HALT] Press Enter to exit..."
    Read-Host
}