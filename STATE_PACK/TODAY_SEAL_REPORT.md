1) TODAY_SEAL_REPORT.md (오늘 봉인 리포트)
A. What is sealed (오늘 봉인된 것)

메인 엔트리 단일화: C:\g7core\g7_v1\main\manager.py만 실행 경로로 사용

devlog 자동 생성 용접: RUN 종료 루프에서 devlog가 자동으로 남음(루트 devlog + RUN 폴더)

FINAL_CHECK 봉인: powershell -ExecutionPolicy Bypass -File .\FINAL_CHECK.ps1 방식에서도 깨지지 않음

night_loop 봉인: manager 실행 → 최신 RUN → exitcode 확인 → FINAL_CHECK 실행 → PASS/FAIL 근거 출력

주문서 경로 정규화: GPTORDER\GPTORDER 같은 중복 경로 버그 제거

기준점 박제: C:\g7core\g7_v1\ANCHOR_RUN.txt 존재