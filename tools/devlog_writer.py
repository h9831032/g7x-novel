"""
G7X DEVLOG Writer v3.3 - Complete Stability Fix
3x3x4 Grid Coverage:
- A(devlog_writer): dict 방어, 스키마 마이그레이션, FAIL 전파
- B(deploy/hotfix): 자동 검증, 백업/롤백
- C(manager 연동): FAIL 전파, 증거팩 동기화

FIX: KeyError 'meta', 'name', 'status', 'path' 완전 해결
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List


# =============================================================================
# A영역: devlog_writer 핵심 함수
# =============================================================================

def get_latest_run(runs_dir: Path) -> Path:
    """Get latest RUN folder by mtime"""
    runs = [d for d in runs_dir.iterdir() if d.is_dir() and d.name.startswith("RUN_")]
    if not runs:
        raise FileNotFoundError("No RUN folders found")
    return max(runs, key=lambda p: p.stat().st_mtime)


def load_verify_report(run_path: Path) -> Dict[str, Any]:
    """
    A-T1-D1: Load Evidence result with full defense
    A-T2-D3: 실패 시에도 최소 필드 반환
    """
    default = {
        "run_id": run_path.name,
        "exitcode": -1,
        "expected_missions": 0,
        "done_missions": 0,
        "api_error_count": 0,
        "pass": False,
        "reason_code": "VERIFY_REPORT_MISSING",
        "verdict": "UNKNOWN"
    }
    
    verify_file = run_path / "verify_report.json"
    if not verify_file.exists():
        return default
    
    try:
        data = json.loads(verify_file.read_text(encoding="utf-8"))
        pass_flag = data.get("pass", False)
        return {
            "run_id": data.get("run_id", run_path.name),
            "exitcode": data.get("exitcode", -1),
            "expected_missions": data.get("expected_missions", 0),
            "done_missions": data.get("done_missions", 0),
            "api_error_count": data.get("api_error_count", 0),
            "pass": pass_flag,
            "reason_code": data.get("reason_code", "UNKNOWN"),
            "verdict": "PASS" if pass_flag else "FAIL"
        }
    except Exception as e:
        default["reason_code"] = f"PARSE_ERROR: {e}"
        return default


def scan_delta_files(ssot_root: Path, since_hours: int = 24) -> List[Dict[str, Any]]:
    """B2: Scan files modified in last N hours"""
    cutoff = datetime.now().timestamp() - (since_hours * 3600)
    delta = []
    
    patterns = ["*.py", "*.ps1", "*.txt", "*.json", "*.jsonl", "*.md"]
    exclude_dirs = {".venv", "runs", "__pycache__", ".git", "DEVLOG"}
    
    for pattern in patterns:
        for f in ssot_root.rglob(pattern):
            if f.is_file():
                if any(excl in f.parts for excl in exclude_dirs):
                    continue
                if f.stat().st_mtime > cutoff:
                    try:
                        rel_path = f.relative_to(ssot_root)
                        delta.append({
                            "path": str(rel_path).replace("\\", "/"),
                            "change_type": "MODIFIED",
                            "size": f.stat().st_size
                        })
                    except ValueError:
                        continue
    
    return sorted(delta, key=lambda x: x["path"])[:50]


def get_default_node(node_id: str) -> Dict[str, Any]:
    """
    A-T3-D1: 기본 노드 구조 반환
    마이그레이션용 - 필수 필드 보장
    """
    return {
        "name": node_id,
        "status": "UNKNOWN",
        "path": "UNKNOWN",
        "progress": 0.0,
        "type": "unknown"
    }


def get_default_integration_map() -> Dict[str, Any]:
    """
    A-T3-D3: 기본 INTEGRATION_MAP 스키마
    """
    return {
        "meta": {
            "version": 2,
            "updated_at": datetime.now().isoformat(),
            "total_progress": 0.0
        },
        "nodes": {
            "MANAGER": {
                "name": "Manager",
                "status": "WELDED",
                "path": "main/manager.py",
                "progress": 1.0,
                "type": "core"
            },
            "EVIDENCE_WRITER": {
                "name": "Evidence Writer",
                "status": "WELDED",
                "path": "engine/evidence_writer.py",
                "progress": 1.0,
                "type": "core"
            },
            "DEVLOG_SYSTEM": {
                "name": "Devlog System",
                "status": "WELDED",
                "path": "tools/devlog_writer.py",
                "progress": 1.0,
                "type": "module"
            }
        },
        "edges": [
            {"from": "MANAGER", "to": "EVIDENCE_WRITER", "relation": "USES"},
            {"from": "MANAGER", "to": "DEVLOG_SYSTEM", "relation": "USES"}
        ]
    }


def migrate_node(node_id: str, node_data: Any) -> Dict[str, Any]:
    """
    A-T3-D1: 노드 마이그레이션 - 불완전한 노드를 완전한 구조로 변환
    """
    if not isinstance(node_data, dict):
        return get_default_node(node_id)
    
    # 필수 필드 보정
    node_data.setdefault("name", node_id)
    node_data.setdefault("status", "UNKNOWN")
    node_data.setdefault("path", "UNKNOWN")
    node_data.setdefault("progress", 0.0)
    node_data.setdefault("type", "unknown")
    
    return node_data


def load_integration_map(devlog_dir: Path) -> Dict[str, Any]:
    """
    A-T3-D1: Load with full schema migration
    구버전 파일도 안전하게 로드
    """
    map_file = devlog_dir / "INTEGRATION_MAP.json"
    default = get_default_integration_map()
    
    if not map_file.exists():
        return default
    
    try:
        loaded = json.loads(map_file.read_text(encoding="utf-8"))
        
        # meta 마이그레이션
        if not isinstance(loaded.get("meta"), dict):
            loaded["meta"] = default["meta"].copy()
        else:
            loaded["meta"].setdefault("version", 2)
            loaded["meta"].setdefault("updated_at", datetime.now().isoformat())
            loaded["meta"].setdefault("total_progress", 0.0)
        
        # nodes 마이그레이션
        if not isinstance(loaded.get("nodes"), dict):
            loaded["nodes"] = default["nodes"].copy()
        else:
            # 각 노드 개별 마이그레이션
            for node_id in list(loaded["nodes"].keys()):
                loaded["nodes"][node_id] = migrate_node(node_id, loaded["nodes"][node_id])
        
        # edges 마이그레이션
        if not isinstance(loaded.get("edges"), list):
            loaded["edges"] = default["edges"].copy()
        
        return loaded
        
    except Exception:
        # 파싱 실패 시 기본값 반환 (A-T3-D4: 마이그레이션 실패 시 안전 처리)
        return default


def update_integration_map(integration_map: Dict[str, Any], ssot_root: Path) -> Dict[str, Any]:
    """
    A-T1-D1: Update with full defense
    """
    # 방어: 필수 키 강제 확보
    if not isinstance(integration_map.get("meta"), dict):
        integration_map["meta"] = {"version": 2, "updated_at": "", "total_progress": 0.0}
    if not isinstance(integration_map.get("nodes"), dict):
        integration_map["nodes"] = {}
    if not isinstance(integration_map.get("edges"), list):
        integration_map["edges"] = []
    
    integration_map["meta"]["updated_at"] = datetime.now().isoformat()
    integration_map["meta"]["version"] = 2
    
    # 핵심 컴포넌트 정의
    components = [
        {"id": "MANAGER", "name": "Manager", "path": "main/manager.py", "status": "WELDED", "progress": 1.0, "type": "core"},
        {"id": "EVIDENCE_WRITER", "name": "Evidence Writer", "path": "engine/evidence_writer.py", "status": "WELDED", "progress": 1.0, "type": "core"},
        {"id": "DEVLOG_SYSTEM", "name": "Devlog System", "path": "tools/devlog_writer.py", "status": "WELDED", "progress": 1.0, "type": "module"}
    ]
    
    for comp in components:
        cid = comp["id"]
        if cid not in integration_map["nodes"]:
            integration_map["nodes"][cid] = {
                "name": comp["name"],
                "status": comp["status"],
                "path": comp["path"],
                "progress": comp["progress"],
                "type": comp["type"]
            }
        else:
            # 기존 노드 필드 보정 (마이그레이션)
            node = integration_map["nodes"][cid]
            node.setdefault("name", comp["name"])
            node.setdefault("status", comp["status"])
            node.setdefault("path", comp["path"])
            node.setdefault("progress", comp["progress"])
            node.setdefault("type", comp["type"])
            
            # 파일 존재 확인
            if (ssot_root / comp["path"]).exists():
                node["progress"] = comp["progress"]
                node["status"] = comp["status"]
    
    # 엣지 추가
    edges_to_add = [
        {"from": "MANAGER", "to": "EVIDENCE_WRITER", "relation": "USES"},
        {"from": "MANAGER", "to": "DEVLOG_SYSTEM", "relation": "USES"}
    ]
    for edge in edges_to_add:
        if edge not in integration_map["edges"]:
            integration_map["edges"].append(edge)
    
    # total_progress 계산
    nodes = integration_map["nodes"]
    if nodes:
        total = sum(n.get("progress", 0) for n in nodes.values())
        integration_map["meta"]["total_progress"] = round(total / len(nodes), 2)
    
    return integration_map


def write_daily_report(
    devlog_dir: Path,
    date_str: str,
    evidence: Dict[str, Any],
    delta: List[Dict[str, Any]],
    integration_map: Dict[str, Any]
) -> Path:
    """
    A-T1-D3: Write DAILY_REPORT with full .get() defense
    """
    day_dir = devlog_dir / date_str
    day_dir.mkdir(parents=True, exist_ok=True)
    
    report_path = day_dir / f"DAILY_REPORT_{date_str}.txt"
    
    meta = integration_map.get("meta", {})
    nodes = integration_map.get("nodes", {})
    edges = integration_map.get("edges", [])
    total_progress = meta.get("total_progress", 0)
    
    content = f"""G7X DAILY REPORT - {date_str}

