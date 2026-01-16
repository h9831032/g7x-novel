import os, hashlib, json
def seal():
    root = r"C:\g7core\g7_v1\runs"
    manifest = []
    for base, _, files in os.walk(root):
        for f in files:
            p = os.path.join(base, f)
            h = hashlib.sha256()
            with open(p, 'rb') as fb:
                for chunk in iter(lambda: fb.read(65536), b""): h.update(chunk)
            manifest.append({"path": os.path.relpath(p, root), "sha256": h.hexdigest(), "size": os.path.getsize(p)})
    
    with open(r"C:\g7core\g7_v1\master_seal.json", 'w') as f:
        json.dump({"project": "G7X", "status": "SEALED", "total_files": len(manifest), "data": manifest}, f, indent=4)
    print(f"SUCCESS: {len(manifest)} files sealed into master_seal.json")
if __name__ == "__main__": seal()
