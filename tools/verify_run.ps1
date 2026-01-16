<# 
G7X verify_run.ps1
단독 RUN 폴더 검문 스크립트
사용법: .\verify_run.ps1 -RunPath "C:\g7core\g7_v1\runs\RUN_xxxxx" -ExpectedMissions 120
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$RunPath,
    
    [Parameter(Mandatory=$false)]
    [int]$ExpectedMissions = 120
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "G7X RUN VERIFY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "RUN: $RunPath"
Write-Host "Expected: $ExpectedMissions missions"
Write-Host ""

if (-not (Test-Path $RunPath)) {
    Write-Host "[FAIL] RUN path does not exist: $RunPath" -ForegroundColor Red
    exit 1
}

$pass = $true
$state = @{}

# 1. 필수 파일 체크
$requiredFiles = @(
    "verify_report.json",
    "stamp_manifest.json", 
    "final_audit.json",
    "exitcode.txt",
    "blackbox_log.jsonl",
    "api_receipt.jsonl"
)

Write-Host "[CHECK] Required files:" -ForegroundColor Yellow
foreach ($f in $requiredFiles) {
    $filePath = Join-Path $RunPath $f
    $exists = Test-Path $filePath
    $state[$f] = $exists
    if ($exists) {
        Write-Host "  [OK] $f" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] $f" -ForegroundColor Red
        $pass = $false
    }
}

# 2. exitcode 값 체크
Write-Host ""
Write-Host "[CHECK] exitcode.txt value:" -ForegroundColor Yellow
$exitcodePath = Join-Path $RunPath "exitcode.txt"
if (Test-Path $exitcodePath) {
    $exitcode = (Get-Content $exitcodePath -Raw).Trim()
    $state["exitcode_value"] = $exitcode
    if ($exitcode -eq "0") {
        Write-Host "  [OK] exitcode = 0" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] exitcode = $exitcode (expected 0)" -ForegroundColor Red
        $pass = $false
    }
} else {
    Write-Host "  [FAIL] exitcode.txt missing" -ForegroundColor Red
    $pass = $false
}

# 3. receipts 개수 체크
Write-Host ""
Write-Host "[CHECK] receipts/mission/*.json:" -ForegroundColor Yellow
$receiptsDir = Join-Path $RunPath "receipts\mission"
if (Test-Path $receiptsDir) {
    $receiptsCount = (Get-ChildItem -Path $receiptsDir -Filter "*.json").Count
    $state["receipts_count"] = $receiptsCount
    if ($receiptsCount -ge $ExpectedMissions) {
        Write-Host "  [OK] receipts = $receiptsCount (expected >= $ExpectedMissions)" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] receipts = $receiptsCount (expected >= $ExpectedMissions)" -ForegroundColor Red
        $pass = $false
    }
} else {
    Write-Host "  [FAIL] receipts/mission directory missing" -ForegroundColor Red
    $pass = $false
}

# 4. api_receipt.jsonl 라인 수 체크
Write-Host ""
Write-Host "[CHECK] api_receipt.jsonl lines:" -ForegroundColor Yellow
$apiReceiptPath = Join-Path $RunPath "api_receipt.jsonl"
if (Test-Path $apiReceiptPath) {
    $apiLines = (Get-Content $apiReceiptPath | Where-Object { $_.Trim() }).Count
    $state["api_lines"] = $apiLines
    if ($apiLines -ge $ExpectedMissions) {
        Write-Host "  [OK] api_lines = $apiLines (expected >= $ExpectedMissions)" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] api_lines = $apiLines (expected >= $ExpectedMissions)" -ForegroundColor Red
        $pass = $false
    }
} else {
    Write-Host "  [FAIL] api_receipt.jsonl missing" -ForegroundColor Red
    $pass = $false
}

# 5. final_audit.json pass 체크
Write-Host ""
Write-Host "[CHECK] final_audit.json pass:" -ForegroundColor Yellow
$auditPath = Join-Path $RunPath "final_audit.json"
if (Test-Path $auditPath) {
    try {
        $audit = Get-Content $auditPath -Raw | ConvertFrom-Json
        $auditPass = $audit.pass
        $state["audit_pass"] = $auditPass
        if ($auditPass -eq $true) {
            Write-Host "  [OK] final_audit.pass = true" -ForegroundColor Green
        } else {
            Write-Host "  [FAIL] final_audit.pass = $auditPass" -ForegroundColor Red
            Write-Host "  reason_code: $($audit.reason_code)" -ForegroundColor Yellow
            $pass = $false
        }
    } catch {
        Write-Host "  [FAIL] Cannot parse final_audit.json" -ForegroundColor Red
        $pass = $false
    }
} else {
    Write-Host "  [FAIL] final_audit.json missing" -ForegroundColor Red
    $pass = $false
}

# 6. blackbox_log.jsonl 비어있지 않은지 체크
Write-Host ""
Write-Host "[CHECK] blackbox_log.jsonl not empty:" -ForegroundColor Yellow
$blackboxPath = Join-Path $RunPath "blackbox_log.jsonl"
if (Test-Path $blackboxPath) {
    $bbSize = (Get-Item $blackboxPath).Length
    if ($bbSize -gt 0) {
        Write-Host "  [OK] blackbox size = $bbSize bytes" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] blackbox is empty" -ForegroundColor Red
        $pass = $false
    }
} else {
    Write-Host "  [FAIL] blackbox_log.jsonl missing" -ForegroundColor Red
    $pass = $false
}

# 최종 결과
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
if ($pass) {
    Write-Host "[FINAL] PASS" -ForegroundColor Green
    exit 0
} else {
    Write-Host "[FINAL] FAIL" -ForegroundColor Red
    exit 1
}
