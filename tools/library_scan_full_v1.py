import os, sys, json, hashlib, threading, time
from concurrent.futures import ThreadPoolExecutor

write_lock = threading.Lock()

def get_sha1(data):
    return hashlib.sha1(data.encode('utf-8') if isinstance(data, str) else data).hexdigest()

def process_file_stream(info):
    fp, run_dir, chunk_len, current_idx, total_files = info
    try:
        perc = (current_idx / total_files) * 100
        sys.stderr.write(f"\r[6-LANE FULL] {perc:>5.1f}% | {os.path.basename(fp)[:25]:<25}")
        sys.stderr.flush()

        f_size, f_mtime = os.path.getsize(fp), os.path.getmtime(fp)
        recs, f_hash, offset = [], hashlib.sha1(), 0
        with open(fp, "rb") as f:
            while True:
                chunk_data = f.read(65536) # 64KB 스트리밍 (메모리 가드)
                if not chunk_data: break
                f_hash.update(chunk_data)
                
                for j in range(0, len(chunk_data), chunk_len):
                    sub_chunk = chunk_data[j:j+chunk_len]
                    try: text = sub_chunk.decode('utf-8', errors='ignore')
                    except: text = sub_chunk.decode('cp949', errors='ignore')

                    recs.append({
                        "chunk_id": "PENDING", "file_path": fp, "file_size": f_size, 
                        "file_mtime": f_mtime, "offset": offset + j, "length": len(sub_chunk),
                        "chunk_sha1": get_sha1(sub_chunk), "text_preview": text[:80].replace("\n", " "),
                        "encoding": "auto_stream"
                    })
                offset += len(chunk_data)
        
        final_f_sha1 = f_hash.hexdigest()
        for r in recs:
            r["chunk_id"] = f"CHK-{final_f_sha1[:8]}-{r['offset']//chunk_len:05d}"
            r["file_sha1"] = final_f_sha1

        with write_lock:
            with open(os.path.join(run_dir, "library_index.jsonl"), "a", encoding="utf-8") as out:
                for r in recs: out.write(json.dumps(r, ensure_ascii=False) + "\n")
        return len(recs)
    except: return 0

def scan_main(src, run_dir):
    # 제로베이스: 기존 인덱스 로드 생략 (마스터에서 폴더 삭제 처리)
    all_found = [os.path.join(r, f) for r, _, fs in os.walk(src) for f in fs]
    total = len(all_found)
    sys.stderr.write(f"\n### [ZERO-BASE] New Start: {total} files found.\n")

    if total == 0: return {"file_count": 0, "chunk_count": 0}
    with ThreadPoolExecutor(max_workers=6) as ex:
        counts = list(ex.map(process_file_stream, [(fp, run_dir, 2500, i+1, total) for i, fp in enumerate(all_found)]))
    return {"file_count": total, "chunk_count": sum(counts)}

if __name__ == "__main__":
    if len(sys.argv) < 3: sys.exit(1)
    print(json.dumps(scan_main(sys.argv[1], sys.argv[2])))