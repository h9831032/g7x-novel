# C:\g7core\g7_v1\ignite_real_night.ps1
$root = "C:\g7core\g7_v1"
$apiKey = "AIzaSyBreX9jWMmxzCD7aySlpZ2I3PJUmcY1AgY"
$env:PYTHONPATH = $root

Write-Host "`n[STEP 1] Generating 360 Orders..." -ForegroundColor Cyan
# 부사장님이 성공하신 생성기 스크립트 호출
pwsh -File "$root\tools\make_real360.ps1"

Write-Host "`n[STEP 2] Launching G7X Real Production Line..." -ForegroundColor Yellow
# 에러가 났던 복잡한 파이프라인 제거하고 다이렉트 실행
python -u "$root\main\manager.py" $apiKey

Write-Host "`n[FINISH] Operation Ended." -ForegroundColor Green
pause