import os, sys, csv

LEGACY_PATH = r"C:\g6core\g6_v24"

def get_snapshot():
    snapshot = []
    for root, dirs, files in os.walk(LEGACY_PATH):
        for f in files:
            p = os.path.join(root, f)
            st = os.stat(p)
            snapshot.append({"path": p, "size": st.st_size, "mtime": st.st_mtime})
    return snapshot

def save_csv(snapshot, target_path):
    keys = ["path", "size", "mtime"]
    with open(target_path, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(snapshot)

def check_diff(pre_csv, post_csv):
    with open(pre_csv, 'r', encoding="utf-8") as f: pre = f.read()
    with open(post_csv, 'r', encoding="utf-8") as f: post = f.read()
    return pre != post