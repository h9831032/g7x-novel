import os
import time
import re
import google.generativeai as genai

class WriterAdapter:
    def __init__(self):
        # [CRITICAL FIX] 형님이 주신 키를 코드에 직접 박았습니다. (환경변수 무시)
        # 보안상 나중에는 환경변수로 빼시는 게 좋지만, 지금은 작동이 우선입니다.
        self.api_key = "AIzaSyBreX9jWMmxzCD7aySlpZ2I3PJUmcY1AgY"
        
        # 혹시 모르니 공백 제거
        self.api_key = self.api_key.strip()
        
        if not self.api_key:
            raise RuntimeError("CRITICAL: GEMINI_API_KEY is empty.")
        
        # 구형 라이브러리 경고 무시
        genai.configure(api_key=self.api_key)
        
        # 형님 지시하신 2.5 모델 (만약 안되면 1.5로 자동 전환)
        self.model_name = "models/gemini-2.5-flash"

    def generate(self, prompt):
        start_time = time.time()
        try:
            # 2.5 모델 호출 시도
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(prompt)
            
            latency_ms = int((time.time() - start_time) * 1000)
            return {
                "status": "PASS",
                "content": response.text,
                "latency_ms": latency_ms,
                "model": self.model_name
            }
        except Exception as e:
            # 2.5 실패 시 1.5로 비상 전환
            err_msg = str(e)
            print(f"[WARNING] Model {self.model_name} failed. Retrying with 1.5... ({err_msg})")
            
            try:
                fallback = "models/gemini-1.5-flash"
                model = genai.GenerativeModel(fallback)
                response = model.generate_content(prompt)
                latency_ms = int((time.time() - start_time) * 1000)
                return {"status": "PASS", "content": response.text, "latency_ms": latency_ms, "model": fallback}
            except Exception as e2:
                return {"status": "FAIL", "error": str(e2), "latency_ms": int((time.time() - start_time) * 1000)}