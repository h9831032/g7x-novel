# [MANDATE] OPS_FINAL_ULTIMATE 실행 및 봉인 확인 스크립트
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$EnginePath = Join-Path $ScriptDir "ops\ops_seal_v4_ultimate.py"

# 1. 환경 변수 주입 (UTF-8 폭탄 방어 및 API 키)
$env:PYTHONUTF8 = 1
Write-Host "[OPS] Checking Environment..." -ForegroundColor Cyan

if (-not $env:GEMINI_API_KEY) {
    Write-Host "[CRITICAL] GEMINI_API_KEY environment variable is missing." -ForegroundColor Red
    Write-Host "Please set it: `$env:GEMINI_API_KEY='YourKey'" -ForegroundColor Yellow
    Read-Host "Press Enter to exit..."
    exit 1
}

# 2. 엔진 가동
Write-Host "[OPS] Starting Final Seal V4 Ultimate Engine (Model: gemini-2.5-flash)..." -ForegroundColor Green
python $EnginePath

# 3. 종료 코드 획득 및 박제
$ExitCode = $LASTEXITCODE
Write-Host "[OPS] Engine finished with ExitCode: $ExitCode" -ForegroundColor ($ExitCode -eq 0 ? "Green" : "Red")

# 가장 최근에 생성된 runs 폴더를 찾아 exitcode.txt 기록
$LatestRun = Get-ChildItem "runs" | Sort-Object CreationTime -Descending | Select-Object -First 1
if ($LatestRun) {
    $ExitFile = Join-Path $LatestRun.FullName "exitcode.txt"
    $ExitCode | Out-File -FilePath $ExitFile -Encoding utf8
    Write-Host "[OPS] Saved ExitCode to: $ExitFile" -ForegroundColor Gray
    
    # verify_report.json 존재 확인
    $VerifyFile = Join-Path $LatestRun.FullName "verify_report.json"
    if (Test-Path $VerifyFile) {
        Write-Host "[OPS] Verification Report found. Checking pass status..." -ForegroundColor Cyan
        Get-Content $VerifyFile | ConvertFrom-Json | Select-Object pass, trucks, injections, drift
    }
}

Write-Host "`n[Audit Done] 모든 작업이 완료되었습니다. 이사 준비를 시작하십시오." -ForegroundColor Green
Read-Host "엔터를 누르면 창이 닫힙니다."