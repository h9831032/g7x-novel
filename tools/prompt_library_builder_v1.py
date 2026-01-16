# C:\g7core\g7_v1\tools\prompt_library_builder_v1.py
import os, time

ROOT = r"C:\g7core\g7_v1"
PROMPT_DIR = os.path.join(ROOT, "queue", "prompts")
STOP_FILE = os.path.join(ROOT, "queue", "STOP.txt")
os.makedirs(PROMPT_DIR, exist_ok=True)

def build():
    print(">>> [PROMPT_GEN] Running until STOP.txt...")
    count = 0
    while not os.path.exists(STOP_FILE) and count < 300:
        # 가상 프롬프트 생성 (1:1 매칭용)
        # 실제 운영 시에는 여기서 정교한 텍스트 생성 로직이 돌아감
        count += 1
        with open(os.path.join(PROMPT_DIR, f"DUMMY_{count}.txt"), "w", encoding="utf-8") as f:
            f.write(f"G7X 분석 타겟 샘플 데이터 {count}\n표준 발화 B 적용 대상.")
        if count % 50 == 0: print(f"  Generated {count} prompts...")
        time.sleep(0.01)

if __name__ == "__main__":
    build()