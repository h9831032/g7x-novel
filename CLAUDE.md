# CLAUDE.md — G7X 운영 규칙(요약판)

PROJECT=G7X / ROOT=C:\g7core\g7_v1

참조 문서: G7X_CLAUDE_GLOBAL_GUIDELINE_V3, SSOT_PROFILE_G7X_V3, 
G7X_GITHUB_CLAUDECODE_ADDENDUM_V1  (정책 ID만 쓰고 본문은 링크 문서 준수)

고정 규칙:
- VENV_LOCK: ROOT.venv만 사용 (python 단독 호출 금지)
- MAIN_ONLY_WELD + MANAGER_THIN_RULE + PIPELINE_SPLIT
- UNIT_RULE=6N(각 SLICE=3+3), 광역치환/전역 리포맷 금지
- CC_SAFE_WELD: 변경 파일 1~3개, 라인 단위 패치만 허용
- 코드만 추적: runs/, output/, logs/, data/ 등 산출물은 .gitignore 유지

작업 절차(매 변경 공통):
1) stamp_manifest(before)로 스냅샷
2) 국지 패치(1~3파일) → manager.py에서만 호출 용접
3) FINAL_CHECK.ps1 → night_loop.ps1 SMOKE3 1회 → REAL120_A 1회
4) 증거팩 최소 5종 수집: exitcode, run_path, verify_report, stamp_manifest, devlog 증가
5) stamp_manifest(after), runs\apply_diff.txt 기록
AUTO-FAIL: devlog 증가 없음 / done_missions 불일치 / api_error_count>0 / 금지 경로 수정 / 신규 엔트리 생성

GitHub 운용:
- main 직접푸시 금지. 항상 브랜치: cc/날짜_짧은목표  → PR 필수
- PR 본문에: 변경 파일(1~3), 라인 범위, 실행 증거(verify_min), stamp before/after, apply_diff.txt
