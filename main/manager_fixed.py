"""
G7X Manager - Main Entry Point (실엔진 연결 완료)
- 제미나이 API 직접 호출 (models/gemini-2.0-flash-exp)
- 증거팩 자동 생성 (evidence_writer 통합)
- FAIL_FAST (실엔진 없으면 즉시 실패)
- [FIX] 거짓합격(exitcode=0) 제거: done_missions != expected_missions → exitcode=1
- [FIX] reason_code 추가: 왜 멈췄는지 blackbox에 기록
"""

import os
import sys
import json
import argparse
import traceback
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# 증거팩 작성기 임포트
sys.path.insert(0, str(Path(__file__).parent.parent / "engine"))
from evidence_writer import EvidenceWriter

# 제미나이 API 설정
GEMINI_API_KEY = "AIzaSyBreX9jWMmxzCD7aySlpZ2I3PJUmcY1AgY"
GEMINI_MODEL = "models/gemini-2.0-flash-exp"


class TeeWriter:
    """표준 출력을 파일과 콘솔 동시 기록"""
    
    def __init__(self, original, file_path: Path):
        self.original = original
        self.file = open(file_path, "w", encoding="utf-8")
    
    def write(self, text):
        self.original.write(text)
        self.file.write(text)
        self.file.flush()
    
    def flush(self):
        self.original.flush()
        self.file.flush()


