import os, json, glob, sys

ROOT = r"C:\g7core\g7_v1"
ORDER_DIR = os.path.join(ROOT, "queue", "work_orders")
AUDIT_DIR = os.path.join(ROOT, "queue", "audit")
os.makedirs(AUDIT_DIR, exist_ok=True)

def audit():
    orders = glob.glob(os.path.join(ORDER_DIR, "*.json"))
    missing_p = []
    for op in orders:
        with open(op, 'r', encoding='utf-8') as f:
            data = json.load(f)
            p_path = data.get("prompt_path", "")
            if not os.path.exists(p_path): missing_p.append(p_path)
            
    with open(os.path.join(AUDIT_DIR, "missing_prompts.txt"), "w") as f:
        f.write("\n".join(missing_p))
    
    summary = {"total_orders": len(orders), "missing_prompts": len(missing_p)}
    with open(os.path.join(AUDIT_DIR, "audit_summary.json"), "w") as f:
        json.dump(summary, f, indent=4)
    print(f">>> Audit Done. Missing Prompts: {len(missing_p)}")

if __name__ == "__main__":
    audit()