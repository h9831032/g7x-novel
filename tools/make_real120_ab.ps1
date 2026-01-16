# C:\g7core\g7_v1\tools\make_real120_ab.ps1
$OrderDir = "C:\g7core\g7_v1\GPTORDER"
if (-not (Test-Path $OrderDir)) { New-Item -ItemType Directory -Path $OrderDir }

# Truck A 생성 (120줄)
$LinesA = for ($i=1; $i -le 120; $i++) { "TASK_V2|payload=box$([math]::Ceiling($i/6))_half$([math]::Ceiling($i/3)%2 + 1)_seq$($i.ToString('000'))" }
$LinesA | Out-File -FilePath "$OrderDir\REAL120_A.txt" -Encoding utf8

# Truck B 생성 (120줄)
$LinesB = for ($i=121; $i -le 240; $i++) { "TASK_V2|payload=box$([math]::Ceiling($i/6))_half$([math]::Ceiling($i/3)%2 + 1)_seq$($i.ToString('000'))" }
$LinesB | Out-File -FilePath "$OrderDir\REAL120_B.txt" -Encoding utf8

Write-Host ">>> SUCCESS: 240 Orders generated in GPTORDER (A/B)." -ForegroundColor Green