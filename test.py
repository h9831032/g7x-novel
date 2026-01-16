# C:\g7core\g7_v1\test.py
import sys
import os

def check_env():
    print("\n" + "="*40)
    print(" G7X SYSTEM ENVIRONMENT CHECK ")
    print("="*40)
    print(f"[1] Python Version: {sys.version}")
    print(f"[2] Python Path: {sys.executable}")
    print(f"[3] Current Dir: {os.getcwd()}")
    print("-" * 40)
    print(">>> 결과: 파이썬이 정상적으로 응답하고 있습니다.")
    print("="*40 + "\n")

if __name__ == "__main__":
    check_env()