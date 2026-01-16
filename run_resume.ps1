# [Console] 인코딩 강제 고정 (UTF8BOM)
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($true)
chcp 65001

$ROOT = "C:\g7core\g7_v1"
$scriptPath = Join-Path $ROOT "run_resume.ps1"

# 1. 파일 존재 강제 체크 및 재생성 (Set-Content UTF8)
$content = @'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($true)
chcp 65001
$statePath = "C:\g7core\g7_v1\runs\REAL\truckF\state_pack.json"
if (Test-Path $statePath) {
    $state = Get-Content $statePath | ConvertFrom-Json
    Write-Host ">>> [RESUME] 지점($($state.total))부터 재가동" -ForegroundColor Cyan
    python C:\g7core\g7_v1\tools\run_integrated_v9.py "F" "C:\g7core\g7_v1\runs\REAL"
}
'@
Set-Content -Path $scriptPath -Value $content -Encoding UTF8

# 2. 실행 위치 검증 (LEGACY 실행 방어)
if ($PWD.Path -ne $ROOT) {
    Write-Host "!!! [FAIL] 실행 위치 위반. C:\g7core\g7_v1에서만 실행 가능합니다." -ForegroundColor Red
    exit 1
}

& $scriptPath