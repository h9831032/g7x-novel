# SSOT Order Bundle Execution Guide v1

## Overview

이 문서는 G7X 프로젝트의 GPTORDER 하청 다발(ORDER 01~12)을 실행하는 방법을 설명합니다.

## Order 목록

### 기본 인프라 (ORDER 01-03)
1. **ORDER 01**: REAL12 SMOKE RUN - 스모크 테스트 스크립트
2. **ORDER 02**: REAL12 SUMMARY - 최신 RUN 요약 도구
3. **ORDER 03**: REAL36 SPEC DOC - REAL36 미션 스펙 문서

### 카탈로그 빌더 (ORDER 04-06)
4. **ORDER 04**: REAL36 CATALOG BUILDER - 36개 실전 미션 카탈로그
5. **ORDER 05**: REAL24 CATALOG BUILDER - 24개 실전 미션 카탈로그
6. **ORDER 06**: REAL CATALOG SANITY - 카탈로그 검증 도구

### 파이프라인 구축 (ORDER 07-10)
7. **ORDER 07**: PIPELINE CATALOG - 주문서 로딩 라이브러리
8. **ORDER 08**: PIPELINE RUNNER - 미션 실행 루프
9. **ORDER 09**: PIPELINE EVIDENCE - 증거팩 작성 라이브러리
10. **ORDER 10**: PIPELINE DEVLOG - DEVLOG 기록 라이브러리

### 운용 도구 (ORDER 11-12)
11. **ORDER 11**: REAL36 DAYNIGHT SWITCH - TEST/REAL 모드 스위치
12. **ORDER 12**: ORDER BUNDLE README - 이 가이드 문서

---

## 추천 실행 순서

### Phase 1: 기본 인프라 구축 (필수)

```powershell
cd C:\g7core\g7_v1
$PY="C:\g7core\g7_v1\.venv\Scripts\python.exe"

# ORDER 01: 스모크 테스트 스크립트 생성
# .\tools\run_real12_smoke_v1.ps1 생성

# ORDER 02: RUN 요약 도구 생성
# .\tools\summarize_latest_run_v1.py 생성

# ORDER 03: REAL36 스펙 문서 생성
# .\DOCS\REAL36_MISSION_SPEC_V1.md 생성
Get-Item .\DOCS\REAL36_MISSION_SPEC_V1.md
```

**증거 수집:**
- 파일 생성 확인: `dir .\tools\run_real12_smoke_v1.ps1`
- 파일 생성 확인: `dir .\tools\summarize_latest_run_v1.py`
- 문서 확인: `Get-Item .\DOCS\REAL36_MISSION_SPEC_V1.md`

---

### Phase 2: 카탈로그 빌더 (필수)

```powershell
# ORDER 04: REAL36 카탈로그 생성
& $PY .\tools\build_real36_real_catalog_v1.py

# ORDER 05: REAL24 카탈로그 생성
& $PY .\tools\build_real24_real_catalog_v1.py

# ORDER 06: 카탈로그 검증
& $PY .\tools\check_real_catalogs_v1.py
```

**증거 수집:**
- `.\GPTORDER\REAL36_REAL_A.txt` (36줄)
- `.\GPTORDER\REAL24_REAL_A.txt` (24줄)
- 검증 출력: 모든 카탈로그 PASS 확인

---

### Phase 3: 파이프라인 구축 (선택적)

```powershell
# ORDER 07-10은 라이브러리 함수 추가
# manager.py에 자동 통합됨

# 검증: manager.py 실행 테스트
& $PY .\main\manager.py -h
```

**증거 수집:**
- `.\main\pipeline\catalog.py` (load_orders 함수)
- `.\main\pipeline\runner.py` (run_orders 함수)
- `.\main\pipeline\evidence.py` (finalize_evidence_pack 함수)
- `.\main\pipeline\devlog.py` (append_run_summary 함수)
- `.\DEVLOG\INTEGRATION_MAP.md`

---

### Phase 4: 운용 도구 (권장)

```powershell
# ORDER 11: TEST 모드로 REAL36 실행
.\tools\run_real36_3p3x6_day_night.ps1 -Mode TEST

# ORDER 12: 이 가이드 문서
Get-Item .\DOCS\SSOT_ORDER_BUNDLE_GUIDE_V1.md
```

**증거 수집:**
- TEST 모드: 12개 RUN 폴더 (DAY 6 + NIGHT 6)
- 각 RUN: `verify_report.json`, `budget_guard.log`

---

## 실전 실행 (REAL 모드)

### 사전 준비
1. Phase 1~2 완료 확인
2. `REAL36_REAL_A.txt` 존재 확인
3. `TEST_REAL36_VERIFY.txt` 존재 확인

### 실행

```powershell
# REAL 모드: 실전 36개 미션
.\tools\run_real36_3p3x6_day_night.ps1 -Mode REAL
```

### 예상 실행 시간
- **DAY 프로파일**: 약 8.3분 (6 슬라이스 × 83초)
- **NIGHT 프로파일**: 약 24분 (6 슬라이스 × 240초)
- **전체**: 약 32.3분

### 증거 수집
- **RUN 폴더**: 12개 (DAY 6 + NIGHT 6)
- **총 미션**: 72개 (36 DAY + 36 NIGHT)
- **증거팩**: 각 RUN 폴더 내
  - `verify_report.json`
  - `budget_guard.log`
  - `stamp_manifest.json`
  - `final_audit.json`
  - `blackbox_log.jsonl`
  - `api_receipt.jsonl`

---

## 증거팩 검증 스크립트

```powershell
# 최신 RUN 요약
& $PY .\tools\summarize_latest_run_v1.py

# 카탈로그 검증
& $PY .\tools\check_real_catalogs_v1.py

# DEVLOG 확인
Get-Content .\DEVLOG\devlog_runs.jsonl | Select-Object -Last 12
```

---

## 트러블슈팅

### 429 에러 발생 시
1. NIGHT 프로파일로 전환 (더 긴 딜레이)
2. REAL36 → REAL24로 다운시프트
3. 배치 크기 축소 (manager.py의 BATCH_SIZE)

### 파일 없음 에러
1. Phase 1~2 완료 확인
2. GPTORDER 폴더 확인: `dir .\GPTORDER\REAL*.txt`
3. 슬라이스 재생성: `& $PY .\tools\build_real36_slices_v1.py`

### 증거팩 미생성
1. `verify_report.json` 확인
2. `exitcode.txt` 확인
3. `stdout_manager.txt` 로그 확인

---

## 참고 문서
- `REAL36_MISSION_SPEC_V1.md` - REAL36 운용 규칙
- `INTEGRATION_MAP.md` - 파이프라인 구조
- `CLAUDE.md` - 프로젝트 전역 규칙

---

## 버전
- v1.0 - 2026-01-17: 초기 ORDER 번들 가이드 작성
