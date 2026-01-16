import json, os, sys
def load_real_novels(file_paths, max_novels=500):
    novel_map = {}
    print(">>> [G7X] Scanning aggregated files for real IDs...")
    for fp in file_paths:
        print(f"    Scanning: {os.path.basename(fp)}")
        try:
            with open(fp, 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip(): continue
                    obj = json.loads(line)
                    nid = obj.get("novel_id") or obj.get("book_id") or "unknown"
                    if nid not in novel_map:
                        if len(novel_map) >= max_novels: return novel_map
                        novel_map[nid] = []
                    novel_map[nid].append(obj.get("text", ""))
        except Exception as e: print(f"SKIP: {fp} due to {e}")
    return novel_map
