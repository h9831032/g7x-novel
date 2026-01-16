import os
import json
import csv
import time
from collections import defaultdict, Counter
from datetime import datetime

# =====================
# CONFIG
# =====================
INPUT_DIR = r"C:\g6core\g6_v24\data\umr\chunks"
OUTPUT_ROOT = r"C:\g7core\g7_v1\runs"
MAX_NOVELS = 1000
CHUNKS_PER_NOVEL_REQUIRED = 110

AMPLIFY_STAGE_1 = 10
AMPLIFY_STAGE_2 = 25
AMPLIFY_STAGE_3 = 50

PROGRESS_EVERY = 50000  # lines

# =====================
# METRIC FUNCTIONS
# =====================

def sentence_lengths(text):
    return [len(s) for s in text.split('.') if len(s.strip()) > 0]

def flattening_score(text):
    lens = sentence_lengths(text)
    if not lens:
        return 0.0
    return 1.0 - (max(lens) - min(lens)) / max(max(lens), 1)

def density_score(text):
    words = text.split()
    if not words:
        return 0.0
    return len(words) / max(len(text), 1)

def rhythm_score(text):
    lens = sentence_lengths(text)
    if len(lens) < 2:
        return 0.0
    diffs = [abs(lens[i] - lens[i-1]) for i in range(1, len(lens))]
    return sum(diffs) / len(diffs)

# =====================
# MAIN
# =====================

def main():
    run_id = f"PHASE18_BUFFER2_V17_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir = os.path.join(OUTPUT_ROOT, run_id)
    per_novel_dir = os.path.join(out_dir, "per_novel")
    os.makedirs(per_novel_dir, exist_ok=True)

    novels = defaultdict(list)
    novel_order = []
    total_lines = 0

    started = datetime.now()

    # -------- STREAM READ --------
    for fname in os.listdir(INPUT_DIR):
        if not fname.endswith(".jsonl"):
            continue
        fpath = os.path.join(INPUT_DIR, fname)
        with open(fpath, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                total_lines += 1
                try:
                    obj = json.loads(line)
                except:
                    continue

                nid = obj.get("novel_id")
                text = obj.get("text", "")
                if not nid or not text:
                    continue

                if nid not in novels:
                    if len(novels) >= MAX_NOVELS:
                        continue
                    novel_order.append(nid)

                novels[nid].append(text)

                if total_lines % PROGRESS_EVERY == 0:
                    print(f"[PROGRESS] lines={total_lines} novels={len(novels)}", flush=True)

    # -------- ANALYSIS --------
    rows = []
    insufficient = []

    for nid in novel_order:
        chunks = novels[nid]
        chunk_count = len(chunks)

        if chunk_count < CHUNKS_PER_NOVEL_REQUIRED:
            insufficient.append(nid)
            rows.append({
                "novel_id": nid,
                "insufficient_chunks": chunk_count
            })
            continue

        flat_vals = []
        dens_vals = []
        rhy_vals = []

        for txt in chunks:
            flat_vals.append(flattening_score(txt))
            dens_vals.append(density_score(txt))
            rhy_vals.append(rhythm_score(txt))

        # base metrics
        flat_mean = sum(flat_vals) / len(flat_vals)
        dens_mean = sum(dens_vals) / len(dens_vals)
        rhy_mean = sum(rhy_vals) / len(rhy_vals)

        # amplification stages
        stage1 = (flat_mean + dens_mean + rhy_mean) * AMPLIFY_STAGE_1
        stage2 = stage1 * (AMPLIFY_STAGE_2 / AMPLIFY_STAGE_1)
        stage3 = stage2 * (AMPLIFY_STAGE_3 / AMPLIFY_STAGE_2)

        flags = {
            "flattening": flat_mean > 0.6,
            "density": dens_mean < 0.02,
            "rhythm": rhy_mean < 5.0
        }

        rows.append({
            "novel_id": nid,
            "flatten_mean": round(flat_mean, 4),
            "density_mean": round(dens_mean, 4),
            "rhythm_mean": round(rhy_mean, 4),
            "amp_stage1": round(stage1, 2),
            "amp_stage2": round(stage2, 2),
            "amp_stage3": round(stage3, 2),
            "chunks_used": chunk_count,
            "flags_total": sum(1 for v in flags.values() if v)
        })

        with open(os.path.join(per_novel_dir, f"NOVEL_{nid}.metrics.json"), "w", encoding="utf-8") as mf:
            json.dump({
                "novel_id": nid,
                "chunks": chunk_count,
                "metrics": {
                    "flattening": flat_vals,
                    "density": dens_vals,
                    "rhythm": rhy_vals
                },
                "flags": flags
            }, mf, ensure_ascii=False, indent=2)

    # -------- CSV --------
    csv_path = os.path.join(out_dir, "quality_matrix.csv")
    if rows:
        with open(csv_path, "w", newline="", encoding="utf-8") as cf:
            writer = csv.DictWriter(cf, fieldnames=rows[0].keys())
            writer.writeheader()
            for r in rows:
                writer.writerow(r)

    # -------- RECEIPT --------
    receipt = {
        "run_id": run_id,
        "status": "PASS" if rows else "EMPTY",
        "novels_total": len(novels),
        "novels_complete": len(rows) - len(insufficient),
        "novels_insufficient": len(insufficient),
        "input_dir": INPUT_DIR,
        "max_novels": MAX_NOVELS,
        "chunks_required": CHUNKS_PER_NOVEL_REQUIRED,
        "started_at": started.isoformat(),
        "ended_at": datetime.now().isoformat(),
        "total_lines": total_lines,
        "notes": "OR-based detection, staged amplification 10/25/50, pathology mining mode"
    }

    with open(os.path.join(out_dir, "receipt.jsonl"), "w", encoding="utf-8") as rf:
        rf.write(json.dumps(receipt, ensure_ascii=False) + "\n")

    print(f"[DONE] {run_id} novels={len(rows)} csv={csv_path}")

if __name__ == "__main__":
    main()
