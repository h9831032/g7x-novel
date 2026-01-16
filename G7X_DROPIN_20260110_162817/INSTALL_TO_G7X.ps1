$ErrorActionPreference = "Stop"
$root = "C:\g7core\g7_v1"
$src = Split-Path -Parent $MyInvocation.MyCommand.Path
$engine = Join-Path $root "engine"
$gpt = Join-Path $root "GPTORDER"
New-Item -ItemType Directory -Force -Path $engine | Out-Null
New-Item -ItemType Directory -Force -Path $gpt | Out-Null

Copy-Item -Force (Join-Path $src "mission_catalog_v1.json") (Join-Path $engine "mission_catalog_v1.json")
Copy-Item -Force (Join-Path $src "REAL_MISSION_120_A.txt") (Join-Path $gpt "REAL_MISSION_120_A.txt")
Copy-Item -Force (Join-Path $src "REAL_MISSION_120_B.txt") (Join-Path $gpt "REAL_MISSION_120_B.txt")

Write-Host "OK: mission_catalog -> engine\mission_catalog_v1.json"
Write-Host "OK: orders -> GPTORDER\REAL_MISSION_120_A.txt / REAL_MISSION_120_B.txt"
