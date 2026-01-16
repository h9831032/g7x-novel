"""
G7X Manager - Main Entry Point (실엔진 연결 완료)
- 제미나이 API 직접 호출 (models/gemini-2.0-flash-exp)
- 증거팩 자동 생성 (evidence_writer 통합)
- FAIL_FAST (실엔진 없으면 즉시 실패)
- [FIX 2026-01-12] 거짓합격 완전 제거
  - done_missions != expected_missions → exitcode=1
  - api_error_count > 0 → exitcode=1
  - reason_code 기록 추가
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
        표준 라이브러리(urllib)만 사용
        """
        try:
            import urllib.request
            import urllib.error
            
            url = f"https://generativelanguage.googleapis.com/v1beta/{self.model}:generateContent?key={self.api_key}"
            
            payload = {
                "contents": [{
                    "parts": [{"text": mission_order}]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 2048
                }
            }
            
            # JSON 인코딩
            data_bytes = json.dumps(payload).encode('utf-8')
            
            # HTTP 요청
            req = urllib.request.Request(
                url,
                data=data_bytes,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            
            # API 호출
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode('utf-8'))
            
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
            
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8', errors='ignore')
            return {
                "status": "API_ERROR",
                "order": mission_order,
                "error": f"HTTP {e.code}",
                "error_body": error_body[:500]
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
        
        # RUN 폴더 생성 (안전 보호)
        run_id = datetime.now().strftime("RUN_%Y%m%d_%H%M%S_%f")[:26]
        self.run_path = self.runs_dir / run_id
        
        try:
            self.run_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"[FAIL_FAST] Cannot create run_path: {e}", file=sys.stderr)
            sys.stderr.flush()
            sys.exit(1)
        
        # TARGET_RUN_PATH 즉시 출력 (stdout 리다이렉트 전)
        print(f"[MANAGER] RUN CREATED: {self.run_path}")
        print(f"TARGET_RUN_PATH:{self.run_path}")
        sys.stdout.flush()
        
        # RUN 경로 재확인
        if not self.run_path.exists():
            print(f"[FAIL_FAST] run_path not found after creation", file=sys.stderr)
            sys.stderr.flush()
            sys.exit(1)
        
        # 증거팩 작성기 초기화
        try:
            self.evidence = EvidenceWriter(self.run_path)
        except Exception as e:
            print(f"[FAIL_FAST] EvidenceWriter init failed: {e}", file=sys.stderr)
            sys.stderr.flush()
            sys.exit(1)
        
        # stdout/stderr 저장 설정
        self.stdout_path = self.run_path / "stdout_manager.txt"
        self.stderr_path = self.run_path / "stderr_manager.txt"
        
        # 표준 출력 리다이렉트 (보호)
        try:
            sys.stdout = TeeWriter(sys.stdout, self.stdout_path)
            sys.stderr = TeeWriter(sys.stderr, self.stderr_path)
        except Exception as e:
            # 리다이렉트 실패해도 계속 진행 (콘솔만 사용)
            print(f"[WARN] TeeWriter init failed: {e}", file=sys.stderr)
        
        print(f"[MANAGER] Stdout/stderr redirected to RUN folder")
        
        # 실엔진 초기화
        try:
            self.engine = BasicEngineAdapter()
            print("[MANAGER] Engine initialized: models/gemini-2.0-flash-exp")
        except Exception as e:
            print(f"[FAIL_FAST] Engine initialization failed: {e}")
            sys.stderr.flush()
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
        
        # api_raw 디렉터리 확보
        api_raw_dir = self.run_path / "api_raw"
        api_raw_dir.mkdir(exist_ok=True)
        
        # 실엔진 호출
        result = self.engine.execute_real_mission(
            mission_order=mission_order,
            output_dir=api_raw_dir
        )
        
        # FAIL_FAST 체크
        if result.get("status") == "FAIL_FAST":
            print(f"[FAIL_FAST] Mission {mission_id}: {result.get('error')}")
            raise RuntimeError(f"FAIL_FAST: {result.get('error')}")
        
        # 결과에 mission_id 추가
        result["mission_id"] = mission_id
        result["timestamp"] = datetime.now().isoformat()
        
        # api_raw 저장
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
        [FIX] 거짓합격 완전 제거
        """
        exitcode = 0
        orders = []
        expected_missions = 0
        done_missions = 0
        api_error_count = 0
        reason_code = "UNKNOWN"
        
        try:
            # 오더 로딩
            orders = self.load_orders(order_path)
            expected_missions = len(orders)
            
            print(f"[MANAGER] Starting {expected_missions} missions...")
            print(f"[MANAGER] expected_missions = {expected_missions}")
            
            # 미션 실행 루프
            for idx, order in enumerate(orders, 1):
                mission_id = f"mission_{idx:04d}"
                
                try:
                    result = self.execute_mission(mission_id, order)
                    
                    # [FIX] 상태별 카운트
                    status = result.get("status", "UNKNOWN")
                    if status == "SUCCESS":
                        done_missions += 1
                    elif status == "API_ERROR":
                        api_error_count += 1
                        print(f"[API_ERROR] Mission {mission_id}: {result.get('error')}")
                        # API_ERROR도 일단 진행은 하되, 나중에 FAIL 처리
                    elif status == "ERROR":
                        api_error_count += 1
                        print(f"[ERROR] Mission {mission_id}: {result.get('error')}")
                    
                except RuntimeError as e:
                    # FAIL_FAST: 즉시 중단
                    print(f"[FAIL_FAST] Stopping at mission {mission_id}: {e}")
                    reason_code = "FAIL_FAST"
                    exitcode = 1
                    break
                    
                except Exception as e:
                    # 예외 발생: 즉시 중단
                    print(f"[EXCEPTION] Mission {mission_id} crashed: {e}")
                    traceback.print_exc()
                    reason_code = "EXCEPTION"
                    exitcode = 1
                    break
            else:
                # 루프가 break 없이 끝남 = 모든 주문 처리 시도 완료
                reason_code = "ORDER_EOF"
            
            print(f"[MANAGER] Loop finished:")
            print(f"  expected_missions = {expected_missions}")
            print(f"  done_missions     = {done_missions}")
            print(f"  api_error_count   = {api_error_count}")
            print(f"  reason_code       = {reason_code}")
            
        except FileNotFoundError as e:
            print(f"[FATAL] Order file not found: {e}")
            reason_code = "ORDER_FILE_NOT_FOUND"
            exitcode = 2
            
        except Exception as e:
            print(f"[FATAL] Manager execution failed: {e}")
            traceback.print_exc()
            reason_code = "FATAL_EXCEPTION"
            exitcode = 2
        
        # ============================================
        # [FIX] 거짓합격 완전 제거: exitcode 강제 계산
        # ============================================
        
        # 조건 1: done_missions != expected_missions → FAIL
        if done_missions != expected_missions:
            print(f"[FAIL] done_missions({done_missions}) != expected_missions({expected_missions})")
            exitcode = 1
            if reason_code == "ORDER_EOF":
                reason_code = "INCOMPLETE_MISSIONS"
        
        # 조건 2: api_error_count > 0 → FAIL
        if api_error_count > 0:
            print(f"[FAIL] api_error_count({api_error_count}) > 0")
            exitcode = 1
            if reason_code in ("ORDER_EOF", "INCOMPLETE_MISSIONS"):
                reason_code = "API_ERROR"
        
        # ============================================
        # 증거팩 최종 생성 (무조건 실행)
        # ============================================
        print("[MANAGER] Finalizing evidence pack...")
        self.evidence.finalize(
            exitcode=exitcode,
            expected_missions=expected_missions,
            done_missions=done_missions,
            api_error_count=api_error_count,
            reason_code=reason_code
        )
        
        # ============================================
        # [작업 A] devlog 자동 생성 - 구버전 (generate_devlog)
        # ============================================
        print("[MANAGER] Calling devlog generator...")
        try:
            # devlog 생성 함수 임포트 및 호출
            tools_path = self.ssot_root / "tools"
            if str(tools_path) not in sys.path:
                sys.path.insert(0, str(tools_path))
            
            from generate_devlog import append_devlog
            
            success = append_devlog(self.run_path, self.ssot_root)
            if not success:
                print("[DEVLOG ERROR] Failed to generate devlog")
                exitcode = 1
        except Exception as e:
            print(f"[DEVLOG ERROR] {e}")
            traceback.print_exc()
            exitcode = 1
        
        # ============================================
        # [작업 B] DEVLOG 5파일 자동 생성 (v2 - self 제거)
        # ============================================
        try:
            from pathlib import Path as _P
            
            # ssot_root 직접 계산 (self 의존 제거)
            ssot_root_calc = _P(__file__).resolve().parents[1]
            
            # devlog_writer import (tools 폴더에서)
            devlog_writer_path = ssot_root_calc / "tools"
            if str(devlog_writer_path) not in sys.path:
                sys.path.insert(0, str(devlog_writer_path))
            
            from devlog_writer import generate_devlog_5files
            
            devlog_files = generate_devlog_5files(ssot_root_calc)
            print("[DEVLOG] Auto-generated 5 files")
        except Exception as e:
            print(f"[DEVLOG ERROR] {e}")
            traceback.print_exc()
            exitcode = 1
        
        print(f"[MANAGER] RUN COMPLETE:")
        print(f"  exitcode    = {exitcode}")
        print(f"  reason_code = {reason_code}")
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
        # 경로에 GPTORDER가 이미 포함되어 있는지 확인
        order_str = str(order_path).replace("\\", "/")
        
        if "GPTORDER" in order_str:
            # 이미 GPTORDER 포함 - ssot_root에만 결합
            order_path = ssot_root / order_path
        else:
            # GPTORDER 없음 - GPTORDER 폴더 추가
            order_path = ssot_root / "GPTORDER" / args.order_path
    
    # 실행
    try:
        manager = RunManager(ssot_root)
        exitcode = manager.run(order_path)
        
        # 종료 전 flush
        sys.stdout.flush()
        sys.stderr.flush()
        
        sys.exit(exitcode)
    except Exception as e:
        print(f"[FATAL] Manager failed to start: {e}")
        traceback.print_exc()
        
        # 예외 발생 시에도 flush
        sys.stdout.flush()
        sys.stderr.flush()
        
        sys.exit(1)


if __name__ == "__main__":
    main()
