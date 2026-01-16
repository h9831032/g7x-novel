G7X DROP-IN (미션 카탈로그 + GPTORDER 120)

목표
- "제미나이에게 하청"이 아니라, 너 로컬에서 manager.py가 주문서를 읽고 API(Gemini)를 직접 때리게 하는 실전 총알

포함 파일
- mission_catalog_v1.json
- REAL_MISSION_120_A.txt (60발)
- REAL_MISSION_120_B.txt (60발)
- INSTALL_TO_G7X.ps1

설치
- 압축 풀고, PowerShell에서:
  pwsh -File .\INSTALL_TO_G7X.ps1

실행(형아가 쓰는 venv python으로)
- python C:\g7core\g7_v1\main\manager.py "REAL_MISSION_120_A.txt"
- python C:\g7core\g7_v1\main\manager.py "REAL_MISSION_120_B.txt"

주의(중요)
- manager.py가 TASK_V3|mission=... 과 engine\mission_catalog_v1.json 을 아직 해석 못하면
  실행은 FAIL이 나야 정상이다(가라 금지).
  그 경우 다음 단계에서 manager.py 라우터/로더를 바로 용접하면 된다.
