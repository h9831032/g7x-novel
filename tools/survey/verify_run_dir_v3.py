import os, json, sys, csv
def verify(run_dir):
    receipt_p = os.path.join(run_dir, "receipt.json")
    with open(receipt_p, "r") as f: receipt = json.load(f)
    if receipt["rows"] != 120: raise Exception("Row mismatch")
    print("FINAL_STATUS: PASS")
if __name__ == "__main__": verify(sys.argv[1])
