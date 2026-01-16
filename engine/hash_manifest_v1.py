import hashlib, os, json, time

def get_sha256(path):
    if not os.path.exists(path): return None
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192): sha.update(chunk)
    return sha.hexdigest()

def create_manifest(target_dir, file_list, run_id):
    manifest = {
        "files": {f: get_sha256(os.path.join(target_dir, f)) for f in file_list},
        "meta": {
            "schema": "MANIFEST_V1",
            "run_id": run_id,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    }
    with open(os.path.join(target_dir, "hash_manifest.json"), "w", encoding="utf-8") as m:
        json.dump(manifest, m, indent=4)

def verify_manifest(target_dir):
    m_path = os.path.join(target_dir, "hash_manifest.json")
    if not os.path.exists(m_path): return False
    with open(m_path, "r", encoding="utf-8") as m:
        manifest = json.load(m)
    for f, h in manifest["files"].items():
        if get_sha256(os.path.join(target_dir, f)) != h: return False
    return True