import os, json, uuid

ROOT = r"C:\g7core\g7_v1"
OUT_DIR = os.path.join(ROOT, "queue", "work_orders")
PROMPT_DIR = os.path.join(ROOT, "queue", "prompts")

def generate():
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(PROMPT_DIR, exist_ok=True)
    
    print(f">>> [GEN] Creating 192 orders in {OUT_DIR}...")
    
    for i in range(192):
        o_id = str(uuid.uuid4())
        # [핵심] 프롬프트 파일명 명확화
        p_filename = f"PROMPT_{i+1:03d}.txt" 
        p_path = os.path.join(PROMPT_DIR, p_filename)
        
        # [방어] 프롬프트 파일이 실제로 없으면 만든다 (0바이트 방지 내용 포함)
        if not os.path.exists(p_path):
            with open(p_path, "w", encoding="utf-8") as f:
                f.write(f"G7X_AUTO_GENERATED_PROMPT_{i+1}: This is a dummy prompt for validation.")
        
        order = {
            "order_id": o_id,
            "prompt_path": p_path, # 절대 경로 박제
            "created_at": str(os.times())
        }
        
        with open(os.path.join(OUT_DIR, f"ORD_{o_id}.json"), "w", encoding="utf-8") as f:
            json.dump(order, f, indent=4)
            
    print(f">>> [GEN] Done. 192 Orders + Prompts ready.")

if __name__ == "__main__":
    generate()