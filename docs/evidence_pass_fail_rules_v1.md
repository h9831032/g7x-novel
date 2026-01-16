# Evidence PASS/FAIL 판정 규칙 v1

## 절대 규칙 (헌법급)

### PASS 조건 (모두 만족해야 함)
```
pass = (
    exitcode == 0
    AND done_missions == expected_missions
    AND api_error_count == 0
)
```

### FAIL 조건 (하나라도 해당되면)
```
fail = (
    exitcode != 0
    OR done_missions != expected_missions
    OR api_error_count > 0
)
```

## 케이스별 예시 (6개 필수 케이스)

### 케이스 1: 완전 성공
- exitcode: 0
- expected_missions: 120
- done_missions: 120
- api_error_count: 0
- **판정: PASS**
- reason_code: ORDER_EOF

### 케이스 2: 미션 부족 (거짓 PASS 차단)
- exitcode: 0
- expected_missions: 120
- done_missions: 119
- api_error_count: 0
- **판정: FAIL**
- reason_code: MISSION_MISMATCH

### 케이스 3: API 에러 발생
- exitcode: 0
- expected_missions: 120
- done_missions: 120
- api_error_count: 3
- **판정: FAIL**
- reason_code: API_ERROR

### 케이스 4: 명시적 실패
- exitcode: 1
- expected_missions: 120
- done_missions: 50
- api_error_count: 10
- **판정: FAIL**
- reason_code: EXECUTION_ERROR

### 케이스 5: Ctrl+C 인터럽트
- exitcode: 1
- expected_missions: 120
- done_missions: 35
- api_error_count: 0
- **판정: FAIL**
- reason_code: INTERRUPTED

### 케이스 6: 완전 실패 (0개 성공)
- exitcode: 1
- expected_missions: 120
- done_missions: 0
- api_error_count: 120
- **판정: FAIL**
- reason_code: TOTAL_FAILURE

## 엄격성 원칙

### 느슨한 비교 금지
```python
# ❌ 금지
if done_missions >= expected_missions:
    pass = True

# ❌ 금지
if api_error_count < 5:
    pass = True
```

### 엄격한 비교만 허용
```python
# ✅ 허용
if done_missions == expected_missions:
    pass_mission = True

# ✅ 허용
if api_error_count == 0:
    pass_api = True
```

## verify_report.json 필수 필드

```json
{
  "timestamp": "ISO8601 timestamp",
  "run_id": "RUN_YYYYMMDD_HHMMSS_NNNNNN",
  "exitcode": 0,
  "expected_missions": 120,
  "done_missions": 120,
  "api_error_count": 0,
  "pass": true,
  "reason_code": "ORDER_EOF"
}
```

## reason_code 정의

- **ORDER_EOF**: 정상 완료
- **MISSION_MISMATCH**: done != expected
- **API_ERROR**: api_error_count > 0
- **EXECUTION_ERROR**: 실행 중 예외
- **INTERRUPTED**: Ctrl+C 등 수동 중단
- **TOTAL_FAILURE**: 모든 미션 실패

## 위험 시나리오

### 거짓 PASS (False Positive)
```
done=119, expected=120, api_error=0
→ 느슨한 규칙: PASS (위험!)
→ 엄격한 규칙: FAIL (안전)
```

**위험도:** 🔴 CRITICAL
**결과:** 불완전한 데이터가 PASS로 통과

### 거짓 FAIL (False Negative)
```
done=120, expected=120, api_error=0, exitcode=0
→ 모든 조건 만족인데 FAIL 판정
```

**위험도:** 🟡 MEDIUM
**결과:** 재작업 비용 증가 (안전 방향)

## 동기화 규칙

### exitcode ↔ pass 동기화
```python
if pass:
    exitcode = 0
else:
    exitcode = 1
```

### DEVLOG Verdict ↔ pass 동기화
```python
verdict = "PASS" if pass else "FAIL"
```

### 3중 일치 보장
```
exitcode == 0 ⟺ pass == True ⟺ Verdict == "PASS"
```
