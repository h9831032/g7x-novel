# G7X RUNBOOK - Night Shift Operations v1

## Overview

야간 운용 가이드: 무인 실행을 위한 실전 미션 수행 절차

## 실행 순서

### 1. 사전 준비 (Pre-flight)

```powershell
cd C:\g7core\g7_v1

# 1.1 GPTORDER 중복 검사
& python .\tools\dedupe_order_guard_v1.py

# 1.2 카탈로그 검증
& python .\tools\check_real_catalogs_v1.py
```

**성공 기준:**
- PASS 메시지 출력
- exitcode = 0

**실패 시:**
- 즉시 중단
- 오류 로그 확인 후 재발주

---

### 2. 실전 미션 실행

```powershell
# REAL30 야간 러너 (DAY + NIGHT)
.\tools\run_real30_3p3x5_day_night.ps1
```

**예상 실행 시간:**
- DAY 프로파일: 약 15분 (5 슬라이스 × 3분)
- NIGHT 프로파일: 약 45분 (5 슬라이스 × 9분)
- **전체**: 약 60분

**성공 기준:**
- 10개 RUN_PATH 출력 (DAY 5 + NIGHT 5)
- 각 RUN: exitcode = 0
- 증거팩 완전 생성

---

### 3. 증거팩 검증

```powershell
# 최신 RUN 증거팩 검사
& python .\tools\check_run_artifacts_v1.py
```

**필수 파일:**
- verify_report.json
- stamp_manifest.json
- exitcode.txt
- stdout_manager.txt
- stderr_manager.txt
- final_audit.json

**성공 기준:**
- PASS 메시지
- 모든 필수 파일 존재

---

### 4. 실패 처리

```powershell
# FAIL_BOX 확인
Get-ChildItem C:\g7core\g7_v1\FAIL_BOX

# FAIL_INDEX 조회
Get-Content C:\g7core\g7_v1\FAIL_BOX\FAIL_INDEX.jsonl | Select-Object -Last 5
```

**실패 시 대응:**
1. FAIL_BOX에 자동 패킹된 RUN 폴더 확인
2. stderr_manager.txt에서 원인 파악
3. 429 에러: NIGHT 프로파일로 재시도
4. API 에러: 다음 날 재발주

---

### 5. 일일 보고서 생성

```powershell
# 자동 리포트 생성
& python .\tools\build_daily_report_v1.py

# 리포트 확인
Get-Content .\DEVLOG\DAILY_REPORT_$(Get-Date -Format "yyyy-MM-dd").txt
```

---

### 6. 상태 아카이브

```powershell
# 상태 스냅샷 생성
.\tools\state_archive_pack_v1.ps1
```

---

## 다음날 재발주 규칙

### Case 1: 전체 성공
- 다음 미션 세트로 진행 (REAL36, REAL48 등)

### Case 2: 일부 실패
- FAIL_BOX에서 실패 RUN 확인
- 실패한 슬라이스만 재실행

### Case 3: 429 Rate Limit
- NIGHT 프로파일로 재시도
- 배치 크기 축소 (3 → 2)
- 딜레이 증가 (75s → 120s)

### Case 4: API 장애
- 24시간 대기 후 재시도
- 실패 RUN 수 기록

---

## 모니터링 포인트

### 1. RUN 폴더 수
```powershell
(Get-ChildItem C:\g7core\g7_v1\runs -Directory).Count
```

**정상 범위:** 하루 10~15개 RUN

### 2. DEVLOG 증가
```powershell
Get-Content .\DEVLOG\devlog_runs.jsonl | Measure-Object -Line
```

**정상 범위:** 매일 +10 라인

### 3. FAIL_BOX 크기
```powershell
(Get-ChildItem C:\g7core\g7_v1\FAIL_BOX -Recurse).Count
```

**정상 범위:** 0~2개 실패

---

## 긴급 연락처

- FAIL 알림: FAIL_BOX/FAIL_INDEX.jsonl 확인
- API 키 만료: GEMINI_API_KEY 갱신
- 디스크 부족: runs/ 폴더 정리

---

## 버전

- v1.0 - 2026-01-17: 초기 야간 운용 가이드 작성
