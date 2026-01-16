$ErrorActionPreference = "Stop"
$API_KEY = "AIzaSyBreX9jWMmxzCD7aySlpZ2I3PJUmcY1AgY"
$URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=$API_KEY"
$TargetDir = "C:\g7core\g7_v1\runs\RUN_API_REAL_ACTION"
$ChunkPath = "C:\g6core\g6_v24\data\umr\chunks"

Write-Host ">>> [START] API 엔진 가동 (물리 파일 생성 모드)" -ForegroundColor Yellow

# 폴더 생성
New-Item -ItemType Directory -Path "$TargetDir\payload" -Force | Out-Null

# 소설 파일 읽기
if (-not (Test-Path $ChunkPath)) { throw "청크 폴더 없음" }
$File = Get-ChildItem $ChunkPath -File | Select-Object -First 1
$Text = Get-Content $File.FullName -Raw -Encoding UTF8

# JSON 바디 생성 (단순 문자열 조합)
$PromptText = "이 소설에서 설정 오류와 어색한 문장을 찾아 JSON으로 답하시오. 소설내용: " + $Text.Substring(0, [Math]::Min($Text.Length, 1000))
$Body = @{ contents = @( @{ parts = @( @{ text = $PromptText } ) } ) } | ConvertTo-Json -Depth 5

Write-Host ">>> [COMM] 구글 본사와 통신 중..." -ForegroundColor Magenta

try {
    # 통신 시도
    $Resp = Invoke-RestMethod -Uri $URL -Method Post -Body $Body -ContentType "application/json"
    $Result = $Resp.candidates[0].content.parts[0].text
    
    # 결과 저장
    $SavePath = "$TargetDir\payload\row_001.json"
    $Result | Out-File $SavePath -Encoding UTF8
    
    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host " [SUCCESS] 동작 완료! 영수증 확인하세요." -ForegroundColor Green
    Write-Host " 저장 경로: $SavePath" -ForegroundColor White
    Write-Host "========================================" -ForegroundColor Green

} catch {
    Write-Host " [FAIL] 통신 실패: $_" -ForegroundColor Red
}

Read-Host "작업 끝. 엔터 치면 닫힘"
