<# 
G7X verify_latest_run.ps1
가장 최신 RUN 폴더를 자동으로 찾아서 검문
사용법: .\verify_latest_run.ps1 -ExpectedMissions 120
#>

param(
    [Parameter(Mandatory=$false)]
    [int]$ExpectedMissions = 120
)

$RunsDir = "C:\g7core\g7_v1\runs"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "G7X LATEST RUN FINDER" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if (-not (Test-Path $RunsDir)) {
    Write-Host "[FAIL] Runs directory not found: $RunsDir" -ForegroundColor Red
    exit 1
}

# LastWriteTime 기준으로 가장 최신 RUN_* 폴더 찾기
$latestRun = Get-ChildItem -Path $RunsDir -Directory -Filter "RUN_*" | 
    Sort-Object LastWriteTime -Descending | 
    Select-Object -First 1

if (-not $latestRun) {
    Write-Host "[FAIL] No RUN_* folders found in $RunsDir" -ForegroundColor Red
    exit 1
}

$RunPath = $latestRun.FullName
Write-Host "Latest RUN: $RunPath"
Write-Host "LastWriteTime: $($latestRun.LastWriteTime)"
Write-Host ""

# verify_run.ps1 호출
$verifyScript = Join-Path $PSScriptRoot "verify_run.ps1"
if (Test-Path $verifyScript) {
    & $verifyScript -RunPath $RunPath -ExpectedMissions $ExpectedMissions
} else {
    # verify_run.ps1이 없으면 직접 검사
    Write-Host "[INFO] verify_run.ps1 not found, running inline check..." -ForegroundColor Yellow
    
    $pass = $true
    
    # exitcode 체크
    $exitcodePath = Join-Path $RunPath "exitcode.txt"
    if (Test-Path $exitcodePath) {
        $ec = (Get-Content $exitcodePath -Raw).Trim()
        Write-Host "exitcode: $ec"
        if ($ec -ne "0") { $pass = $false }
    } else {
        Write-Host "exitcode.txt: MISSING" -ForegroundColor Red
        $pass = $false
    }
    
    # receipts 체크
    $receiptsDir = Join-Path $RunPath "receipts\mission"
    if (Test-Path $receiptsDir) {
        $cnt = (Get-ChildItem -Path $receiptsDir -Filter "*.json").Count
        Write-Host "receipts: $cnt / $ExpectedMissions"
        if ($cnt -lt $ExpectedMissions) { $pass = $false }
    } else {
        Write-Host "receipts: MISSING" -ForegroundColor Red
        $pass = $false
    }
    
    # api_receipt 체크
    $apiPath = Join-Path $RunPath "api_receipt.jsonl"
    if (Test-Path $apiPath) {
        $lines = (Get-Content $apiPath | Where-Object { $_.Trim() }).Count
        Write-Host "api_lines: $lines / $ExpectedMissions"
        if ($lines -lt $ExpectedMissions) { $pass = $false }
    } else {
        Write-Host "api_receipt.jsonl: MISSING" -ForegroundColor Red
        $pass = $false
    }
    
    # final_audit 체크
    $auditPath = Join-Path $RunPath "final_audit.json"
    if (Test-Path $auditPath) {
        $audit = Get-Content $auditPath -Raw | ConvertFrom-Json
        Write-Host "final_audit.pass: $($audit.pass)"
        Write-Host "reason_code: $($audit.reason_code)"
        if ($audit.pass -ne $true) { $pass = $false }
    } else {
        Write-Host "final_audit.json: MISSING" -ForegroundColor Red
        $pass = $false
    }
    
    Write-Host ""
    if ($pass) {
        Write-Host "[FINAL] PASS" -ForegroundColor Green
        exit 0
    } else {
        Write-Host "[FINAL] FAIL" -ForegroundColor Red
        exit 1
    }
}
