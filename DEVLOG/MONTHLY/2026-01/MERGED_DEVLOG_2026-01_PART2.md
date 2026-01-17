# G7X MERGED DEVLOG - PART 2
## 기간: 2026-01-01 ~ 2026-01-07
## 프로젝트: G7X 통합 공정 구축기

---

## DATE: 2026-01-01 ~ 2026-01-02

### WHAT_CHANGED
- GPT 이사 패키지 템플릿 확정 (STATE/SOUL/LOCK/TODAY_INTENT/NEXT_FAIL_FAST)
- 문체/품질 문제 6종 고정 패턴 확정
- RowContext 개념 도입 (ROW별 완전 독립 처리)

### COMMANDS
- 이사 패키지 복붙 테스트

### RESULTS
- 이사 패키지가 세션 간 맥락 유지에 효과적임 확인
- 6종 문체 문제 정의 완료: 석화, 드리프트, 슬리피·리프트, 선악 붕괴, 캐릭터 음성 붕괴, 의미 공허 드리프트

### ISSUES
1. "기억 문제"가 아니라 "정의 부재 문제"였음
2. 필터·단어치환·예외처리 → 전부 땜방으로 판명
3. 주입(injection)이 문장 생성 역할을 침범 → 해괴체 발생

### DECISIONS
- **원칙**: 문체 최종 책임자 = Writer 단일화
- **금지**: 인덱싱/주입/설계층의 문장 생성
- **규칙**: 품질은 "보고서"가 아니라 FAIL_FAST 조건

### NEXT
- 라이트엔진 + 문체 안정화
- VMCL 통합 검증

---

## DATE: 2026-01-03

### WHAT_CHANGED
- 500권 전수조사 및 8대 레이더 매트릭스 구축
- `tools/survey/metric_pack_buffer2_v1.py` 8대 품질 지표 (6→8 확장)
- `tools/survey/run_quality_survey_v1.py` 5구간 정밀 샘플링

### COMMANDS
```powershell
python tools/run_quality_survey_v1.ps1
```

### RESULTS
- `quality_matrix.csv` (500 Novels x 8 Metrics) 생성
- `exec_guard.json` → `status: SAFE`
- G6 레거시 환경 간섭 없음 확인

### ISSUES
- 없음 (파서 오류 수정 후 정상 완수)

### DECISIONS
- **완료**: 500권 전수조사 기반 품질 레이더 데이터화
- **확정**: 5구간 정밀 샘플링 알고리즘

### NEXT
- quality_matrix.csv 기반 후반부 캐릭터 음성 붕괴 비중 분석

---

## DATE: 2026-01-04 ~ 2026-01-05

### WHAT_CHANGED
- Layer-1 도서관 통합판 (전수스캔+딱지+증거봉인)
- 8종 증거(영수증) 세트 구조 확립
- 3+3 분할 실행 구조 도입

### COMMANDS
```powershell
python g7_fast_tagger.py
dir C:\g7core\g7_v1\queue\work_orders -Recurse -Filter *.json | measure
```

### RESULTS
- `C:\g7core\g7_v1\index_v1_fast.db` 고속 인덱스 DB 생성
- `verify_report.json`: pass=true, strike_count=2509, chunk_count=4,816,747
- `api_receipt.jsonl`, `state_pack.json` 트럭별 생성 확인

### ISSUES
1. **stdout 해시 불일치 (WARN)**
   - 원인: manifest 생성 후 stdout.txt에 추가 로그가 append됨
   - REF: (2026-01-04, HASH_MISMATCH_STDOUT)
2. **BudgetGuard 로그 누락**
   - 원인: 영수증은 있는데 가계부(집계 로그)가 빠진 상태

### DECISIONS
- **봉인**: Layer-1 도서관 통합 구조 방향 확정
- **금지**: stdout 같은 "계속 커질 수 있는 파일"을 봉인 대상으로 두는 방식
- **필수**: 6×20 유지 + 내부 3+3 자동분할

### NEXT
- 봉인(해시) 불변성 보강 패치
- TOKEN_OPTIMIZER + AUTO_HEAL_V2 용접

---

## DATE: 2026-01-06

### WHAT_CHANGED
- 원키 위저드 루프 점화 (factory_reset → order_gen → main_run → verifier → devlog_summary)
- `main.py` 통합 엔트리 확립
- `devlog_manager.py` 정산기 연결

### COMMANDS
```powershell
python C:\g7core\g7_v1\main.py
python C:\g7core\g7_v1\tools\devlog_manager.py
```

### RESULTS
- `daily_20260106.md` 생성
- 용접 3개 요약: Workers Max=3 / Anti-Empty Audit / SHA1 Manifest

### ISSUES
1. **오더 카운트 0 문제**
   - 원인: PowerShell 파이프라인 처리 시점 차이 또는 경로 불일치
2. **TASK_TYPE=UNKNOWN 191건**
   - 원인: 오더 생성기의 task_type 목록을 실행/로거가 인식 못함
3. **API 호출 수 1회로 매우 적음**
   - 원인: 로컬 루프/더미성 처리 비율 높음

### DECISIONS
- **문제인정**: 시스템이 아직 "반자동 작업장" 상태
- **필수수리**: 오더 생성기/카운터/분류로직 봉인 수리

### NEXT
- 오더 생성 → main 실행 → devlog 갱신 루프 안정화

---

## DATE: 2026-01-07

### WHAT_CHANGED
- Python 실행 별칭 충돌 해결 (`& python.exe` 사용)
- 메인 엔진 부팅 성공 확인
- devlog.jsonl 실시간 적재 확인

### COMMANDS
```powershell
& python.exe -u C:\g7core\g7_v1\main.py 2>&1 | Tee-Object -FilePath C:\g7core\g7_v1\runs\_main_stdout_stderr.txt
Get-Content C:\g7core\g7_v1\runs\REAL\DEVLOG\devlog.jsonl -Tail 5
```

### RESULTS
- `--- [ENGINE] 2026-01-07 BOOT SUCCESS ---`
- `[ENGINE] FOUND: 10 orders.`
- `[ENGINE] FINISHED. PROCESSED: 10`
- devlog.jsonl에 `2026-01-07T00:58:14` 타임스탬프 적재

### ISSUES
1. 오더가 10개(DEVLOG_TEST)만 처리됨 → 240/600급 무인생산 미달
2. 실행 방식 표준화 필요 (별칭 충돌 우회)

### DECISIONS
- **PASS**: 메인 부팅 및 10개 오더 처리 + 로그 기록 성공
- **WARN**: 공장 풀가동(대량 오더/무인 스케줄) 단계 미진입

### NEXT
- work_orders 최소 240개 이상 생성
- main 실행 후 PROCESSED 96 이상 확인

---

## 치매방지 1줄
이 기간은 "통합 루프(오더→실행→검증→일지) 점화 성공"까지 도달했으나, "무인 공장"은 아직 아닌 상태로 마무리됐다.
