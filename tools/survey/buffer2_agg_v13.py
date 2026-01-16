import os, json, re, csv, time, sys, gc, hashlib
from datetime import datetime

INPUT_DIR = r"C:\g6core\g6_v24\data\umr\chunks"
MAX_NOVELS = 500

# 운영 파라미터 (멈춤 방지)
PROGRESS_EVERY_NOVELS = 10
STALL_SECONDS = 600          # 10분 동안 novel 완료가 0이면 스톨로 판정
MAX_FILE_MB = 200            # 초대형 파일 스킵

# 버퍼2 임계치(임시): count_above 판정선
TH_FLATTEN = 0.70
TH_DENSITY = 0.70
TH_RHYTHM  = 0.70

token_re = re.compile(r"[가-힣A-Za-z0-9]+")

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def safe_float(x, default=0.0):
    try:
        return float(x)
    except:
        return default

def get_tokens(text: str):
    return token_re.findall(text or "")

def percentile(sorted_vals, q: float):
    if not sorted_vals:
        return 0.0
    idx = int(q * (len(sorted_vals) - 1))
    return sorted_vals[idx]

def stats(values, threshold):
    if not values:
        return 0.0, 0.0, 0
    m = sum(values) / len(values)
    sv = sorted(values)
    p95 = percentile(sv, 0.95)
    cnt = sum(1 for v in values if v > threshold)
    return round(m, 4), round(p95, 4), int(cnt)

def sentence_lengths(text: str):
    # 초간단 문장 분리(버퍼2용): . ! ? \n 기준
    if not text:
        return []
    parts = re.split(r"[\.!\?\n]+", text)
    lens = []
    for p in parts:
        tk = get_tokens(p)
        if tk:
            lens.append(len(tk))
    return lens

def file_too_large(path: str) -> bool:
    try:
        return (os.path.getsize(path) / (1024 * 1024)) > MAX_FILE_MB
    except:
        return False

def iter_jsonl_files(root: str):
    for base, _, files in os.walk(root):
        for fn in files:
            if fn.lower().endswith(".jsonl"):
                yield os.path.join(base, fn)

