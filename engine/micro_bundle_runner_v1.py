import os, sys, json, subprocess, time, math, traceback, hashlib

# [V33.4] 올인원 봉인기 (외부 hash_manifest_v1 미사용)
def internal_create_manifest(target_dir, files):
    manifest = {}
    for f_name in files:
        f_path = os.path.join(target_dir, f_name)
        if os.path.exists(f_path):
            with open(f_path, "rb") as f:
                manifest[f_name] = hashlib.sha256(f.read()).hexdigest()
    with open(os.path.join(target_dir, "hash_manifest.json"), "w") as f:
        json.dump(manifest, f, indent=4)

def run():
    try:
        run_id, packet_path, truck_id, inner_runner = sys.argv[1:5]
        with open(packet_path, 'r', encoding='utf-8') as f:
            lines = [json.loads(line) for line in f if line.strip()]
        
        bundle_count = math.ceil(len(lines) / 6)
        for i in range(bundle_count):
            b_id = f"bundle_{i+1:02d}"
            b_dir = os.path.join(r"C:\g7core\g7_v1", "runs", run_id, f"truck{truck_id}", b_id)
            os.makedirs(b_dir, exist_ok=True)
            
            chunk = lines[i*6 : (i+1)*6]
            b_packet = os.path.join(b_dir, "bundle_packet.jsonl")
            with open(b_packet, "w", encoding='utf-8') as f:
                for c in chunk: f.write(json.dumps(c, ensure_ascii=False) + "\n")
            
            print(f">>> [{b_id}] Processing 6 tasks...")
            res = subprocess.run(["python", inner_runner, b_packet, b_dir], capture_output=True, text=True)
            
            # 기록 보존
            with open(os.path.join(b_dir, "stdout.txt"), "w") as f: f.write(res.stdout)
            with open(os.path.join(b_dir, "stderr.txt"), "w") as f: f.write(res.stderr)
            with open(os.path.join(b_dir, "exitcode.txt"), "w") as f: f.write(str(res.returncode))
            
            # 외부 모듈 없이 직접 봉인
            internal_create_manifest(b_dir, ["bundle_packet.jsonl", "stdout.txt", "stderr.txt", "exitcode.txt", "verify_report.json"])
            
            if res.returncode != 0:
                print(f"!!! [{b_id}] FAILED.")
                sys.exit(2)
            print(f"--- [{b_id}] PASS.")
            time.sleep(0.1)
    except Exception:
        with open(r"C:\g7core\g7_v1\logs\stderr.txt", "a") as f: f.write(traceback.format_exc())
        sys.exit(2)

if __name__ == "__main__": run()