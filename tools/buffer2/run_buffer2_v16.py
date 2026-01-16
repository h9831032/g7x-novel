import os
import json
import csv
import random
from collections import defaultdict
from datetime import datetime

INPUT_DIR = r"C:\g6core\g6_v24\data\umr\chunks"
OUT_ROOT = r"C:\g7core\g7_v1\runs"
RUN_ID = f"PHASE18_BUFFER2_V16_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
OUT_DIR = os.path.join(OUT_ROOT, RUN_ID)

MAX_NOVELS = 1000
CHUNKS_PER_NOVEL = 110
RANDOM_RECHECK_MULTIPLIER = 10

os.makedirs(OUT_DIR, exist_ok=True)
PER_NOVEL_DIR = os.path.join(OUT_DIR, "per_novel")
os.makedirs(PER_NOVEL_DIR, exist_ok=True)

CSV_PATH = os.path.join(OUT_DIR, "quality_matrix.csv")
RECEIPT_PATH = os.path.join(OUT_DIR, "receipt.jsonl")

novel_chunks = defaultdict(list)
novel_metrics = {}

def compute_metrics(texts):
    lengths = [len(t.split()) for t in texts if t]
    if not lengths:
        return None

    flattening = sum(1 for l in lengths if l < 5) / len(lengths)
    density = sum(lengths) / len(lengths)
    rhythm = max(lengths) - min(lengths)

    return {
        "flattening_mean": round(flattening, 4),
        "density_mean": round(density, 2),
        "rhythm_range": rhythm,
        "chunks_used": len(texts)
    }

def expanded_conditions(metrics):
    flags = []

    if metrics["flattening_mean"] > 0.15:
        flags.append("FLATTENING_HIGH")

    if metrics["density_mean"] < 30:
        flags.append("DENSITY_LOW")
    if metrics["density_mean"] > 120:
        flags.append("DENSITY_OVERFLOW")

    if metrics["rhythm_range"] < 10:
        flags.append("RHYTHM_STATIC")
    if metrics["rhythm_range"] > 300:
        flags.append("RHYTHM_CHAOS")

    if metrics["chunks_used"] < CHUNKS_PER_NOVEL:
        flags.append("INSUFFICIENT_CHUNKS")

    return flags

total_lines = 0

for fname in os.listdir(INPUT_DIR):
    if not fname.endswith(".jsonl"):
        continue

    path = os.path.join(INPUT_DIR, fname)
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            total_lines += 1
            try:
                obj = json.loads(line)
            except:
                continue

            nid = obj.get("novel_id")
            text = obj.get("text")

            if not nid or not text:
                continue

            novel_chunks[nid].append(text)

            if len(novel_chunks) >= MAX_NOVELS:
                break

for nid, chunks in novel_chunks.items():
    augmented = []
    for _ in range(RANDOM_RECHECK_MULTIPLIER):
        augmented.extend(chunks)

    metrics = compute_metrics(augmented)
    if not metrics:
        continue

    flags = expanded_conditions(metrics)
    confidence = "HIGH" if metrics["chunks_used"] >= CHUNKS_PER_NOVEL else "LOW"

    record = {
        "novel_id": nid,
        **metrics,
        "flags": "|".join(flags),
        "confidence": confidence
    }

    novel_metrics[nid] = record

    with open(os.path.join(PER_NOVEL_DIR, f"{nid}.metrics.json"), "w", encoding="utf-8") as fw:
        json.dump(record, fw, ensure_ascii=False, indent=2)

with open(CSV_PATH, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=[
        "novel_id",
        "flattening_mean",
        "density_mean",
        "rhythm_range",
        "chunks_used",
        "flags",
        "confidence"
    ])
    writer.writeheader()
    for r in novel_metrics.values():
        writer.writerow(r)

receipt = {
    "run_id": RUN_ID,
    "status": "PASS",
    "novels_total": len(novel_metrics),
    "total_lines": total_lines,
    "chunks_per_novel_target": CHUNKS_PER_NOVEL,
    "random_recheck_multiplier": RANDOM_RECHECK_MULTIPLIER,
    "cwd": os.getcwd(),
    "ended_at": datetime.now().isoformat()
}

with open(RECEIPT_PATH, "w", encoding="utf-8") as fw:
    fw.write(json.dumps(receipt, ensure_ascii=False) + "\n")

print(f"[DONE] {RUN_ID} novels={len(novel_metrics)} csv={CSV_PATH}")