def main():
    run_id = "PHASE18_BUFFER2_V13_" + time.strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join(r"C:\g7core\g7_v1\runs", run_id)
    per_dir = os.path.join(out_dir, "per_novel")
    os.makedirs(per_dir, exist_ok=True)

    # 입력 파일 목록(재현성 위해 정렬)
    files = sorted(list(iter_jsonl_files(INPUT_DIR)))

    # novel 집계 저장소
    # nid -> {"flat":[], "density":[], "rhythm":[], "len_sum":int, "chunks":int, "skips":int}
    acc = {}
    done = []

    last_done_ts = time.time()
    start_ts = time.time()

    print(f">>> [START] run_id={run_id} files={len(files)} input={INPUT_DIR}", flush=True)

    for fp in files:
        if len(done) >= MAX_NOVELS:
            break

        if file_too_large(fp):
            print(f">>> [SKIP_TOO_LARGE] {fp}", file=sys.stderr, flush=True)
            continue

        # utf-8-sig/utf-8 혼재 방지: errors=replace
        try:
            with open(fp, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    if len(done) >= MAX_NOVELS:
                        break
                    if not line.strip():
                        continue

                    try:
                        data = json.loads(line)
                    except:
                        continue

                    nid = data.get("novel_id") or data.get("book_id") or data.get("id")
                    if not nid:
                        continue

                    # 이미 완료된 novel은 스킵(중복 방지)
                    # (완주 우선. 정밀도는 다음 단계에서)
                    if nid in done:
                        continue

                    if nid not in acc:
                        if len(done) + len(acc) >= MAX_NOVELS:
                            continue
                        acc[nid] = {"flat":[], "density":[], "rhythm":[], "len_sum":0, "chunks":0, "skips":0}

                    text = data.get("text", "")
                    tk = get_tokens(text)
                    if not tk:
                        acc[nid]["skips"] += 1
                        continue

                    # 1) flattening: 1 - unique_ratio
                    uniq_ratio = len(set(tk)) / max(1, len(tk))
                    flat = 1.0 - uniq_ratio

                    # 2) density: 토큰 수가 너무 적거나 너무 많으면 비정상 (0~1로 정규화)
                    #    여기서는 간단히 len(tk)/200을 0~1 clamp
                    density = min(1.0, max(0.0, len(tk) / 200.0))

                    # 3) rhythm: 문장 길이 분산(변동이 작으면 리듬 없음=평탄)
                    lens = sentence_lengths(text)
                    if len(lens) <= 1:
                        rhythm = 0.0
                    else:
                        mean_l = sum(lens)/len(lens)
                        var = sum((x-mean_l)**2 for x in lens) / len(lens)
                        # var를 0~1로 대충 정규화: var/50 clamp
                        rhythm = min(1.0, max(0.0, var / 50.0))

                    a = acc[nid]
                    a["flat"].append(flat)
                    a["density"].append(density)
                    a["rhythm"].append(rhythm)
                    a["len_sum"] += len(tk)
                    a["chunks"] += 1

                    # novel 완료 기준: chunks 40개 이상이면 “대표 표본”으로 완료 처리
                    # (500권 완주가 1순위라서, 무한 누적 대신 샘플링형으로 봉인)
                    if a["chunks"] >= 40:
                        mf_mean, mf_p95, mf_cnt = stats(a["flat"], TH_FLATTEN)
                        md_mean, md_p95, md_cnt = stats(a["density"], TH_DENSITY)
                        mr_mean, mr_p95, mr_cnt = stats(a["rhythm"], TH_RHYTHM)

                        row = {
                            "novel_id": nid,
                            "flattening_mean": mf_mean,
                            "flattening_p95": mf_p95,
                            "flattening_count_above": mf_cnt,
                            "density_mean": md_mean,
                            "density_p95": md_p95,
                            "density_count_above": md_cnt,
                            "rhythm_mean": mr_mean,
                            "rhythm_p95": mr_p95,
                            "rhythm_count_above": mr_cnt,
                            "word_count_sum": int(a["len_sum"]),
                            "chunks_used": int(a["chunks"]),
                            "flags_total": int(mf_cnt + md_cnt + mr_cnt),
                        }
                        done.append(nid)
                        done_set = set(done)  # 작은 규모라 허용
                        # per_novel 저장(증거)
                        with open(os.path.join(per_dir, f"NOVEL_{nid}.metrics.json"), "w", encoding="utf-8") as pf:
                            json.dump({"novel_id": nid, "row": row, "skips": a["skips"]}, pf, ensure_ascii=False)

                        yield_row = row
                        # 메모리 해제
                        del acc[nid]
                        gc.collect()

                        if len(done) % PROGRESS_EVERY_NOVELS == 0:
                            print(f">>> [PROGRESS] novels_done={len(done)}/{MAX_NOVELS} last={nid}", flush=True)

                        last_done_ts = time.time()

                    # 스톨 가드: novel 완료가 오랫동안 없으면 FAIL_FAST
                    if (time.time() - last_done_ts) > STALL_SECONDS:
                        print(f"FAIL_FAST: STALL_DETECTED >{STALL_SECONDS}s (last_done={len(done)}) file={fp} nid={nid}", file=sys.stderr, flush=True)
                        raise SystemExit(2)

        except SystemExit:
            raise
        except Exception as e:
            print(f"FAIL_FAST: FILE_READ_ERROR fp={fp} err={repr(e)}", file=sys.stderr, flush=True)
            raise SystemExit(3)

    # CSV 쓰기(집계형)
    out_csv = os.path.join(out_dir, "quality_matrix.csv")
    rows = []
    # per_novel에 저장된 json에서 다시 로드(쓰기 안정성 + 순서 통제)
    for fn in os.listdir(per_dir):
        if fn.endswith(".metrics.json"):
            with open(os.path.join(per_dir, fn), "r", encoding="utf-8") as pf:
                obj = json.load(pf)
                rows.append(obj["row"])
    rows.sort(key=lambda r: r["novel_id"])

    if rows:
        with open(out_csv, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
            f.flush()
            os.fsync(f.fileno())

    # hashes/receipt (증거팩)
    hashes = {
        "quality_matrix.csv": sha256_file(out_csv) if os.path.exists(out_csv) else None,
    }
    with open(os.path.join(out_dir, "hashes.json"), "w", encoding="utf-8") as hf:
        json.dump(hashes, hf, ensure_ascii=False, indent=2)

    receipt = {
        "run_id": run_id,
        "status": "PASS" if len(rows) > 0 else "EMPTY",
        "novels_done": len(rows),
        "input_dir": INPUT_DIR,
        "max_novels": MAX_NOVELS,
        "sys_executable": sys.executable,
        "cwd": os.getcwd(),
        "started_at": datetime.fromtimestamp(start_ts).isoformat(),
        "ended_at": datetime.now().isoformat(),
        "params": {
            "chunks_per_novel": 40,
            "stall_seconds": STALL_SECONDS,
            "max_file_mb": MAX_FILE_MB,
            "thresholds": {"flatten": TH_FLATTEN, "density": TH_DENSITY, "rhythm": TH_RHYTHM},
        }
    }
    with open(os.path.join(out_dir, "receipt.jsonl"), "w", encoding="utf-8") as rf:
        rf.write(json.dumps(receipt, ensure_ascii=False) + "\n")

    print(f">>> [DONE] out_dir={out_dir} rows={len(rows)} csv={out_csv}", flush=True)

if __name__ == "__main__":
    main()
