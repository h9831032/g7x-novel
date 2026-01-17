# REAL36 Mission Specification v1

## Overview

REAL36은 G7X 프로젝트의 실전 미션 배치 단위로, **36개 미션을 (3+3)×6 슬라이스 구조로 실행**하는 표준 운용 방식입니다.

## UNIT_RULE: (3+3)×N

### 기본 원칙
- **슬라이스 크기**: 6개 미션 (3+3)
- **REAL36**: (3+3)×6 = 36개 미션
- **REAL24**: (3+3)×4 = 24개 미션 (다운시프트용)

### 슬라이스 분할 이유
1. **429 방지**: API rate limit 회피를 위해 작은 단위로 분산
2. **증거팩 수집**: 각 슬라이스마다 독립적인 RUN 폴더 생성
3. **실패 격리**: 특정 슬라이스 실패 시 영향 범위 최소화
4. **복구 용이**: 실패한 슬라이스만 재실행 가능

## DAY/NIGHT 프로파일

### DAY Profile (주간 운용)
```
MAX_RETRIES: 5
BASE_DELAY: 2.0s
BATCH_SIZE: 3
BATCH_DELAY: 20.0s
TASK_DELAY_PER_MISSION: 8.0s
JITTER_MAX: 1.0s
```

**백오프 패턴**: 2s → 4s → 8s → 16s → 32s (+ jitter 0~1s)

### NIGHT Profile (야간 운용)
```
MAX_RETRIES: 6
BASE_DELAY: 5.0s
BATCH_SIZE: 3
BATCH_DELAY: 75.0s
TASK_DELAY_PER_MISSION: 25.0s
JITTER_MAX: 2.0s
```

**백오프 패턴**: 5s → 10s → 20s → 40s → 80s → 160s (+ jitter 0~2s)

## 파일 구조

### 슬라이스 오더 파일
```
GPTORDER/
├── REAL36_DAY_S1.txt    (미션 1-6)
├── REAL36_DAY_S2.txt    (미션 7-12)
├── REAL36_DAY_S3.txt    (미션 13-18)
├── REAL36_DAY_S4.txt    (미션 19-24)
├── REAL36_DAY_S5.txt    (미션 25-30)
├── REAL36_DAY_S6.txt    (미션 31-36)
├── REAL36_NIGHT_S1.txt  (미션 1-6)
├── REAL36_NIGHT_S2.txt  (미션 7-12)
├── REAL36_NIGHT_S3.txt  (미션 13-18)
├── REAL36_NIGHT_S4.txt  (미션 19-24)
├── REAL36_NIGHT_S5.txt  (미션 25-30)
└── REAL36_NIGHT_S6.txt  (미션 31-36)
```

### RUN 증거팩 (각 슬라이스마다 생성)
```
runs/RUN_YYYYMMDD_HHMMSS_xxxxxx/
├── verify_report.json
├── budget_guard.log
├── stdout_manager.txt
├── stderr_manager.txt
├── missions/
│   ├── mission_0001.json
│   ├── mission_0002.json
│   └── ...
└── api_raw/
    ├── mission_0001.json
    └── ...
```

## 실행 시퀀스

### 1단계: 슬라이스 생성
```powershell
cd C:\g7core\g7_v1
$PY="C:\g7core\g7_v1\.venv\Scripts\python.exe"
& $PY .\tools\build_real36_slices_v1.py
```

### 2단계: DAY+NIGHT 실행
```powershell
powershell -ExecutionPolicy Bypass -File .\tools\run_real36_3p3x6_day_night.ps1
```

### 3단계: 증거팩 검증
- 12개 RUN 폴더 생성 확인 (DAY 6 + NIGHT 6)
- 각 RUN 폴더 내 verify_report.json 확인
- devlog_runs.jsonl에 12개 entry 추가 확인

## PASS 조건

### 슬라이스 단위 (각 6개 미션)
```
✓ exitcode = 0
✓ done_missions = 6
✓ api_error_count = 0
```

### 전체 실행 단위 (12개 슬라이스)
```
✓ DAY: 6/6 슬라이스 PASS
✓ NIGHT: 6/6 슬라이스 PASS
✓ 총 72개 미션 성공 (36 DAY + 36 NIGHT)
```

## 다운시프트 규칙

### REAL36 → REAL24 전환 조건
- REAL36 실행 중 2개 이상 슬라이스 실패
- 연속 429 에러 발생
- 야간 시간대 과부하 경고

### REAL24 구조
```
(3+3)×4 = 24개 미션
슬라이스: S1~S4 (각 6개 미션)
```

## 예상 실행 시간

### DAY 프로파일
- 슬라이스당: 약 83초
- 전체 6슬라이스: 약 8.3분

### NIGHT 프로파일
- 슬라이스당: 약 240초
- 전체 6슬라이스: 약 24분

### 전체 REAL36 (DAY+NIGHT)
- 총합: 약 32.3분

## 주요 도구

### build_real36_slices_v1.py
- 소스: TEST_REAL36_VERIFY.txt
- 출력: 12개 슬라이스 파일
- 검증: 36라인 확인, FAIL_FAST

### run_real36_3p3x6_day_night.ps1
- DAY: S1~S6 순차 실행
- NIGHT: S1~S6 순차 실행
- 실패 시 즉시 중단
- Read-Host로 창 강제 종료 방지

## 참고 문서
- G7X_CLAUDE_GLOBAL_GUIDELINE_V3
- SSOT_PROFILE_G7X_V3
- G7X_GITHUB_CLAUDECODE_ADDENDUM_V1
