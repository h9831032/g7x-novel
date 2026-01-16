import os
import json

LOG_PATH = r"C:/g7core/g7_v1/runs/REAL/DEVLOG/devlog.jsonl"
BACKUP_PATH = LOG_PATH + ".bak"

def purify():
    if not os.path.exists(LOG_PATH):
        print("[FAIL] Log file not found.")
        return

    # 1. 원본 백업
    with open(LOG_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    with open(BACKUP_PATH, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print(f"[SUCCESS] Backup created at {BACKUP_PATH}")

    # 2. 정밀 필터링 (task_type이 없거나 UNKNOWN인 경우 모두 제거)
    purified_lines = []
    removed_count = 0
    
    for line in lines:
        line = line.strip()
        if not line: continue
        try:
            item = json.loads(line)
            data_block = item.get("data", {})
            
            # task_type 필드가 없거나 값이 'UNKNOWN'이면 폐기
            t_type = data_block.get("task_type")
            if not t_type or t_type == "UNKNOWN":
                removed_count += 1
                continue
            
            purified_lines.append(line + "\n")
        except Exception:
            removed_count += 1

    # 3. 장부 최종 갱신
    with open(LOG_PATH, 'w', encoding='utf-8') as f:
        f.writelines(purified_lines)
    
    print(f"[SUCCESS] Result: {len(purified_lines)} items kept, {removed_count} invalid logs removed.")

if __name__ == "__main__":
    purify()