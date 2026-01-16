# A2 - devlog_writer에서 Evidence 결과 읽어오기

## 구현 위치
C:\g7core\g7_v1\tools\devlog_writer.py

## 핵심 함수
```python
def load_verify_report(run_path: Path) -> Dict[str, Any]
```

## 기능
1. verify_report.json 읽기
2. 핵심 필드 추출:
   - exitcode
   - expected_missions
   - done_missions  
   - api_error_count
   - pass (bool)
   - reason_code

3. Verdict 자동 계산:
   - pass == True → verdict = "PASS"
   - pass == False → verdict = "FAIL"

## 실패 처리
- 파일 없음 → verdict = "UNKNOWN"
- 파싱 실패 → verdict = "UNKNOWN"
- 에러 발생해도 DEVLOG 생성은 계속 진행

## 사용 예시
```python
evidence = load_verify_report(Path("C:/g7core/g7_v1/runs/RUN_20260115_123456_789"))
print(evidence["verdict"])  # "PASS" or "FAIL" or "UNKNOWN"
print(evidence["exitcode"])  # 0 or 1
print(evidence["pass"])      # True or False
```
