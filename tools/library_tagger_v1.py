import os, sys, json, hashlib, time

def get_sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(4096), b""): h.update(b)
    return h.hexdigest().upper()

def run_tagging(src_path, run_dir):
    idx_p = os.path.join(run_dir, "library_index.jsonl")
    receipt_p = os.path.join(run_dir, "audit_receipt.jsonl")
    
    # [DRIFT_LOCK] 상태 초기화
    stats = {"total": 0, "drift_unresolved": 0, "errors": 0}
    
    # 태그 규칙 (Layer-1 딱지)
    rules = {
        "ERROR_CANDIDATE": ["오류", "모순", "불가능"],
        "DRIFT_CANDIDATE": ["급변", "돌변", "누락"],
        "FUN_LOW_CANDIDATE": ["지루함", "반복", "도배"],
        "PETRIFY_CANDIDATE": ["정지", "착각", "석화"]
    }

    with open(src_path, "r", encoding="utf-8") as f_in, \
         open(idx_p, "w", encoding="utf-8") as f_idx, \
         open(receipt_p, "w", encoding="utf-8") as f_rec:
        
        for line in f_in:
            data = json.loads(line)
            stats["total"] += 1
            content = data.get("text_preview", "")
            
            # 딱지 붙이기 (Heuristic Tagging)
            found_tags = []
            for tag, keywords in rules.items():
                if any(k in content for k in keywords):
                    found_tags.append(tag)
            
            # [결함 재현 테스트용] 특정 조건에서 강제 drift 발생 (예: CHK-0001)
            # if "CHK-0001" in data.get("chunk_id", ""): stats["drift_unresolved"] += 1
            
            res = {
                "chunk_id": data.get("chunk_id"),
                "tags": found_tags,
                "has_issue": len(found_tags) > 0,
                "v_h": hashlib.sha256(content.encode()).hexdigest()
            }
            f_idx.write(json.dumps(res, ensure_ascii=False) + "\n")
            f_rec.write(json.dumps({"row": stats["total"], "status": "OK"}, ensure_ascii=False) + "\n")

    return stats

if __name__ == "__main__":
    if len(sys.argv) < 3: sys.exit(2)
    res_stats = run_tagging(sys.argv[1], sys.argv[2])
    print(json.dumps(res_stats))