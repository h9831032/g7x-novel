import os, sys, json, hashlib, time

def get_sha1(data):
    return hashlib.sha1(data.encode('utf-8') if isinstance(data, str) else data).hexdigest()

def read_safe(f_path):
    for enc in ['utf-8', 'cp949']:
        try:
            with open(f_path, "r", encoding=enc) as f: return f.read(), enc, None
        except: continue
    return None, None, "DECODE_FAIL"

def run_pipeline(src_root, run_dir, chunk_len=2500):
    idx_p = os.path.join(run_dir, "library_index.jsonl")
    tag_p = os.path.join(run_dir, "tag_index_rules.jsonl")
    str_p = os.path.join(run_dir, "strike_list.jsonl")
    
    stats = {"file_count": 0, "chunk_count": 0, "strike_count": 0}
    danger_map = {
        "drift": ["급변", "붕괴", "갑자기", "돌변", "누락"],
        "logic": ["오류", "모순", "불가능", "안맞음", "이상함"],
        "rule": ["수치", "설정", "반복", "도배", "금지"]
    }

    with open(idx_p, "w", encoding="utf-8") as f_idx, \
         open(tag_p, "w", encoding="utf-8") as f_tag, \
         open(str_p, "w", encoding="utf-8") as f_str:
        
        for root, _, files in os.walk(src_root):
            for file in files:
                stats["file_count"] += 1
                fp = os.path.join(root, file)
                content, enc, skip = read_safe(fp)
                
                if skip:
                    f_idx.write(json.dumps({"chunk_id": f"SKIP-{stats['file_count']}", "file_path": fp, "skip_reason": skip}, ensure_ascii=False)+"\n")
                    continue

                f_sha1, f_size, f_mtime = get_sha1(content), os.path.getsize(fp), os.path.getmtime(fp)
                
                for i in range(0, len(content), chunk_len):
                    chunk = content[i:i+chunk_len]
                    chunk_id = f"CHK-{f_sha1[:8]}-{i//chunk_len:05d}"
                    preview = chunk[:80].replace("\n", " ")
                    
                    # 1. 인덱싱 레코드
                    idx_rec = {
                        "chunk_id": chunk_id, "file_path": fp, "file_size": f_size,
                        "file_mtime": f_mtime, "offset": i, "length": len(chunk),
                        "chunk_sha1": get_sha1(chunk), "text_preview": preview,
                        "encoding_used": enc
                    }
                    f_idx.write(json.dumps(idx_rec, ensure_ascii=False) + "\n")
                    stats["chunk_count"] += 1
                    
                    # 2. 태깅 (딱지 붙이기)
                    risk = {k: len([w for w in v if w in preview]) for k, v in danger_map.items()}
                    reasons = [w for v in danger_map.values() for w in v if w in preview]
                    hit = any(risk.values())
                    
                    tag_rec = {"chunk_id": chunk_id, "tags": {"needs_strike": hit, "reasons": reasons, "risk": risk}, "mode": "RULES"}
                    f_tag.write(json.dumps(tag_rec, ensure_ascii=False) + "\n")
                    
                    # 3. 스트라이크 리스트 (Layer-2 타겟)
                    if hit:
                        idx_rec.update({"reasons": reasons, "risk": risk})
                        f_str.write(json.dumps(idx_rec, ensure_ascii=False) + "\n")
                        stats["strike_count"] += 1
                        
    return stats

if __name__ == "__main__":
    if len(sys.argv) < 3: sys.exit(1)
    print(json.dumps(run_pipeline(sys.argv[1], sys.argv[2])))