import os, json
import google.generativeai as genai

# [V34.1] LAW60 제1조: 인물 설정 무결성 센서
class LAW60Sensor:
    def __init__(self):
        # 보안 규칙: API 키는 환경변수에서 로드
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("CRITICAL: GEMINI_API_KEY environment variable not set.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def audit_content(self, payload):
        prompt = f"""
        [LAW60 제1조: 인물 설정 무결성 검사]
        아래 소설 내용을 분석하여 등장인물의 설정 오류(이름 바뀜, 성격 급변, 모순적 행동)를 찾아내라.
        단순 키워드가 아닌 문맥적 추론(Semantic Context)으로 판정할 것.

        내용: {payload}

        [출력 규격]
        1. 판정: PASS 또는 FAIL
        2. 사유: (FAIL일 경우 구체적 모순점 기재)
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"SENSOR_ERROR: {str(e)}"