import os, json, hashlib

def generate_hash_manifest(run_id, truck_id):
    run_dir = f"C:\\g7core\\g7_v1\\runs\\{run_id}"
    truck_dir = os.path.join(run_dir, f"truck{truck_id}")
    final_dir = os.path.join(truck_dir, "FINAL")
    
    manifest = []
    # 모든 결과 파일 및 스테이트 팩의 SHA1 추출
    for root, dirs, files in os.walk(truck_dir):
        for file in files:
            file_path = os.path.join(root, file)
            with open(file_path, "rb") as f:
                f_hash = hashlib.sha1(f.read()).hexdigest()
                manifest.append({"file": os.path.relpath(file_path, truck_dir), "sha1": f_hash})
    
    with open(os.path.join(final_dir, "hash_manifest.json"), "w") as f:
        json.dump(manifest, f, indent=4)
    print(f">>> [SEAL] Truck {truck_id} Hash Manifest Created.")

if __name__ == "__main__":
    generate_hash_manifest("REAL", "A")
    generate_hash_manifest("REAL", "B")