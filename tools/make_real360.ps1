$OrderDir = "C:\g7core\g7_v1\GPTORDER"
if (-not (Test-Path $OrderDir)) { New-Item -ItemType Directory -Path $OrderDir }
function Create-Truck($Name, $Start, $End) {
    $Lines = for ($i=$Start; $i -le $End; $i++) { "TASK_V2|job=box$([math]::Ceiling($i/6))_half$([math]::Ceiling($i/3)%2 + 1)_seq$($i.ToString('000'))|payload=CHUNK_$i" }
    $Lines | Out-File -FilePath "$OrderDir\$Name.txt" -Encoding utf8
}
Create-Truck "REAL120_A" 1 120
Create-Truck "REAL120_B" 121 240
Create-Truck "REAL120_C" 241 360
Write-Host ">>> SUCCESS: 360 Orders generated." -ForegroundColor Green
