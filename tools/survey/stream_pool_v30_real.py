import os, sys, json, hashlib, time, argparse
from sensor_pack_v1 import SensorPackV1
from exception_pack_v1 import ExceptionPackV1

def get_sha1(text):
    return hashlib.sha1(text.encode('utf-8')).hexdigest().upper()

def run_miner(input_dir, out_dir, target_count):
    # [P0-009] Input Dir 검사
    if not os.path.exists(input_dir):
        print(f"CRITICAL_ERROR: Input dir {input_dir} missing")
        sys.exit(2)

    sensors = SensorPackV1()
    exceptions = ExceptionPackV1()
    
    secured_records = []
    seen_hashes = set()
    manifest = []
    
    # [P2-043] Streaming Iteration 시작
    print(f">>> STARTING STREAMING MINER. TARGET: {target_count}")
    
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if not (file.endswith(".jsonl") or file.endswith(".txt")): continue
            
            with open(os.path.join(root, file), "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    text = line.strip()
                    if len(text) < 50: continue # [P2-045] 단문 스킵
                    
                    h = get_sha1(text)
                    if h in seen_hashes: continue
                    
                    # [P1-031] 센서 및 예외 투사
                    s_res = sensors.analyze_record(text)
                    e_res = exceptions.apply_exceptions(s_res)
                    
                    record = {
                        "sha1": h,
                        "text": text[:100] + "...",
                        "sensors": s_res,
                        "exceptions": e_res,
                        "final_risk": e_res["risk_after"]
                    }
                    
                    secured_records.append(record)
                    seen_hashes.add(h)
                    
                    # [P0-008] 10건마다 진행 보고
                    if len(secured_records) % 10 == 0:
                        print(f"[SECURED] {len(secured_records)} / {target_count}")
                    
                    if len(secured_records) >= target_count: break
            if len(secured_records) >= target_count: break

    # [P0-004, 032] 물리 저장 및 매니페스트 생성
    for i, rot in enumerate(['A', 'B', 'C']):
        chunk = secured_records[i*120 : (i+1)*120]
        file_name = f"ROTATION_{rot}.jsonl"
        path = os.path.join(out_dir, file_name)
        
        with open(path, "w", encoding="utf-8") as out_f:
            for r in chunk:
                out_f.write(json.dumps(r, ensure_ascii=False) + "\n")
        
        # [P0-005] Manifest 영수증 기록
        manifest.append(f"{file_name},{os.path.getsize(path)},{get_sha1(open(path).read())},{time.ctime()}")

    with open(os.path.join(out_dir, "hash_manifest.csv"), "w") as m_f:
        m_f.write("relpath,size_bytes,sha1,created_utc\n")
        m_f.write("\n".join(manifest))

    # [P0-006] receipt.json 발행
    receipt = {
        "run_id": os.path.basename(out_dir),
        "actual_records": len(secured_records),
        "target_records": target_count,
        "sys_executable": sys.executable
    }
    with open(os.path.join(out_dir, "receipt.json"), "w") as r_f:
        json.dump(receipt, r_f, indent=4)

    print(">>> MINING_COMPLETE. DATA_SEALED.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=int, default=360)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    run_miner(r"C:\g6core\g6_v24\data\umr\chunks", args.out, args.target)
