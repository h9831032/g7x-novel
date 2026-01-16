import os, json, re, csv, time, sys, hashlib, traceback
from datetime import datetime
from collections import defaultdict

INPUT_DIR = r"C:\g6core\g6_v24\data\umr\chunks"

MAX_NOVELS = 1000
CHUNKS_PER_NOVEL = 110

PROGRESS_EVERY_SECONDS = 20
STALL_SECONDS_ANY_UPDATE = 900     # 15분간 어떤 업데이트도 없으면 FAIL
STALL_SECONDS_NO_COMPLETE = 1800   # 30분간 완성 증가 0이면 FAIL

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

def get_tokens(text: str):
    return token_re.findall(text or "")

def sentence_lengths(text: str):
    if not text:
        return []
    parts = re.split(r"[\.!\?\n]+", text)
    lens = []
    for p in parts:
        tk = get_tokens(p)
        if tk:
            lens.append(len(tk))
    return lens

def iter_jsonl_files(root: str):
    for base, _, files in os.walk(root):
        for fn in files:
            if fn.lower().endswith(".jsonl"):
                yield os.path.join(base, fn)

def safe_basename(p: str) -> str:
    try:
        return os.path.basename(p)
    except:
        return ""

def normalize_title(s: str) -> str:
    s = (s or "").strip()
    if not s:
        return ""
    s = re.sub(r"\s+", " ", s)
    s = s.replace("\u00a0", " ")
    return s[:160]

def pick_group_key(data: dict):
    """
    핵심: 이전 EMPTY 원인 = novel_id가 '청크 단위로 분열'되어 chunks_used가 1에서 멈춤.
    그래서 group_key(권 식별자)를 더 상위 필드로 교정한다.
    """
    # 1) 확실한 상위 키 후보들
    candidates = [
        ("series_id", data.get("series_id")),
        ("novel_root_id", data.get("novel_root_id")),
        ("novel_group_id", data.get("novel_group_id")),
        ("work_id", data.get("work_id")),
        ("book_id", data.get("book_id")),
        ("title", data.get("title")),
        ("novel_title", data.get("novel_title")),
        ("book_title", data.get("book_title")),
        ("source_title", data.get("source_title")),
        ("origin_title", data.get("origin_title")),
    ]

    for src, v in candidates:
        if v is None:
            continue
        if isinstance(v, (int, float)):
            v = str(v)
        if isinstance(v, str):
            vv = normalize_title(v)
            if vv:
                return vv, src

    # 2) 파일/경로가 있으면 그걸로 그룹핑(청크가 같은 원본에서 왔는지)
    for k in ("source_file", "file", "filepath", "path", "src_path", "origin_path"):
        v = data.get(k)
        if isinstance(v, str) and v.strip():
            b = safe_basename(v.strip())
            if b:
                # jsonl 이름(장르 파일명)로 묶이면 망하니까, 가능한 한 '소설 파일명' 느낌만 사용
                # 예: "NOVEL_xxx.txt" 같은 경우만 채택
                if re.search(r"novel|book|raw|txt|chapter", b, re.IGNORECASE):
                    return b[:180], f"path:{k}"

    # 3) 마지막: novel_id
    nid = data.get("novel_id") or data.get("id")
    if nid is None:
        return None, "missing"

    if not isinstance(nid, str):
        nid = str(nid)

    # 3-1) 흔한 분열 패턴 교정(예: RAW_00da3c31 같은 청크성 ID)
    # 여기서 무리한 가정은 금지. 대신 "prefix"가 있으면 prefix로만 묶는 최소 휴리스틱만 적용.
    m = re.match(r"^([A-Za-z]+)_([0-9a-f]{8,})$", nid.strip())
    if m:
        prefix = m.group(1)
        # prefix만 쓰면 너무 뭉뚱그려질 수 있으니 "prefix+첫2바이트" 정도로 완화
        hexpart = m.group(2)
        return f"{prefix}_{hexpart[:2]}", "novel_id:heuristic_prefix2"

    return nid.strip(), "novel_id"

