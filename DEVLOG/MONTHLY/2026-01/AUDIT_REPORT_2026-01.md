# AUDIT_REPORT_2026-01.md
## G7X 프로젝트 외부 감리 보고서
### 기간: 2025-12-25 ~ 2026-01-16 (약 23일)

---

## 3줄 결론

1. **P1 이슈 4건 중 4건 해결 (100%)**: 거짓합격, KeyError, evidence_writer 구버전 문제 모두 closed
2. **미진 사항 3건**: TASK_TYPE=UNKNOWN, REAL120 API_ERROR, budget_guard.log 누락
3. **핵심 성과**: 통합 루프(오더→실행→검증→일지) 점화 성공, DEVLOG 시스템 실사용 가능 단계 진입

---

## 문제·원인 Top 5

| 순위 | 문제 | 원인 | 영향(숫자) | 증거경로 |
|------|------|------|-----------|----------|
| 1 | 거짓합격(False PASS) | manager.py 예외 발생해도 break 없이 계속 진행 | FAIL=7 | C:\g7core\g7_v1\main\manager.py:229-233 |
| 2 | KeyError 'name' | INTEGRATION_MAP 노드에 필수 필드 없음 + .get() 방어 부재 | FAIL=4 | C:\g7core\g7_v1\tools\devlog_writer.py:311 |
| 3 | devlog.jsonl 미생성 | manager finalize() 직후 devlog append 용접 없음 | devlog_missing=5 | C:\g7core\g7_v1\runs\REAL\DEVLOG\devlog.jsonl |
| 4 | TASK_TYPE=UNKNOWN | 오더 생성기 task_type을 실행/로거가 인식 못함 | UNKNOWN=191 | C:\g7core\g7_v1\runs\REAL\DEVLOG\daily_20260106.md |
| 5 | work_orders Count=0 | PowerShell 파이프라인 시점 차이 또는 경로 불일치 | count_mismatch=4 | C:\g7core\g7_v1\queue\work_orders |

---

## "가라/엉터리 의심" Top 5

| 순위 | 무엇이 가라였나 | 근거 | 어디를 고칠지 | 증거경로 |
|------|----------------|------|--------------|----------|
| 1 | exitcode=0 while receipts=3 | 3개만 처리됐는데 PASS 판정 | evidence_writer PASS 조건 >= → == 변경 | C:\g7core\g7_v1\runs\RUN_*\exitcode.txt |
| 2 | total_api_calls=1 while orders=192 | 192건 처리인데 API 호출 1회 | 로컬 더미 처리 비율 확인/증거 강화 | C:\g7core\g7_v1\runs\REAL\DEVLOG\daily_20260106.md |
| 3 | UNKNOWN=191 분류 | 거의 전체가 미분류 상태로 통과 | task_type 매핑 테이블 동기화 | C:\g7core\g7_v1\queue\work_orders\*.json |
| 4 | stdout 해시 ≠ manifest | 봉인 후 추가 로그 append로 무결성 깨짐 | stdout 핸들 close 후 manifest 생성 | C:\g7core\g7_v1\logs\hash_manifest.json |
| 5 | done_missions 미추적 | 실제 완료 수 카운트 없이 루프 횟수로 PASS | done_missions 필드 추가 + 엄격 비교 | C:\g7core\g7_v1\main\manager.py |

---

## "진행 느림" 원인 Top 5

| 순위 | 병목 | 증거 | 제거 액션ID |
|------|------|------|-------------|
| 1 | 거짓합격 디버깅 시간 | 01/10~01/13 4일간 동일 문제 반복 | ACT-001, ACT-002 |
| 2 | KeyError 반복 발생 | 01/14~01/16 3일간 동일 문제 | ACT-004, ACT-005 |
| 3 | 오더 생성기 경로 혼란 | create_orders_*, work_order_generator_v2, 위저드 혼재 | ACT-007 |
| 4 | Python 별칭 충돌 | Windows 앱 별칭으로 실행 차단 | ACT-009 |
| 5 | API 쿼터/속도 제한 | REAL120 대량 실행 시 API_ERROR 다수 | ACT-011, ACT-012 |

---

## NEXT 10 (동사로 시작)

| ID | Owner | Due | Action |
|----|-------|-----|--------|
| ACT-007 | 형아 | 2026-01-20 | work_orders 경로 및 오더 생성기 출력 위치 확인/통일 |
| ACT-008 | gemini | 2026-01-20 | 오더 생성기 task_type 목록과 실행/로거 인식 목록 동기화 |
| ACT-010 | 형아 | 2026-01-20 | stdout 로거/파일 핸들 완전 close 이후에만 manifest 생성 |
| ACT-011 | gemini | 2026-01-20 | REAL120용 API 재시도/슬로틀 정책 강화 (지수 백오프) |
| ACT-012 | gemini | 2026-01-20 | 대량 실패 시 자동 분할 실행 (120 → 30/30/30/30) |
| ACT-013 | 형아 | 2026-01-20 | budget_guard.log 자동 생성 + 매 번들 종료마다 갱신 |
| NEW-001 | 형아 | 2026-01-25 | REAL_WORK_12_001.txt 기준 실전 12미션 DEVLOG 재검증 |
| NEW-002 | gemini | 2026-01-25 | 3×3×4 실전 묶음 투입 (FILL/VARIATION 계열만) |
| NEW-003 | 형아 | 2026-01-25 | 새로 생성된 INTEGRATION_MAP.json 누적 상태 점검 |
| NEW-004 | claude_code | 2026-01-30 | 야간 자동화 시스템 1.0 버전 구축 |

---

## 치매방지 1줄
거짓합격/KeyError 핵심 문제는 해결됐고, 남은 건 "TASK_TYPE 분류 + API 재시도 정책 + 야간 자동화"다.
