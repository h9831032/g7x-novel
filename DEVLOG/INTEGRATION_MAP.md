# G7X Integration Map

## Pipeline 구조

```
main/
├── manager.py (메인 엔트리, RUN 생성 및 관리)
├── pipeline/
│   ├── catalog.py (주문서 로딩 및 카탈로그 컴파일)
│   ├── runner.py (미션 실행 루프, 재시도 로직)
│   ├── evidence.py (증거팩 작성: verify_report, hash_manifest, audit_receipt)
│   └── devlog.py (DEVLOG 기록, run_id 요약)
```

## 주요 함수

### catalog.py
- `load_orders(order_path) -> List[str]`: 주문서 파일 로딩
- `CatalogCompiler.compile_prompt(order_line)`: 주문 라인을 프롬프트로 컴파일

### runner.py
- `run_missions(orders, compiler, engine, ...)`: 미션 순차 실행 + 실패 격리
- `run_orders(mission_orders)`: 간단한 래퍼 (베이직엔진 용접 준비)

### evidence.py
- `EvidenceWriter.finalize(exitcode, stats)`: 증거팩 일괄 생성
- `finalize_evidence_pack(...)`: 한 함수 호출로 증거팩 작성

### devlog.py
- `write_daily_devlog(run_path, stats, reason_code)`: 사람이 읽을 수 있는 일일 로그
- `append_run_summary(run_id, exitcode, pass_status, ssot_root)`: DEVLOG/devlog_runs.jsonl에 요약 추가
- `call_devlog_generator(run_path, ssot_root)`: tools/generate_devlog.py 호출

## 증거팩 파일

```
runs/RUN_YYYYMMDD_HHMMSS_xxxxxx/
├── verify_report.json (exitcode, pass/fail, 미션 수)
├── budget_guard.log (API 호출 수, 비용 추정)
├── stamp_manifest.json (해시, 타임스탬프)
├── final_audit.json (최종 감사 리포트)
├── blackbox_log.jsonl (이벤트 로그)
├── api_receipt.jsonl (API 호출 기록)
├── daily_devlog.txt (사람이 읽을 수 있는 요약)
├── stdout_manager.txt (표준 출력)
├── stderr_manager.txt (표준 에러)
├── receipts/mission/ (미션별 영수증)
│   ├── mission_0001.json
│   ├── mission_0002.json
│   └── ...
└── missions/ (호환성 유지용)
    ├── mission_0001.json
    └── ...
```

## DEVLOG 구조

```
DEVLOG/
├── devlog_runs.jsonl (모든 RUN 요약)
├── INTEGRATION_MAP.md (이 파일)
└── [날짜별 로그 추가 가능]
```

## 실행 흐름

1. **manager.py**: RUN 폴더 생성, 주문서 로딩
2. **catalog.py**: 주문서 → 미션 리스트 변환
3. **runner.py**: 미션 순차 실행, API 호출, 재시도
4. **evidence.py**: 증거팩 파일 작성
5. **devlog.py**: DEVLOG 기록, run_id 요약 추가

## 환경변수

- `G7_RUN_PROFILE`: DAY | NIGHT (프로파일 선택)
- `G7X_CATALOG_PATH`: 카탈로그 파일 경로 (선택적)

## 버전

- v1.0 - 2026-01-17: 초기 파이프라인 구조 확립
