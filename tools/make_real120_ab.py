import os

def make_orders():
    root = r"C:\g7core\g7_v1\GPTORDER"
    os.makedirs(root, exist_ok=True)

    # A120 생성
    with open(os.path.join(root, "REAL120_A.txt"), "w", encoding="utf-8") as f:
        for i in range(1, 121):
            f.write(f"TASK_V2|payload=REAL_{i:03d}\n")

    # B120 생성
    with open(os.path.join(root, "REAL120_B.txt"), "w", encoding="utf-8") as f:
        for i in range(121, 241):
            f.write(f"TASK_V2|payload=REAL_{i:03d}\n")

    print(f"   G7X_MSG: [SUCCESS] A120, B120 주문서 배차 완료.")

if __name__ == "__main__":
    make_orders()