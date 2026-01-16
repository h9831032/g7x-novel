# [PERSISTENCE_GUARD] 강제 종료 방지 적용
$env:GEMINI_API_KEY="형님의_API_키_직접입력"
$env:PYTHONUTF8=1

Write-Host " [START] FINAL_RESUME_SESSION 점화..." -ForegroundColor Cyan

#Saved Info 규칙: C:\g7core\g7_v1 경로일 경우 python 파일명.py로 실행
cd C:\g7core\g7_v1
python ops_seal_final_v6_resume.py

$EXIT_CODE = $LASTEXITCODE
Write-Host "`n" + "="*50
if ($EXIT_CODE -eq 0) {
    Write-Host " [SUCCESS] GOLD SEAL 확보. 12GB 본진 이사 가능." -ForegroundColor Green
} else {
    Write-Host " [FAIL] SEAL 파괴됨. stderr.txt 확인 필요 (Code: $EXIT_CODE)" -ForegroundColor Red
}
Write-Host "="*50

# [PERSISTENCE_GUARD] 사용자가 확인 전까지 창 닫힘 방지
Read-Host "Audit Done. Press Enter to Exit."