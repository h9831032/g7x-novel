# G7X 증거팩 검증 스크립트 (VERIFY_COMMANDS.ps1)

Write-Host "`n=== G7X Evidence Pack Verification ===" -ForegroundColor Cyan

# 최신 RUN 찾기
$runs = Get-ChildItem "C:\g7core\g7_v1\runs\RUN_*" -Directory | Sort-Object Name -Descending
if ($runs.Count -eq 0) {
    Write-Host "[FAIL] No RUN found" -ForegroundColor Red
    exit 1
}

$latest = $runs[0].FullName
$runName = Split-Path $latest -Leaf
Write-Host "[CHECK] Latest RUN: $runName" -ForegroundColor Yellow
Write-Host "        Path: $latest`n" -ForegroundColor Gray

# 필수 파일 체크
$required = @{
    "verify_report.json" = $false
    "stamp_manifest.json" = $false
    "final_audit.json" = $false
    "exitcode.txt" = $false
    "blackbox_log.jsonl" = $false
    "api_receipt.jsonl" = $false
}

$missing = @()

foreach ($file in $required.Keys) {
    $path = Join-Path $latest $file
    if (Test-Path $path) {
        $size = (Get-Item $path).Length
        if ($size -eq 0) {
            Write-Host "  ❌ $file (0 bytes)" -ForegroundColor Red
            $missing += "$file (empty)"
        } else {
            Write-Host "  ✅ $file ($size bytes)" -ForegroundColor Green
            $required[$file] = $true
        }
    } else {
        Write-Host "  ❌ $file (missing)" -ForegroundColor Red
        $missing += $file
    }
}

# receipts 체크
Write-Host "`n[Receipts Check]" -ForegroundColor Cyan
$receiptsDir = Join-Path $latest "receipts\mission"
if (Test-Path $receiptsDir) {
    $receipts = Get-ChildItem "$receiptsDir\*.json"
    $count = $receipts.Count
    $valid = ($receipts | Where-Object { $_.Length -ge 200 }).Count
    $empty = ($receipts | Where-Object { $_.Length -eq 0 }).Count
    
    Write-Host "  Total: $count files" -ForegroundColor Yellow
    Write-Host "  Valid (>=200 bytes): $valid" -ForegroundColor Green
    Write-Host "  Empty: $empty" -ForegroundColor $(if ($empty -eq 0) { "Green" } else { "Red" })
    
    if ($valid -lt $count) {
        $missing += "receipts (some invalid)"
    }
} else {
    Write-Host "  ❌ receipts/mission not found" -ForegroundColor Red
    $missing += "receipts/mission"
}

# exitcode 체크
Write-Host "`n[Exitcode Check]" -ForegroundColor Cyan
$exitcodePath = Join-Path $latest "exitcode.txt"
$exitcode = "999"
if (Test-Path $exitcodePath) {
    $exitcode = (Get-Content $exitcodePath -Raw).Trim()
    if ($exitcode -eq "0") {
        Write-Host "  ✅ exitcode = 0" -ForegroundColor Green
    } else {
        Write-Host "  ❌ exitcode = $exitcode" -ForegroundColor Red
        $missing += "exitcode != 0"
    }
}

# final_audit 체크
Write-Host "`n[Final Audit Check]" -ForegroundColor Cyan
$auditPath = Join-Path $latest "final_audit.json"
if (Test-Path $auditPath) {
    $audit = Get-Content $auditPath -Raw | ConvertFrom-Json
    Write-Host "  pass: $($audit.pass)" -ForegroundColor $(if ($audit.pass) { "Green" } else { "Red" })
    Write-Host "  receipts_valid_count: $($audit.receipts_valid_count)"
    
    if (-not $audit.pass) {
        $missing += "final_audit.pass = false"
    }
}

# 최종 판정
Write-Host "`n=== FINAL VERDICT ===" -ForegroundColor Cyan
if ($missing.Count -eq 0 -and $exitcode -eq "0") {
    Write-Host "✅ PASS - All evidence complete" -ForegroundColor Green
    exit 0
} else {
    Write-Host "❌ FAIL - Issues:" -ForegroundColor Red
    foreach ($m in $missing) {
        Write-Host "  - $m" -ForegroundColor Red
    }
    exit 1
}