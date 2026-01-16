import sys
import os
import subprocess

def sync_environment():
    """
    파이참 가상환경(.venv)과 터미널 실행 환경을 강제 일치시키는 플러그인
    """
    venv_python = r"C:\Users\00\PycharmProjects\PythonProject\.venv\Scripts\python.exe"
    current_python = sys.executable

    print(f"G7X_MSG: [ENV_CHECK] Current: {current_python}")
    
    if current_python.lower() != venv_python.lower():
        print(f"G7X_MSG: [ENV_MISMATCH] 파이참 venv로 경로를 재배선합니다.")
        # 가상환경의 site-packages를 sys.path에 강제 삽입
        venv_site_packages = os.path.join(os.path.dirname(os.path.dirname(venv_python)), 'Lib', 'site-packages')
        if venv_site_packages not in sys.path:
            sys.path.insert(0, venv_site_packages)
        print(f"G7X_MSG: [ENV_FIXED] Library path linked: {venv_site_packages}")
    else:
        print(f"G7X_MSG: [OK] Environment Synchronized.")

if __name__ == "__main__":
    sync_environment()