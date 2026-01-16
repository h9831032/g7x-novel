# C:\g7core\g7_v1\tools\orders\make_real120_ab.ps1
$OrderDir = "C:\g7core\g7_v1\GPTORDER"
if (-not (Test-Path $OrderDir)) { New-Item -ItemType Directory -Path $OrderDir }

function Create-Truck($Name, $Start, $End) {
    $Lines = New-Object System.Collections.Generic.List[string]
    for ($i=$Start; $i -le $End; $i++) {
        $box = [math]::Ceiling($i/6)
        $half = if ($i % 6 -le 3 -and $i % 6 -ne 0) { 1 } else { 2 }
        $seq = $i.ToString("000")
        $Lines.Add("TASK_V2|payload=box${box}_half${half}_seq${seq}")
    }
    $Lines | Out-File -FilePath "$OrderDir\$Name.txt" -Encoding utf8 -NoNewline
}

Create-Truck "REAL120_A" 1 120
Create-Truck "REAL120_B" 121 240
Write-Host ">>> SUCCESS: 240 Orders generated in GPTORDER." -ForegroundColor Green