class P2Quantile:
    def __init__(self, q: float):
        self.q = q
        self.n = 0
        self.init = []
        self.np = [0.0]*5
        self.ni = [0]*5
        self.dn = [0.0]*5
        self.qv = [0.0]*5

    def add(self, x: float):
        x = float(x)
        if self.n < 5:
            self.init.append(x)
            self.n += 1
            if self.n == 5:
                self.init.sort()
                self.qv = self.init[:]
                self.ni = [1,2,3,4,5]
                self.np = [1.0,
                           1.0 + 2.0*self.q,
                           1.0 + 4.0*self.q,
                           3.0 + 2.0*self.q,
                           5.0]
                self.dn = [0.0,
                           self.q/2.0,
                           self.q,
                           (1.0+self.q)/2.0,
                           1.0]
            return

        if x < self.qv[0]:
            self.qv[0] = x
            k = 0
        elif x < self.qv[1]:
            k = 0
        elif x < self.qv[2]:
            k = 1
        elif x < self.qv[3]:
            k = 2
        elif x < self.qv[4]:
            k = 3
        else:
            self.qv[4] = x
            k = 3

        for i in range(k+1, 5):
            self.ni[i] += 1
        for i in range(5):
            self.np[i] += self.dn[i]
        self.n += 1

        for i in (1,2,3):
            d = self.np[i] - self.ni[i]
            if (d >= 1.0 and (self.ni[i+1] - self.ni[i]) > 1) or (d <= -1.0 and (self.ni[i-1] - self.ni[i]) < -1):
                di = 1 if d >= 1.0 else -1

                qi = self.qv[i]
                qip1 = self.qv[i+1]
                qim1 = self.qv[i-1]
                nip1 = self.ni[i+1]
                ni = self.ni[i]
                nim1 = self.ni[i-1]

                num = di * (ni - nim1 + di) * (qip1 - qi) / (nip1 - ni) + di * (nip1 - ni - di) * (qi - qim1) / (ni - nim1)
                qn = qi + num / (nip1 - nim1)

                if qn <= qim1 or qn >= qip1:
                    qn = qi + di * (self.qv[i+di] - qi) / (self.ni[i+di] - ni)

                self.qv[i] = qn
                self.ni[i] += di

    def value(self) -> float:
        if self.n == 0:
            return 0.0
        if self.n < 5:
            s = sorted(self.init)
            idx = int(self.q * (len(s) - 1)) if len(s) > 1 else 0
            return float(s[idx])
        return float(self.qv[2])

class Agg:
    __slots__ = ("count","sum_flat","sum_density","sum_rhythm",
                 "p95_flat","p95_density","p95_rhythm",
                 "cnt_above_flat","cnt_above_density","cnt_above_rhythm",
                 "word_sum","chunks","skips","complete")
    def __init__(self):
        self.count = 0
        self.sum_flat = 0.0
        self.sum_density = 0.0
        self.sum_rhythm = 0.0

        self.p95_flat = P2Quantile(0.95)
        self.p95_density = P2Quantile(0.95)
        self.p95_rhythm = P2Quantile(0.95)

        self.cnt_above_flat = 0
        self.cnt_above_density = 0
        self.cnt_above_rhythm = 0

        self.word_sum = 0
        self.chunks = 0
        self.skips = 0
        self.complete = False

    def add(self, flat, density, rhythm, word_count):
        self.count += 1
        self.sum_flat += flat
        self.sum_density += density
        self.sum_rhythm += rhythm

        self.p95_flat.add(flat)
        self.p95_density.add(density)
        self.p95_rhythm.add(rhythm)

        if flat > TH_FLATTEN: self.cnt_above_flat += 1
        if density > TH_DENSITY: self.cnt_above_density += 1
        if rhythm > TH_RHYTHM: self.cnt_above_rhythm += 1

        self.word_sum += int(word_count)
        self.chunks += 1
        if self.chunks >= CHUNKS_PER_NOVEL:
            self.complete = True

    def row(self, group_id: str, group_src: str):
        mean_flat = self.sum_flat / self.count if self.count else 0.0
        mean_density = self.sum_density / self.count if self.count else 0.0
        mean_rhythm = self.sum_rhythm / self.count if self.count else 0.0
        insufficient = 0 if self.complete else 1
        return {
            "group_id": group_id,
            "group_key_source": group_src,

            "flattening_mean": round(mean_flat, 4),
            "flattening_p95": round(self.p95_flat.value(), 4),
            "flattening_count_above": int(self.cnt_above_flat),

            "density_mean": round(mean_density, 4),
            "density_p95": round(self.p95_density.value(), 4),
            "density_count_above": int(self.cnt_above_density),

            "rhythm_mean": round(mean_rhythm, 4),
            "rhythm_p95": round(self.p95_rhythm.value(), 4),
            "rhythm_count_above": int(self.cnt_above_rhythm),

            "word_count_sum": int(self.word_sum),
            "chunks_used": int(self.chunks),
            "flags_total": int(self.cnt_above_flat + self.cnt_above_density + self.cnt_above_rhythm),
            "insufficient_chunks": int(insufficient),
        }

