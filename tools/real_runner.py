
import os
import json
import requests
import datetime

class RealRunner:
    def __init__(self, api_key):
        self.api_key = api_key
        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.api_key}"
        
    def execute_task(self, prompt):
        headers = {'Content-Type': 'application/json'}
        data = {"contents": [{"parts": [{"text": prompt}]}]}
        
        try:
            start_t = datetime.datetime.now()
            response = requests.post(self.url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            end_t = datetime.datetime.now()
            
            # 토큰 및 비용 계산 (약식)
            content = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', "")
            usage = result.get('usageMetadata', {})
            
            receipt = {
                "timestamp": str(end_t),
                "duration_ms": (end_t - start_t).total_seconds() * 1000,
                "model": "gemini-2.0-flash",
                "tokens_in": usage.get('promptTokenCount', 0),
                "tokens_out": usage.get('candidatesTokenCount', 0),
                "preview": content[:50]
            }
            return True, content, receipt
            
        except Exception as e:
            return False, str(e), {}
