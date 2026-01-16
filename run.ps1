# C:\g7core\g7_v1\run.ps1
param(
    [string]$run_id = "auto",
    [int]$text_only = 0,
    [int]$unit = 0,
    [string]$writer_mode = "REAL",
    [int]$purge = 0
)

$base_dir = "C:\g7core\g7_v1"
$run_dir = "$base_dir\runs\$run_id"
$manager_path = "$base_dir\main\manager.py"

if (-not (Test-Path $run_dir)) { New-Item -ItemType Directory -Path $run_dir -Force }

# [TEXTONLY_HARDLOCK]
if ($text_only -eq 1) { $unit = 0 }

Write-Host "WELDING_CHECK: Starting G7X Factory (Final Direct Mode)..."

# 에러가 발생하는 파이프라인을 제거하고, 파이썬을 직접 호출합니다.
# 대신 manager.py 내부에서 이미 로그를 남기므로, 화면 출력을 우선시합니다.
python.exe "$manager_path" --run_id "$run_id" --text_only $text_only --unit $unit --writer_mode "$writer_mode" --purge $purge

Write-Host "`n--- EXECUTION FINISHED ---"
if (Test-Path "$run_dir\final_audit.json") {
    $audit = Get-Content "$run_dir\final_audit.json" | ConvertFrom-Json
    $color = if($audit.status -eq "PASS") {"Green"} else {"Red"}
    Write-Host "FINAL_VERDICT: $($audit.status) (ExitCode: $($audit.exit_code))" -ForegroundColor $color
}