def compute_metrics(text: str):
    tk = get_tokens(text)
    if not tk:
        return None
    uniq_ratio = len(set(tk)) / max(1, len(tk))
    flat = 1.0 - uniq_ratio
    density = min(1.0, max(0.0, len(tk) / 200.0))

    lens = sentence_lengths(text)
    if len(lens) <= 1:
        rhythm = 0.0
    else:
        mean_l = sum(lens) / len(lens)
        var = sum((x - mean_l)**2 for x in lens) / len(lens)
        rhythm = min(1.0, max(0.0, var / 50.0))

    return flat, density, rhythm, len(tk)

def main():
    run_id = "PHASE18_BUFFER2_V15_4_" + time.strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join(r"C:\g7core\g7_v1\runs", run_id)
    per_dir = os.path.join(out_dir, "per_novel")
    os.makedirs(per_dir, exist_ok=True)

    files = sorted(list(iter_jsonl_files(INPUT_DIR)))

    chosen_groups = []
    chosen_set = set()
    aggs = {}

    group_src_stats = defaultdict(int)

    start_ts = time.time()
    last_progress_ts = time.time()
    last_any_update_ts = time.time()
    last_complete_ts = time.time()

    total_lines = 0
    total_bad_json = 0
    total_no_key = 0
    total_empty_text = 0
    total_skipped_text = 0

    last_fp = ""
    last_gid = ""
    complete_count = 0

    print(f">>> [START] run_id={run_id} files={len(files)} input={INPUT_DIR} max_groups={MAX_NOVELS} chunks_per_group={CHUNKS_PER_NOVEL}", flush=True)

    try:
        for fp in files:
            last_fp = fp
            with open(fp, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    total_lines += 1
                    if not line.strip():
                        continue

                    try:
                        data = json.loads(line)
                    except:
                        total_bad_json += 1
                        continue

                    gid, gsrc = pick_group_key(data)
                    if not gid:
                        total_no_key += 1
                        continue

                    last_gid = gid
                    group_src_stats[gsrc] += 1

                    if gid not in chosen_set:
                        if len(chosen_groups) >= MAX_NOVELS:
                            continue
                        chosen_groups.append((gid, gsrc))
                        chosen_set.add(gid)
                        aggs[gid] = Agg()
                        last_any_update_ts = time.time()

                    agg = aggs.get(gid)
                    if agg is None:
                        continue
                    if agg.complete:
                        continue

                    text = data.get("text", "")
                    if not text:
                        total_empty_text += 1
                        agg.skips += 1
                        continue

                    m = compute_metrics(text)
                    if m is None:
                        total_skipped_text += 1
                        agg.skips += 1
                        continue

                    flat, density, rhythm, wc = m
                    before = agg.complete
                    agg.add(flat, density, rhythm, wc)
                    last_any_update_ts = time.time()

                    if (not before) and agg.complete:
                        complete_count += 1
                        last_complete_ts = time.time()

                    now = time.time()
                    if (now - last_progress_ts) >= PROGRESS_EVERY_SECONDS:
                        print(
                            f">>> [PROGRESS] lines={total_lines} chosen={len(chosen_groups)}/{MAX_NOVELS} complete={complete_count}/{MAX_NOVELS} "
                            f"file={os.path.basename(fp)} last_group={str(last_gid)[:60]} bad_json={total_bad_json} no_key={total_no_key}",
                            flush=True
                        )
                        last_progress_ts = now

                    if (now - last_any_update_ts) > STALL_SECONDS_ANY_UPDATE:
                        msg = f"FAIL_FAST: STALL_ANY_UPDATE >{STALL_SECONDS_ANY_UPDATE}s lines={total_lines} chosen={len(chosen_groups)} complete={complete_count} file={fp} last_group={last_gid}"
                        print(msg, file=sys.stderr, flush=True)
                        raise SystemExit(2)

                    if (now - last_complete_ts) > STALL_SECONDS_NO_COMPLETE:
                        msg = f"FAIL_FAST: STALL_NO_COMPLETE >{STALL_SECONDS_NO_COMPLETE}s lines={total_lines} chosen={len(chosen_groups)} complete={complete_count} file={fp} last_group={last_gid}"
                        print(msg, file=sys.stderr, flush=True)
                        raise SystemExit(2)

    except SystemExit:
        raise
    except Exception as e:
        print(f"FAIL_FAST: UNHANDLED_ERROR err={repr(e)} file={last_fp} last_group={last_gid}", file=sys.stderr, flush=True)
        print(traceback.format_exc(), file=sys.stderr, flush=True)
        raise SystemExit(3)

    complete_rows = []
    insufficient_rows = []

    for gid, gsrc in chosen_groups:
        agg = aggs.get(gid)
        if agg is None:
            continue
        row = agg.row(gid, gsrc)

        safe_id = re.sub(r"[^A-Za-z0-9_\-\.]+", "_", gid)[:120]
        out_p = os.path.join(per_dir, f"GROUP_{safe_id}.metrics.json")
        with open(out_p, "w", encoding="utf-8") as pf:
            json.dump(
                {
                    "group_id": gid,
                    "group_key_source": gsrc,
                    "chunks_used": int(agg.chunks),
                    "skips": int(agg.skips),
                    "complete": bool(agg.complete),
                    "chunks_per_group_required": int(CHUNKS_PER_NOVEL),
                    "row": row
                },
                pf,
                ensure_ascii=False
            )

        if agg.complete:
            complete_rows.append(row)
        else:
            insufficient_rows.append(row)

    out_csv = os.path.join(out_dir, "quality_matrix.csv")
    out_ins_csv = os.path.join(out_dir, "insufficient_groups.csv")

    if complete_rows:
        with open(out_csv, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(complete_rows[0].keys()))
            w.writeheader()
            w.writerows(complete_rows)
            f.flush()
            os.fsync(f.fileno())
    else:
        with open(out_csv, "w", encoding="utf-8-sig", newline="") as f:
            f.write("group_id,insufficient_chunks\n")

    if insufficient_rows:
        with open(out_ins_csv, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(insufficient_rows[0].keys()))
            w.writeheader()
            w.writerows(insufficient_rows)
            f.flush()
            os.fsync(f.fileno())

    hashes = {
        "quality_matrix.csv": sha256_file(out_csv) if os.path.exists(out_csv) else None,
        "insufficient_groups.csv": sha256_file(out_ins_csv) if os.path.exists(out_ins_csv) else None,
    }
    with open(os.path.join(out_dir, "hashes.json"), "w", encoding="utf-8") as hf:
        json.dump(hashes, hf, ensure_ascii=False, indent=2)

    # group_key_source 통계(어떤 키로 묶였는지)
    gstats_sorted = sorted(group_src_stats.items(), key=lambda x: x[1], reverse=True)
    gstats_obj = {k: int(v) for k, v in gstats_sorted[:50]}

    receipt = {
        "run_id": run_id,
        "status": "PASS" if len(complete_rows) > 0 else "EMPTY",
        "groups_chosen": int(len(chosen_groups)),
        "groups_complete": int(len(complete_rows)),
        "groups_insufficient": int(len(insufficient_rows)),
        "input_dir": INPUT_DIR,
        "max_groups": int(MAX_NOVELS),
        "chunks_per_group_required": int(CHUNKS_PER_NOVEL),
        "sys_executable": sys.executable,
        "cwd": os.getcwd(),
        "started_at": datetime.fromtimestamp(start_ts).isoformat(),
        "ended_at": datetime.now().isoformat(),
        "counters": {
            "total_lines": int(total_lines),
            "bad_json": int(total_bad_json),
            "no_group_key": int(total_no_key),
            "empty_text": int(total_empty_text),
            "skipped_text": int(total_skipped_text),
        },
        "group_key_source_stats_top50": gstats_obj,
        "thresholds": {
            "flatten": float(TH_FLATTEN),
            "density": float(TH_DENSITY),
            "rhythm": float(TH_RHYTHM),
        },
        "notes": "NO_SAMPLING=1 NO_SKIP=1; GROUP_KEY_FIX=1; complete_requires_chunks=110; complete_rows_only_in_main_csv=1"
    }
    with open(os.path.join(out_dir, "receipt.jsonl"), "w", encoding="utf-8") as rf:
        rf.write(json.dumps(receipt, ensure_ascii=False) + "\n")

    print(f">>> [DONE] out_dir={out_dir} chosen={len(chosen_groups)} complete={len(complete_rows)} insufficient={len(insufficient_rows)} csv_exists={os.path.exists(out_csv)}", flush=True)

if __name__ == "__main__":
    main()
