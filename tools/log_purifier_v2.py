import os
import json

LOG_PATH = r"C:/g7core/g7_v1/runs/REAL/DEVLOG/devlog.jsonl"

def nuclear_purify():
    if not os.path.exists(LOG_PATH):
        print("[FAIL] Log file missing.")
        return

    valid_types = ["NAV_LIGHT_TEST_V1", "DEVLOG_TEST", "NOVEL_GENERATION"]
    purified_lines = []
    
    with open(LOG_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line: continue
            try:
                item = json.loads(line)
                t_type = item.get("data", {}).get("task_type")
                # 유효한 task_type 리스트에 포함된 경우만 살려둠
                if t_type in valid_types:
                    purified_lines.append(line + "\n")
            except:
                continue

    with open(LOG_PATH, 'w', encoding='utf-8') as f:
        f.writelines(purified_lines)
    
    print(f"[PURIFY] Cleanup complete. {len(purified_lines)} valid logs remain.")

if __name__ == "__main__":
    nuclear_purify()