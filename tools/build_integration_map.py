"""
G7X Integration Map Builder
시스템 전체 통합 상태 맵핑
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any


class IntegrationMapBuilder:
    """통합 지도 생성기"""
    
    def __init__(self, ssot_root: Path):
        self.ssot_root = Path(ssot_root)
        self.map_data = {
            "timestamp": datetime.now().isoformat(),
            "ssot_root": str(self.ssot_root),
            "components": {},
            "integration_rate": 0.0
        }
    
    def check_component(self, name: str, path: Path, checks: Dict[str, callable]) -> str:
        """컴포넌트 상태 체크"""
        
        # 기본 상태: 파일 존재 여부
        if not path.exists():
            return "NOT_DONE"
        
        # 추가 체크 수행
        try:
            for check_name, check_func in checks.items():
                if not check_func(path):
                    return "BLOCKED"
            return "DONE"
        except Exception as e:
            return "BLOCKED"
    
    def build(self) -> Dict[str, Any]:
        """통합 지도 빌드"""
        
        # 1. Manager
        manager_path = self.ssot_root / "main" / "manager.py"
        self.map_data["components"]["manager"] = {
            "path": str(manager_path),
            "status": self.check_component("manager", manager_path, {
                "importable": lambda p: "RunManager" in p.read_text(encoding="utf-8"),
                "has_evidence": lambda p: "evidence_writer" in p.read_text(encoding="utf-8")
            }),
            "role": "메인 실행 엔트리 포인트"
        }
        
        # 2. Evidence Writer
        evidence_path = self.ssot_root / "engine" / "evidence_writer.py"
        self.map_data["components"]["evidence_writer"] = {
            "path": str(evidence_path),
            "status": self.check_component("evidence_writer", evidence_path, {
                "class_exists": lambda p: "EvidenceWriter" in p.read_text(encoding="utf-8")
            }),
            "role": "증거팩 생성 전용"
        }
        
        # 3. Night Guard
        guard_path = self.ssot_root / "main" / "night_shift_guard_v5.py"
        self.map_data["components"]["night_guard"] = {
            "path": str(guard_path),
            "status": self.check_component("night_guard", guard_path, {}),
            "role": "검문소 + FAIL_FAST"
        }
        
        # 4. One Shot
        oneshot_path = self.ssot_root / "tools" / "one_shot_night_work_600.py"
        self.map_data["components"]["one_shot"] = {
            "path": str(oneshot_path),
            "status": self.check_component("one_shot", oneshot_path, {}),
            "role": "야간 자동 실행 트리거"
        }
        
        # 5. Work Catalog Builder
        catalog_builder_path = self.ssot_root / "tools" / "build_work_catalog_v3.py"
        self.map_data["components"]["catalog_builder"] = {
            "path": str(catalog_builder_path),
            "status": self.check_component("catalog_builder", catalog_builder_path, {}),
            "role": "600발 탄창 생성"
        }
        
        # 6. GPTORDER
        gptorder_dir = self.ssot_root / "GPTORDER"
        gptorder_files = list(gptorder_dir.glob("REAL_WORK_*.txt")) if gptorder_dir.exists() else []
        self.map_data["components"]["gptorder"] = {
            "path": str(gptorder_dir),
            "status": "DONE" if len(gptorder_files) > 0 else "NOT_DONE",
            "role": "오더 입력 폴더",
            "files_count": len(gptorder_files)
        }
        
        # 7. RUN 폴더 최신 상태 체크
        runs_dir = self.ssot_root / "runs"
        if runs_dir.exists():
            run_dirs = sorted(runs_dir.glob("RUN_*"), key=lambda p: p.name, reverse=True)
            if run_dirs:
                latest_run = run_dirs[0]
                
                # 증거팩 완성도 체크
                evidence_complete = all([
                    (latest_run / "verify_report.json").exists(),
                    (latest_run / "stamp_manifest.json").exists(),
                    (latest_run / "final_audit.json").exists(),
                    (latest_run / "exitcode.txt").exists(),
                    (latest_run / "blackbox_log.jsonl").exists()
                ])
                
                self.map_data["components"]["latest_run"] = {
                    "path": str(latest_run),
                    "status": "DONE" if evidence_complete else "BLOCKED",
                    "role": "최신 실행 결과",
                    "evidence_complete": evidence_complete
                }
        
        # 통합률 계산
        total_components = len(self.map_data["components"])
        done_count = sum(1 for c in self.map_data["components"].values() if c["status"] == "DONE")
        self.map_data["integration_rate"] = (done_count / total_components * 100) if total_components > 0 else 0
        
        return self.map_data
    
    def save(self, output_path: Path):
        """통합 지도 저장"""
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.map_data, f, indent=2, ensure_ascii=False)
        print(f"[INTEGRATION MAP] Saved to {output_path}")
        print(f"[INTEGRATION MAP] Rate: {self.map_data['integration_rate']:.1f}%")


def main():
    import sys
    
    ssot_root = Path("C:\\g7core\\g7_v1")
    if len(sys.argv) > 1:
        ssot_root = Path(sys.argv[1])
    
    builder = IntegrationMapBuilder(ssot_root)
    map_data = builder.build()
    
    output_path = ssot_root / "INTEGRATION_MAP.json"
    builder.save(output_path)


if __name__ == "__main__":
    main()
