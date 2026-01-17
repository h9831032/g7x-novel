"""Catalog & Compiler Pipeline"""

import os
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def load_orders(order_path: Path) -> List[str]:
    """
    주문서 파일을 읽어 list[str]로 반환 (베이직엔진 용접용)

    Args:
        order_path: 주문서 파일 경로

    Returns:
        List[str]: 미션 목록 (빈 줄 제외)
    """
    if not order_path.exists():
        raise FileNotFoundError(f"Order file not found: {order_path}")

    with open(order_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    return lines


def _find_latest_file(glob_pat: str, root: Path) -> Optional[Path]:
    hits = list(root.glob(glob_pat))
    if not hits:
        return None
    hits.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return hits[0]


class CatalogCompiler:
    def __init__(self, ssot_root: Path):
        self.ssot_root = ssot_root
        self.catalog_path: Optional[Path] = None
        self.catalog_index: List[Dict[str, Any]] = []

    def locate_catalog(self, order_path: Path) -> Optional[Path]:
        env_path = os.environ.get("G7X_CATALOG_PATH", "").strip()
        if env_path:
            p = Path(env_path)
            if p.exists():
                return p

        candidate = order_path.with_suffix(".jsonl")
        if candidate.exists():
            return candidate

        gptorder_dir = self.ssot_root / "GPTORDER"
        if gptorder_dir.exists():
            latest = _find_latest_file("mission_catalog*.jsonl", gptorder_dir)
            if latest and latest.exists():
                return latest

        latest2 = _find_latest_file("mission_catalog*.jsonl", self.ssot_root)
        if latest2 and latest2.exists():
            return latest2

        return None

    def load_catalog(self, order_path: Path) -> None:
        self.catalog_path = self.locate_catalog(order_path)
        self.catalog_index = []
        if not self.catalog_path:
            return

        with open(self.catalog_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    self.catalog_index.append(obj)
                except Exception:
                    continue

    def _pick_prompt(self, obj: Dict[str, Any]) -> str:
        for k in ("prompt", "text", "instruction", "content"):
            v = obj.get(k)
            if isinstance(v, str) and v.strip():
                return v.strip()

        if "contents" in obj and isinstance(obj["contents"], list) and obj["contents"]:
            c0 = obj["contents"][0]
            if isinstance(c0, dict) and "parts" in c0 and isinstance(c0["parts"], list):
                return "".join(str(p.get("text", "")) for p in c0["parts"]).strip()

        return ""

    def compile_prompt(self, order_line: str) -> Tuple[str, Dict[str, Any]]:
        meta: Dict[str, Any] = {
            "catalog_used": 0,
            "compiler_used": 0,
            "catalog_path": str(self.catalog_path) if self.catalog_path else "",
            "compile_mode": "raw",
        }

        line = order_line.strip()
        if not line:
            return "", meta

        if line.startswith("MODEL="):
            meta["compile_mode"] = "directive_model"
            return "", meta
        if line.startswith("CATALOG="):
            meta["compile_mode"] = "directive_catalog"
            return "", meta

        if not self.catalog_index:
            return line, meta

        idx: Optional[int] = None
        if line.startswith("mission_"):
            try:
                idx = int(line.split("_", 1)[1]) - 1
            except Exception:
                idx = None

        if idx is None and line.isdigit():
            try:
                idx = int(line) - 1
            except Exception:
                idx = None

        if idx is not None and 0 <= idx < len(self.catalog_index):
            obj = self.catalog_index[idx]
            prompt = self._pick_prompt(obj)
            if prompt:
                meta["catalog_used"] = 1
                meta["compiler_used"] = 1
                meta["compile_mode"] = "catalog_index"
                return prompt, meta

        for obj in self.catalog_index:
            mid = obj.get("mission_id") or obj.get("id")
            if isinstance(mid, str) and mid.strip() == line:
                prompt = self._pick_prompt(obj)
                if prompt:
                    meta["catalog_used"] = 1
                    meta["compiler_used"] = 1
                    meta["compile_mode"] = "catalog_match"
                    return prompt, meta

        return line, meta
