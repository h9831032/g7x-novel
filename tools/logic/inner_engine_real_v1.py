import os
from google import genai

class InnerEngineReal:
    def __init__(self, api_key=None):
        # 인증 무결성 확보
        self.client = genai.Client(api_key=api_key.strip()) if api_key else None

    def execute(self, task):
        input_path = task.get("input_path")
        
        # [CRITICAL_FIX] 파일 경로만 주지 않고, 내용을 직접 읽어서 제미나이 입에 전달
        try:
            # 해당 경로의 실물 파일이 있는지 확인 후 로드
            if os.path.exists(input_path):
                with open(input_path, "r", encoding='utf-8') as f:
                    content = f.read()
            else:
                content = f"[ERROR] File not found at {input_path}"
        except Exception as e:
            content = f"[ERROR] Reading fail: {str(e)}"

        try:
            # 2.5-Lite 모델 고정 및 실전 프롬프트 배선
            response = self.client.models.generate_content(
                model='gemini-2.5-flash-lite',
                contents=f"다음은 소설 원고의 일부이다. LAW60 제2조(공간적 모순)에 따라 판정하라:\n\n{content}"
            )
            # 영수증 기록을 위해 model 정보 포함하여 반환
            return {"status": "SUCCESS", "model": "gemini-2.5-flash-lite", "api_used": True, "output": response.text}
        except Exception as e:
            return {"status": "FAIL", "api_used": True, "error": str(e)}