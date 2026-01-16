import sys, json, os, hashlib

def get_sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(4096), b""): h.update(b)
    return h.hexdigest().upper()

def main(run_dir):
    m_p = os.path.join(run_dir, "hash_manifest.json")
    if not os.path.exists(m_p): sys.exit(2)
    with open(m_p, "r", encoding="utf-8") as f: m = json.load(f)
    if m.get("meta", {}).get("schema") != "MANIFEST_V1": sys.exit(2)
    for fn, exp in m["files"].items():
        if fn == "hash_manifest.json": continue
        fp = os.path.join(run_dir, fn)
        if not os.path.exists(fp) or get_sha256(fp) != exp.upper():
            print(f"MISMATCH: {fn}"); sys.exit(2)
    print("VERIFIED"); sys.exit(0)

if __name__ == "__main__":
    main(sys.argv[1])