class BasicEngineAdapter:
    """제미나이 API 직접 호출 어댑터"""
    
    def __init__(self):
        self.api_key = GEMINI_API_KEY
        self.model = GEMINI_MODEL
        
        # API 키 검증
        if not self.api_key:
            raise RuntimeError("[FAIL_FAST] GEMINI_API_KEY not configured")
    
    def execute_real_mission(self, mission_order: str, output_dir: Path) -> Dict[str, Any]:
        """
        실제 미션 실행 (제미나이 API 호출)
        """
        try:
            import requests
            
            url = f"https://generativelanguage.googleapis.com/v1beta/{self.model}:generateContent"
            headers = {"Content-Type": "application/json"}
            
            payload = {
                "contents": [{
                    "parts": [{"text": mission_order}]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 2048
                }
            }
            
            response = requests.post(
                f"{url}?key={self.api_key}",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                return {
                    "status": "API_ERROR",
                    "order": mission_order,
                    "error": f"HTTP {response.status_code}",
                    "response_text": response.text[:500]
                }
            
            data = response.json()
            
            # 응답 파싱
            content = ""
            if "candidates" in data and len(data["candidates"]) > 0:
                candidate = data["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    parts = candidate["content"]["parts"]
                    content = "".join(p.get("text", "") for p in parts)
            
            result = {
                "status": "SUCCESS",
                "order": mission_order,
                "content": content,
                "raw_response": data
            }
            
            return result
            
        except ImportError:
            return {
                "status": "FAIL_FAST",
                "order": mission_order,
                "error": "requests module not installed (pip install requests)"
            }
        except Exception as e:
            return {
                "status": "ERROR",
                "order": mission_order,
                "error": str(e),
                "traceback": traceback.format_exc()
            }


class RunManager:
    """RUN 실행 관리자"""
    
    def __init__(self, ssot_root: Path):
        self.ssot_root = Path(ssot_root)
        self.runs_dir = self.ssot_root / "runs"
        self.runs_dir.mkdir(exist_ok=True)
        
        # RUN 폴더 생성
        run_id = datetime.now().strftime("RUN_%Y%m%d_%H%M%S_%f")[:26]
        self.run_path = self.runs_dir / run_id
        self.run_path.mkdir(exist_ok=True)
        
        # 증거팩 작성기 초기화
        self.evidence = EvidenceWriter(self.run_path)
        
        # stdout/stderr 저장 설정
        self.stdout_path = self.run_path / "stdout_manager.txt"
        self.stderr_path = self.run_path / "stderr_manager.txt"
        
        # 표준 출력 리다이렉트
        sys.stdout = TeeWriter(sys.stdout, self.stdout_path)
        sys.stderr = TeeWriter(sys.stderr, self.stderr_path)
        
        print(f"[MANAGER] RUN CREATED: {self.run_path}")
        print(f"TARGET_RUN_PATH:{self.run_path}")  # Guard가 이걸로 경로 추출
        
        # 실엔진 초기화
        try:
            self.engine = BasicEngineAdapter()
            print("[MANAGER] Basic Engine initialized (Gemini API)")
        except Exception as e:
            print(f"[FAIL_FAST] Basic Engine initialization failed: {e}")
            raise
    
    def load_orders(self, order_path: Path) -> List[str]:
        """오더 파일 로딩 (한 줄씩 미션)"""
        if not order_path.exists():
            raise FileNotFoundError(f"Order file not found: {order_path}")
        
        with open(order_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        
        print(f"[MANAGER] Loaded {len(lines)} orders from {order_path}")
        return lines
    
    def execute_mission(self, mission_id: str, mission_order: str) -> Dict[str, Any]:
        """
        개별 미션 실행 (실제 API 호출)
        """
        
        print(f"[MISSION] Executing: {mission_id} | Order: {mission_order[:50]}...")
        
        # 실엔진 호출
        result = self.engine.execute_real_mission(
            mission_order=mission_order,
            output_dir=self.run_path / "api_raw"
        )
        
        # FAIL_FAST 체크
        if result.get("status") == "FAIL_FAST":
            print(f"[FAIL_FAST] Mission {mission_id}: {result.get('error')}")
            raise RuntimeError(f"FAIL_FAST: {result.get('error')}")
        
        # 결과에 mission_id 추가
        result["mission_id"] = mission_id
        result["timestamp"] = datetime.now().isoformat()
        
        # api_raw 저장
        api_raw_dir = self.run_path / "api_raw"
        api_raw_dir.mkdir(exist_ok=True)
        api_raw_file = api_raw_dir / f"{mission_id}.json"
        with open(api_raw_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        # 증거팩 기록
        self.evidence.write_mission_receipt(mission_id, result)
        
        # missions 폴더에도 복사 (기존 도구 호환용)
        missions_dir = self.run_path / "missions"
        missions_dir.mkdir(exist_ok=True)
        
        mission_file = missions_dir / f"{mission_id}.json"
        with open(mission_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"[MISSION] {mission_id} status: {result.get('status')}")
        
        return result
    
    def run(self, order_path: Path):
        """
        메인 실행 루프
        [FIX] 거짓합격 제거: done_missions != expected_missions → exitcode=1
        [FIX] reason_code 기록 추가
        """
        exitcode = 0
        orders = []
        done_missions = 0
        api_error_count = 0
        reason_code = "UNKNOWN"
        
        try:
            # 오더 로딩
            orders = self.load_orders(order_path)
            expected_missions = len(orders)
            
            print(f"[MANAGER] Starting {expected_missions} missions...")
            
            # 미션 실행 루프
            for idx, order in enumerate(orders, 1):
                mission_id = f"mission_{idx:04d}"
                
                try:
                    result = self.execute_mission(mission_id, order)
                    
                    # [FIX] API_ERROR 카운트
                    if result.get("status") == "API_ERROR":
                        api_error_count += 1
                        print(f"[API_ERROR] Mission {mission_id}: {result.get('error')}")
                    elif result.get("status") == "SUCCESS":
                        done_missions += 1
                    else:
                        # ERROR 등 다른 상태
                        pass
                        
                except RuntimeError as e:
                    # FAIL_FAST: 즉시 중단
                    print(f"[FAIL_FAST] Stopping due to: {e}")
                    reason_code = "FAIL_FAST"
                    exitcode = 1
                    break
                except Exception as e:
                    print(f"[ERROR] Mission {mission_id} failed: {e}")
                    traceback.print_exc()
                    reason_code = "BREAK_ON_EXCEPTION"
                    exitcode = 1
                    break  # [FIX] 예외 발생 시 중단 (거짓합격 방지)
            else:
                # 루프가 break 없이 완료된 경우
                reason_code = "ORDER_EOF"
            
            print(f"[MANAGER] Loop finished: done={done_missions}, expected={expected_missions}, api_errors={api_error_count}")
            
            # [FIX] 거짓합격 방지: done != expected → FAIL
            if done_missions != expected_missions:
                print(f"[FAIL] done_missions({done_missions}) != expected_missions({expected_missions})")
                exitcode = 1
                if reason_code == "ORDER_EOF":
                    reason_code = "INCOMPLETE_MISSIONS"
            
            # [FIX] API_ERROR 1개라도 있으면 FAIL
            if api_error_count > 0:
                print(f"[FAIL] api_error_count={api_error_count} > 0")
                exitcode = 1
                if reason_code == "ORDER_EOF":
                    reason_code = "API_ERROR"
            
        except FileNotFoundError as e:
            print(f"[FATAL] Order file not found: {e}")
            reason_code = "ORDER_FILE_NOT_FOUND"
            exitcode = 2
        except Exception as e:
            print(f"[FATAL] Manager execution failed: {e}")
            traceback.print_exc()
            reason_code = "FATAL_EXCEPTION"
            exitcode = 2
        
        finally:
            # 증거팩 최종 생성 (무조건 실행)
            print("[MANAGER] Finalizing evidence pack...")
            expected = len(orders) if orders else 0
            
            # [FIX] finalize에 추가 정보 전달
            self.evidence.finalize(
                exitcode=exitcode, 
                total_missions=expected,
                done_missions=done_missions,
                api_error_count=api_error_count,
                reason_code=reason_code
            )
            
            print(f"[MANAGER] RUN COMPLETE: exitcode={exitcode}, reason={reason_code}")
            print(f"TARGET_RUN_PATH:{self.run_path}")
        
        return exitcode


def main():
    parser = argparse.ArgumentParser(description="G7X Manager")
    parser.add_argument("--order_path", required=True, help="Order file path")
    parser.add_argument("--ssot_root", default="C:\\g7core\\g7_v1", help="SSOT root path")
    
    args = parser.parse_args()
    
    # SSOT_ROOT 경로 확인
    ssot_root = Path(args.ssot_root)
    if not ssot_root.exists():
        print(f"[ERROR] SSOT_ROOT not found: {ssot_root}")
        sys.exit(1)
    
    # 오더 파일 경로 처리
    order_path = Path(args.order_path)
    if not order_path.is_absolute():
        # GPTORDER 폴더 기준으로 해석
        order_path = ssot_root / "GPTORDER" / args.order_path
    
    # 실행
    try:
        manager = RunManager(ssot_root)
        exitcode = manager.run(order_path)
        sys.exit(exitcode)
    except Exception as e:
        print(f"[FATAL] Manager failed to start: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