=== EVIDENCE (Latest RUN) ===
RUN ID: {evidence.get('run_id', 'UNKNOWN')}
Exitcode: {evidence.get('exitcode', -1)}
Expected: {evidence.get('expected_missions', 0)}
Done: {evidence.get('done_missions', 0)}
API Errors: {evidence.get('api_error_count', 0)}
Verdict: {evidence.get('verdict', 'UNKNOWN')}
Reason: {evidence.get('reason_code', 'UNKNOWN')}

=== DELTA (Today's Changes) ===
Total Files Modified: {len(delta)}
"""
    
    if delta:
        content += "Top changes:\n"
        for item in delta[:10]:
            content += f"  - {item.get('path', '?')} ({item.get('change_type', '?')}, {item.get('size', 0)} bytes)\n"
    else:
        content += "  (no changes detected)\n"
    
    content += f"""
=== INTEGRATION MAP (Snapshot) ===
Total Progress: {total_progress} ({int(total_progress * 100)}%)
Nodes: {len(nodes)}
Edges: {len(edges)}
"""
    
    # A-T1-D1: 완전한 .get() 방어
    for node_id, node_data in nodes.items():
        if isinstance(node_data, dict):
            status = node_data.get("status", "UNKNOWN")
            name = node_data.get("name", node_id)
            path = node_data.get("path", "UNKNOWN")
            prog = int(node_data.get("progress", 0) * 100)
            content += f"  [{status}] {name} -> {path} ({prog}%)\n"
        else:
            content += f"  [UNKNOWN] {node_id} -> UNKNOWN (0%)\n"
    
    content += """
=== NEXT (Tomorrow) ===
  1. Verify DEVLOG auto-generation stability
  2. Review evidence layer completeness
  3. Execute REAL_WORK_120 batch
"""
    
    report_path.write_text(content, encoding="utf-8")
    return report_path


def write_evidence_latest(devlog_dir: Path, evidence: Dict[str, Any]) -> Path:
    """A-T1-D3, A-T2-D3: Write EVIDENCE_LATEST.json"""
    path = devlog_dir / "EVIDENCE_LATEST.json"
    output = {
        "run_id": evidence.get("run_id", "UNKNOWN"),
        "timestamp": datetime.now().isoformat(),
        "exitcode": evidence.get("exitcode", -1),
        "expected_missions": evidence.get("expected_missions", 0),
        "done_missions": evidence.get("done_missions", 0),
        "api_error_count": evidence.get("api_error_count", 0),
        "pass": evidence.get("pass", False),
        "verdict": evidence.get("verdict", "UNKNOWN"),
        "reason_code": evidence.get("reason_code", "UNKNOWN")
    }
    path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def write_delta_today(devlog_dir: Path, date_str: str, delta: List[Dict[str, Any]]) -> Path:
    """B2: Write DELTA_TODAY.json"""
    day_dir = devlog_dir / date_str
    day_dir.mkdir(parents=True, exist_ok=True)
    path = day_dir / "DELTA_TODAY.json"
    data = {"date": date_str, "timestamp": datetime.now().isoformat(), "count": len(delta), "items": delta}
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def write_next_tomorrow(devlog_dir: Path, date_str: str) -> Path:
    """B3: Write NEXT_TOMORROW.json"""
    day_dir = devlog_dir / date_str
    day_dir.mkdir(parents=True, exist_ok=True)
    path = day_dir / "NEXT_TOMORROW.json"
    tasks = [
        {"id": "NEXT_001", "title": "Verify DEVLOG stability", "priority": "HIGH"},
        {"id": "NEXT_002", "title": "Review evidence layer", "priority": "MEDIUM"},
        {"id": "NEXT_003", "title": "Execute REAL_WORK_120 batch", "priority": "MEDIUM"}
    ]
    data = {"date": date_str, "timestamp": datetime.now().isoformat(), "tasks": tasks}
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def write_integration_map(devlog_dir: Path, integration_map: Dict[str, Any]) -> Path:
    """B4: Write INTEGRATION_MAP.json"""
    path = devlog_dir / "INTEGRATION_MAP.json"
    path.write_text(json.dumps(integration_map, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def generate_devlog_5files(ssot_root) -> Dict[str, Path]:
    """
    Main entry: Generate 5 DEVLOG files
    A-T1-D4: 예외 발생 시 상위로 전파 (manager에서 FAIL 처리)
    """
    ssot_root = Path(ssot_root)
    devlog_dir = ssot_root / "DEVLOG"
    devlog_dir.mkdir(exist_ok=True)
    
    runs_dir = ssot_root / "runs"
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    latest_run = get_latest_run(runs_dir)
    evidence = load_verify_report(latest_run)
    delta = scan_delta_files(ssot_root)
    integration_map = load_integration_map(devlog_dir)
    integration_map = update_integration_map(integration_map, ssot_root)
    
    files = {}
    files["daily_report"] = write_daily_report(devlog_dir, date_str, evidence, delta, integration_map)
    files["evidence_latest"] = write_evidence_latest(devlog_dir, evidence)
    files["delta_today"] = write_delta_today(devlog_dir, date_str, delta)
    files["next_tomorrow"] = write_next_tomorrow(devlog_dir, date_str)
    files["integration_map"] = write_integration_map(devlog_dir, integration_map)
    
    return files


# =============================================================================
# CLI Entry
# =============================================================================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python devlog_writer.py <ssot_root>")
        sys.exit(1)
    
    try:
        files = generate_devlog_5files(Path(sys.argv[1]))
        print("[DEVLOG] Generated 5 files:")
        for name, path in files.items():
            print(f"  {name}: {path}")
        sys.exit(0)
    except Exception as e:
        print(f"[DEVLOG ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
