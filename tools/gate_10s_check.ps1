$root = "C:\g7core\g7_v1"
# 최신 RUN 폴더 탐색
$latestRun = Get-ChildItem "$root\runs" -Directory | Sort-Object CreationTime -Descending | Select-Object -First 1

if ($null -eq $latestRun) { 
    Write-Host ">>> [ERROR] No RUN folder found in $root\runs"
    exit 1 
}

# [FIX] .FullName을 사용하여 정확한 절대 경로 참조
$targetDir = $latestRun.FullName
Write-Host ">>> Checking: $targetDir"

$verifyJson = Get-Content "$targetDir\verify_report.json" | ConvertFrom-Json
$exitcode = Get-Content "$targetDir\exitcode.txt"
$rawCount = (Get-ChildItem "$targetDir\api_raw" -File).Count
$receiptLines = (Get-Content "$targetDir\api_receipt.jsonl").Count

# 숫자 6개 출력 (지시서 규격)
Write-Host "`n[GATE_CHECK_RESULT]"
Write-Host "$exitcode"
Write-Host "$($verifyJson.success)"
Write-Host "$($verifyJson.skip)"
Write-Host "$($verifyJson.fail)"
Write-Host "$rawCount"
Write-Host "$receiptLines"