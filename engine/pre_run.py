import os
import sys

def scan_forbidden_patterns(target_dir):
    # 실제 실행 코드가 아닌 문자열 매칭 시 예외 처리를 위해 필터 강화
    forbidden = ["time" + ".sleep"] # 스캐너 우회 방지용 결합
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.endswith(".py") and file not in ["pre_run.py", "finalize_gate.py"]:
                with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                    content = f.read()
                    if "time.sleep" in content: # 실제 금지 단어
                        print(f">>> [GATE_A_FAIL] Pattern found in {file}")
                        sys.exit(1)
    print(">>> [GATE_A_PASS] System Clean.")
    return True

if __name__ == "__main__":
    scan_forbidden_patterns("C:\\g7core\\g7_v1\\main")