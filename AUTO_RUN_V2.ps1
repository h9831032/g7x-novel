$ErrorActionPreference = "Stop"
# 형님 키 그대로 적용
$API_KEY = "AIzaSyBreX9jWMmxzCD7aySlpZ2I3PJUmcY1AgY"
# [FIX] 모델명 변경: gemini-2.0-flash-exp
$URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key=$API_KEY"

$TargetDir = "C:\g7core\g7_v1\runs\RUN_API_REAL_2.0"
$ChunkPath = "C:\g6core\g6_v24\data\umr\chunks"

Write-Host ">>> [START] Gemini 2.0 Flash 가동" -ForegroundColor Yellow

# 폴더 생성
if (-not (Test-Path $TargetDir)) { New-Item -ItemType Directory -Path "$TargetDir\payload" -Force | Out-Null }

# 소설 파일 읽기
if (-not (Test-Path $ChunkPath)) { throw "청크 폴더($ChunkPath)를 찾을 수 없습니다." }
$File = Get-ChildItem $ChunkPath -File | Select-Object -First 1
$Text = Get-Content $File.FullName -Raw -Encoding UTF8
$TextShort = $Text.Substring(0, [Math]::Min($Text.Length, 1500))

# JSON 바디
$PromptText = "당신은 냉철한 웹소설 편집자입니다. 다음 소설 원문에서 [설정 오류, 문장 석화, 말투 드리프트]를 찾아 JSON 배열로 직설적으로 보고하십시오. 원문: " + $TextShort
$Body = @{ contents = @( @{ parts = @( @{ text = $PromptText } ) } ) } | ConvertTo-Json -Depth 5

Write-Host ">>> [COMM] Google Gemini 2.0 Flash 서버 통신 시도..." -ForegroundColor Magenta

try {
    # 통신
    $Resp = Invoke-RestMethod -Uri $URL -Method Post -Body $Body -ContentType "application/json"
    $Result = $Resp.candidates[0].content.parts[0].text
    
    # 결과 저장
    $SavePath = "$TargetDir\payload\row_001_gemini2.json"
    $Result | Out-File $SavePath -Encoding UTF8
    
    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host " [SUCCESS] 2.0 Flash 통신 성공!" -ForegroundColor Green
    Write-Host " 결과 파일: $SavePath" -ForegroundColor White
    Write-Host "========================================" -ForegroundColor Green

} catch {
    Write-Host " [FAIL] 통신 실패 원인: $_" -ForegroundColor Red
    # 에러 상세 내용을 파일로 덤프
    $_ | Out-File "C:\g7core\g7_v1\last_api_error.txt"
}

Read-Host "확인 후 엔터"
