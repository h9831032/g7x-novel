"""
Patch manager.py to call devlog_writer v2
Fix: Remove self reference, calculate ssot_root directly
"""

import sys
from pathlib import Path


def patch_manager(manager_path: Path) -> bool:
    """Add devlog_writer call to manager finalize"""
    
    if not manager_path.exists():
        print(f"[ERROR] manager.py not found: {manager_path}")
        return False
    
    content = manager_path.read_text(encoding="utf-8")
    
    if "devlog_writer" in content and "generate_devlog_5files" in content:
        print("[SKIP] devlog_writer already integrated")
        return True
    
    backup_path = manager_path.parent / f"{manager_path.name}.bak_patch_manager_devlog"
    backup_path.write_text(content, encoding="utf-8")
    print(f"[BACKUP] {backup_path}")
    
    import_block_lines = [
        "",
        "sys.path.insert(0, str(Path(__file__).parent.parent / 'tools'))",
        "from devlog_writer import generate_devlog_5files"
    ]
    
    if "import sys" in content and "from pathlib import Path" in content:
        lines = content.splitlines()
        insert_pos = None
        for i, line in enumerate(lines):
            if line.startswith("from pathlib import Path"):
                insert_pos = i + 1
                break
        
        if insert_pos:
            for offset, import_line in enumerate(import_block_lines):
                lines.insert(insert_pos + offset, import_line)
            content = "\n".join(lines)
    
    finalize_call = """        try:
            from pathlib import Path as _P
            ssot_root = _P(__file__).resolve().parents[1]
            devlog_files = generate_devlog_5files(ssot_root)
            print("[DEVLOG] Auto-generated 5 files")
        except Exception as e:
            print(f"[DEVLOG ERROR] {e}")
            exitcode = 1
"""
    
    search_pattern = "sys.exit(exitcode)"
    if search_pattern in content:
        content = content.replace(
            search_pattern,
            finalize_call + "\n        " + search_pattern
        )
    else:
        print("[WARN] Could not find sys.exit(exitcode) - manual integration needed")
        return False
    
    manager_path.write_text(content, encoding="utf-8")
    print(f"[PATCHED] {manager_path}")
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python patch_manager_devlog.py <manager_path>")
        sys.exit(1)
    
    manager_path = Path(sys.argv[1])
    success = patch_manager(manager_path)
    sys.exit(0 if success else 1)
