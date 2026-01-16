import os, sys, json, argparse

def main():
    parser = argparse.ArgumentParser()
    # 메인 엔진이 실행된 결과 폴더 경로를 인자로 받습니다.
    parser.add_argument("--run_dir", required=True, help="Path to the RUN_XXXX directory")
    args = parser.parse_args()

    receipt_path = os.path.join(args.run_dir, "audit_receipt.jsonl")
    if not os.path.exists(receipt_path):
        print(f"[FAIL] Receipt file not found: {receipt_path}")
        sys.exit(2)

    drift_casebook = []
    with open(receipt_path, "r", encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)
            # 판정이 흔들렸거나(v_drift) 다수결로 해결된(resolved) 건만 추출
            if data.get("v_drift") or data.get("resolved"):
                drift_casebook.append(data)

    casebook_path = os.path.join(args.run_dir, "drift_casebook.jsonl")
    with open(casebook_path, "w", encoding="utf-8") as f:
        for d in drift_casebook:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")

    print(f"\n" + "="*50)
    print(f" [@] CASEBOOK GENERATED: {casebook_path}")
    print(f" [@] TOTAL INCIDENTS FOUND: {len(drift_casebook)}")
    print("="*50 + "\n")

if __name__ == "__main__":
    main()