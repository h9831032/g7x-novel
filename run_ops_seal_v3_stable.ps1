# [PATCH] 파이썬 인코딩 환경변수 강제 주입
$env:PYTHONUTF8=1
$env:GEMINI_API_KEY="AIzaSyBreX9jWMmxzCD7aySlpZ2I3PJUmcY1AgY"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$EnginePath = Join-Path $ScriptDir "ops\ops_seal_v3_final.py"

Write-Host "[OPS] Starting Final Seal V3.1..." -ForegroundColor Green
python $EnginePath

$ExitCode = $LASTEXITCODE
Write-Host "[OPS] ExitCode: $ExitCode" -ForegroundColor ($ExitCode -eq 0 ? "Green" : "Red")

$LatestRun = Get-ChildItem "runs" | Sort-Object CreationTime -Descending | Select-Object -First 1
if ($LatestRun) {
    Set-Content -Path (Join-Path $LatestRun.FullName "exitcode.txt") -Value $ExitCode
}
Read-Host "Audit Done. Press Enter..."