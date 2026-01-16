import sys

def check_fatal_error(stderr_output):
    fatal_keywords = ["API_KEY_INVALID", "MODEL_NOT_FOUND", "PERMISSION_DENIED"]
    for kw in fatal_keywords:
        if kw in stderr_output:
            print(f"!!! FATAL API ERROR DETECTED: {kw} !!!")
            sys.exit(3) # 지시서 명시 Exitcode=3

if __name__ == "__main__":
    # 이 모듈은 subprocess 결과 처리 시 호출됨
    pass