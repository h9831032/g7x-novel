# G7X MERGED DEVLOG - PART 1
## 기간: 2025-12-25 ~ 2025-12-29
## 프로젝트: G6X → G7X 전환기

---

## DATE: 2025-12-25 (이전 누적)

### WHAT_CHANGED
- G6X 프로젝트 12대 검문 로직 완성
- 테슬라 자가발전 엔진 안정화
- `engine/world_rule_gate_v1.py` 스키마 봉인 (verdict/violations/meta)
- `engine/lawbook_v3.py` HARD/STRONG/SOFT 3계층 분류 확정

### COMMANDS
```powershell
# 봉인 스냅샷
python seal_snapshot_v0.py PHASE2_FINAL
```

### RESULTS
- Sync_ID: `20251227_V12_1_FINAL_UNIFIED`
- 12대 검문 항목(시공간~문체 이탈) 로직 실장 완료
- Anti-Mock 헌법 확립: 실전 엔진 경로에서 하드코딩/시뮬레이션 금지

### ISSUES
- 없음 (Phase 1 봉인 완료)

### DECISIONS
- **봉인**: Phase 1 서사 무결성 및 배선 공정 완료
- **금지**: SQL/DB/ORM 사용 전면 금지
- **원칙**: "추론 대신 검증(Validation over Inference)"

### NEXT
- Phase 2: 실전 Writer API 연동

---

## DATE: 2025-12-27

### WHAT_CHANGED
- `engine/gate_judge_v12.py` Gate 판사 로직
- `engine/claim_extractor_v12.py` 수사관 로직
- `engine/writer_adapter_v12.py` 통로 로직
- `tests/redteam_harness_v12.py` 하네스
- 아이템(ASSET) 배선 적용 후 TP 급상승 확인

### COMMANDS
```powershell
python tests\redteam_harness_v12.py --novel "순례자" --turns 90 --seed 42 --writer_mode STUB --run_id PILGRIM_COMPOSITE_STUB_90_ASSET
```

### RESULTS
- `[DONE] tp=70 fp=0 fn=20`
- `FN_TOP3_BUCKET [('STATE', 20)]`
- Phase1 Gate(Composite) 봉인 진입

### ISSUES
1. STUB 주행에서 FN이 전부 UNKNOWN으로 나오는 런 존재
   - 원인: 케이스북에 poison_bucket/poison_id 기록 누락
2. REAL Writer가 30턴에서 HTTPError로 멈춤
   - 원인: 네트워크/키/쿼터 이슈
3. 프로필 dataclass frozen 때문에 필드 수정 시 크래시

### DECISIONS
- **봉인**: Phase1에서 확실히 먹히는 3개만 유지 (SPACE/TIME, STATE, ASSET)
- **금지**: Navigator/FunEngine/자가발전 전체 연결 금지 (디버그 지옥)
- **우선순위**: VMCL "도시락(Priority Recall) + 영수증 박제" 먼저

### NEXT
- VMCL Priority Recall 구현
- SPACE/TIME FN Top-3 수술

---

## DATE: 2025-12-28 (Part 1)

### WHAT_CHANGED
- `engine/explainability_v0.py` 판정 근거 생성기
- `engine/ledger_explain_v0.py` 영구 장부 기록기
- `tools/audit_report_v1.py` 오프라인 통계 분석기
- `tools/seal_snapshot_v0.py` 공정 봉인 도구

### COMMANDS
```powershell
python tools/audit_report_v1.py RUN_1766864027
python seal_snapshot_v0.py PHASE2_FINAL
```

### RESULTS
- PHASE2_FINAL 스냅샷 봉인 완료
- 6개 핵심 파일 해시 고정
- 하네스 200턴 3회 동일 해시 PASS

### ISSUES
- 없음 (정상 봉인)

### DECISIONS
- **봉인**: Phase 2.5 Audit Tooling 완성
- **금지**: SQL/DB 영구 금지, 실시간 판단 루프에 통계/검색 삽입 금지

### NEXT
- Phase 3 Navigator Core 설계

---

## DATE: 2025-12-28 (Part 2) - 만차 주행 도입

### WHAT_CHANGED
- 줄자(MeterTick/MeterGuard) 시스템 도입
- 만차(12+12) 주행 구조 확립
- `tools/run_bundle_v4.py` 번들 러너

### COMMANDS
```powershell
python tools/run_bundle_v4.py
```

### RESULTS
- `Subpack A done_files: 12`
- `Subpack B done_files: 12`
- `Total Tasks: 24 | Subpacks: 2 | REALCALL Used: 2`
- meter_tick에 `workitem_count: 12`, `meter_status: OK`, `evidence_status: VERIFIED` 확인

### ISSUES
1. PowerShell findstr 따옴표 처리 문제
2. Guard 케이스에서 NEG_02 오탐 (부정문장 과잉탐지)

### DECISIONS
- **원칙**: WorkItem 1개 = 커밋 1개 = 실패 원인 추적 가능한 크기
- **상한**: 2동작까지만 허용 (3~4동작 금지)
- **금지**: "12개 말로 무한 작업" 방식 금지

### NEXT
- Guard 케이스 PHASE2 봉인
- MeterGuard v0.1.1 법공장 투입

---

## DATE: 2025-12-29

### WHAT_CHANGED
- `google.generativeai` → `google.genai` SDK 전면 교체
- `gemini-pro` → `gemini-2.0-flash` 모델 전환
- 배치 수식 기반 무한 확장성 확보: `WID = (batch_idx - 1) * WIP + local_idx`

### COMMANDS
```powershell
python tools/run_b240_stress.py
python tools/dod_b240_stress.py
```

### RESULTS
- B240 (12 x 20 Batches) 스트레스 테스트 PERFECT PASS
- WID 1~240 완전 연속, 누락/중복/역전 0
- 정규 운영값 **B360 (12 × 30)** 채택

### ISSUES
- 기술적 문제 없음
- 운영 피로/비용 우려로 600+ 확장 보류

### DECISIONS
- **봉인**: B240 구조 합격
- **고정**: B360 정규 운영값
- **금지**: 600+ 무리한 확장 (현 단계)

### NEXT
- B360 고정 세팅 반영
- 실소설 투입 (REAL RUN)

---

## 치매방지 1줄
이 기간은 "G6X 12대 검문 로직 완성 → SDK 이주 → 배치 확장 검증(B240)"까지 인프라 기반을 다진 시기다.
