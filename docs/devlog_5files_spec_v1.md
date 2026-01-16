# DEVLOG 5파일 스펙 v1

## 목적
실행 종료 시 자동 생성되는 5개 파일로 프로젝트 상태를 완전히 파악

## 파일 구조

```
DEVLOG/
├─ 2026-01-15/
│   └─ DAILY_REPORT_2026-01-15.txt
├─ EVIDENCE_LATEST.json
├─ DELTA_TODAY.json
├─ NEXT_TOMORROW.json
└─ INTEGRATION_MAP.json
```

---

## 1. DAILY_REPORT_YYYY-MM-DD.txt

### 목적
사람이 읽는 일일 요약 보고서

### 포함 내용
- 날짜
- 오늘 실행한 RUN 목록
- 최신 RUN 증거 요약 (exitcode, verdict, done/expected)
- 오늘 수정된 파일 목록 (Delta)
- 현재 통합 상태 스냅샷
- 내일 할 일

### 샘플
```
G7X DAILY REPORT - 2026-01-15

=== EVIDENCE (Latest RUN) ===
RUN ID: RUN_20260115_211256_937205
Exitcode: 0
Expected: 120
Done: 120
Verdict: PASS
Stderr Exists: False

Representative Errors (last 3 lines):
  (none)

=== DELTA (Today's Changes) ===
Total Files Modified: 5
  - main/manager.py
  - engine/evidence_writer.py
  - tools/devlog_writer.py
  - DEVLOG/EVIDENCE_LATEST.json
  - DEVLOG/INTEGRATION_MAP.json

=== INTEGRATION MAP (Snapshot) ===
Total Progress: 0.73 (73%)
  [WELDED] manager -> manager.py (100%)
  [WIRED] evidence_writer -> engine/evidence_writer.py (100%)
  [WIRED] devlog_writer -> tools/devlog_writer.py (100%)
  [PLANNED] navigator -> main/navigator.py (0%)

=== NEXT (Tomorrow) ===
Main Tasks (Day):
  1. Verify DEVLOG auto-generation stability
  2. Review evidence layer completeness
  3. Test REAL_WORK_120 batch

Night Tasks:
  1. Execute REAL_WORK_120 batch with Gemini 2.0 Flash
  2. Monitor FAIL_BOX isolation
  3. Validate retry order generation
```

---

## 2. EVIDENCE_LATEST.json

### 목적
최신 RUN의 핵심 숫자만 기록 (머신 판독용)

### 필드
```json
{
  "run_id": "RUN_YYYYMMDD_HHMMSS_NNNNNN",
  "timestamp": "ISO8601",
  "exitcode": 0,
  "expected": 120,
  "done": 120,
  "verdict": "PASS",
  "api_error_count": 0,
  "reason_code": "ORDER_EOF",
  "stderr_exists": false,
  "errors": []
}
```

### 갱신 규칙
- 실행할 때마다 덮어쓰기
- 항상 최신 RUN만 반영

---

## 3. DELTA_TODAY.json

### 목적
오늘 수정/생성된 파일만 기록

### 필드
```json
{
  "timestamp": "ISO8601",
  "date": "YYYY-MM-DD",
  "count": 5,
  "files": [
    {
      "path": "main/manager.py",
      "change_type": "MODIFIED",
      "size": 15234
    },
    {
      "path": "tools/new_tool.py",
      "change_type": "ADDED",
      "size": 3421
    }
  ]
}
```

### 갱신 규칙
- 매일 덮어쓰기
- 최근 24시간 이내 수정된 파일만
- 최대 50개까지만 기록

---

## 4. NEXT_TOMORROW.json

### 목적
다음 세션에서 할 일 목록

### 필드
```json
{
  "timestamp": "ISO8601",
  "main_tasks": [
    {
      "id": "T001",
      "title": "Verify DEVLOG stability",
      "priority": "HIGH",
      "reason": "First production run",
      "related_files": ["tools/devlog_writer.py"]
    }
  ],
  "night_tasks": [
    {
      "id": "N001",
      "title": "Execute REAL_WORK_120",
      "priority": "MEDIUM",
      "reason": "Production batch",
      "related_files": ["GPTORDER/REAL_WORK_120_A.txt"]
    }
  ]
}
```

### 갱신 규칙
- 매일 덮어쓰기
- 템플릿 기반으로 자동 생성
- 사람이 수동으로 수정 가능

---

## 5. INTEGRATION_MAP.json

### 목적
전체 시스템 통합 상태를 숫자/그래프로 추적

### 구조
```json
{
  "timestamp": "ISO8601",
  "version": 3,
  "total_progress": 0.73,
  "nodes": {
    "manager": {
      "id": "manager",
      "name": "Manager",
      "type": "CORE",
      "path": "manager.py",
      "role": "main_entry",
      "status": "WELDED",
      "progress": 1.0
    },
    "evidence_writer": {
      "id": "evidence_writer",
      "name": "Evidence Writer",
      "type": "ENGINE",
      "path": "engine/evidence_writer.py",
      "role": "evidence_generation",
      "status": "WIRED",
      "progress": 1.0
    },
    "navigator": {
      "id": "navigator",
      "name": "Navigator",
      "type": "CORE",
      "path": "main/navigator.py",
      "role": "mission_routing",
      "status": "PLANNED",
      "progress": 0.0
    }
  },
  "edges": [
    {
      "from": "manager",
      "to": "evidence_writer",
      "relation": "USES"
    },
    {
      "from": "manager",
      "to": "devlog_writer",
      "relation": "USES"
    }
  ],
  "meta": {
    "total_nodes": 5,
    "welded_nodes": 2,
    "wired_nodes": 2,
    "planned_nodes": 1,
    "total_edges": 4
  }
}
```

### status 정의
- **WELDED**: 완전 통합 (100%)
- **WIRED**: 연결됨 (50~99%)
- **PLANNED**: 계획만 (0~49%)
- **DEPRECATED**: 폐기 예정

### 갱신 규칙
- 누적 방식 (덮어쓰지 않음)
- 새 노드 추가 시 기존 유지
- progress는 실제 파일 존재/크기 기반 계산
- total_progress = welded/total 비율

### 숫자/그래프 원칙
- 텍스트 최소화
- 모든 상태를 0~1 float로 표현
- 노드/엣지 개수로 진행도 추적
- 시각화 도구로 바로 렌더링 가능하게

---

## 용량 제한

| 파일 | 최대 크기 |
|------|----------|
| DAILY_REPORT | 100KB |
| EVIDENCE_LATEST | 10KB |
| DELTA_TODAY | 50KB |
| NEXT_TOMORROW | 30KB |
| INTEGRATION_MAP | 500KB |

---

## 생성 순서 (중요)

1. EVIDENCE_LATEST.json (최신 RUN 읽기)
2. DELTA_TODAY.json (파일 스캔)
3. INTEGRATION_MAP.json (노드 추가/갱신)
4. NEXT_TOMORROW.json (템플릿 생성)
5. DAILY_REPORT (1~4 종합)

---

## 실패 시 동작

- DEVLOG 생성 실패 → exitcode=1
- 일부 파일만 생성 → FAIL
- 5개 모두 있어야 PASS
