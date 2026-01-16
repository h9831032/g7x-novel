$root = "C:\g7core\g7_v1"
$apiKey = "AIzaSyBreX9jWMmxzCD7aySlpZ2I3PJUmcY1AgY"
$env:PYTHONPATH = $root

Write-Host "`n[STEP 1] Generating 360 Real Orders..." -ForegroundColor Cyan
if (-not (Test-Path "$root\tools\make_real360.ps1")) {
    Write-Host "!!! [FAIL] make_real360.ps1 is missing!" -ForegroundColor Red
    return
}
pwsh -File "$root\tools\make_real360.ps1"

Write-Host "`n[STEP 2] Launching G7X Real Production Line (Gemini 2.5 Flash)..." -ForegroundColor Yellow
python -u "$root\main\manager.py" $apiKey

Write-Host "`n[FINISH] Operation Ended." -ForegroundColor Green
pause
