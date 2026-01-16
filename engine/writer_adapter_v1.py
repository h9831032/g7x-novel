import time
import hashlib
from google import genai # pip install google-genai 필요

class WriterAdapterV1:
    def __init__(self, api_key="YOUR_GEMINI_API_KEY"):
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-2.0-flash"

    def generate_content(self, objective):
        """진짜 LLM을 호출하여 산출물을 생성합니다."""
        start_time = time.time()
        try:
            # 소설 본문 생성 요청
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=f"G7X Factory Instruction: {objective}\nGenerate content (min 20 lines)."
            )
            text = response.text
            latency = int((time.time() - start_time) * 1000)
            
            return {
                "status": "PASS",
                "content": text,
                "model": self.model_id,
                "usage": {
                    "p": response.usage_metadata.prompt_token_count,
                    "c": response.usage_metadata.candidates_token_count
                },
                "latency_ms": latency,
                "sha1": hashlib.sha1(text.encode("utf-8")).hexdigest()
            }
        except Exception as e:
            return {"status": "FAIL", "error": str(e), "latency_ms": int((time.time() - start_time) * 1000)}