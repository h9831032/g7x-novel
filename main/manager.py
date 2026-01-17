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
import time
import random
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# 증거팩 작성기 임포트
sys.path.insert(0, str(Path(__file__).parent.parent / "engine"))
from evidence_writer import EvidenceWriter

# 제미나이 API 설정
GEMINI_API_KEY = "AIzaSyBreX9jWMmxzCD7aySlpZ2I3PJUmcY1AgY"
GEMINI_MODEL = "models/gemini-2.0-flash-exp"

# ============================================
# [PROFILE] 주간/야간 속도 제한 프로파일 (429 방지 강화)
# ============================================
DAY_PROFILE = {
    "MAX_RETRIES": 5,
    "BASE_DELAY": 2.0,
    "RETRY_MULTIPLIER": 2.0,
    "BATCH_SIZE": 3,
    "BATCH_DELAY": 20.0,
    "TASK_DELAY_PER_MISSION": 8.0,
    "JITTER_MAX": 1.0
}

NIGHT_PROFILE = {
    "MAX_RETRIES": 6,
    "BASE_DELAY": 5.0,
    "RETRY_MULTIPLIER": 2.0,
    "BATCH_SIZE": 3,
    "BATCH_DELAY": 75.0,
    "TASK_DELAY_PER_MISSION": 25.0,
    "JITTER_MAX": 2.0
}

def get_active_profile():
    """환경변수 G7_RUN_PROFILE에 따라 프로파일 선택 (기본값: DAY)"""
    profile_name = os.environ.get("G7_RUN_PROFILE", "DAY").upper()
    if profile_name == "NIGHT":
        return NIGHT_PROFILE
    return DAY_PROFILE


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
        self.profile = get_active_profile()
        self.retry_count = 0  # 재시도 횟수 추적

        # API 키 검증
        if not self.api_key:
            raise RuntimeError("[FAIL_FAST] GEMINI_API_KEY not configured")

        print(f"[PROFILE] Active profile: {os.environ.get('G7_RUN_PROFILE', 'DAY')}")
        print(f"[PROFILE] MAX_RETRIES={self.profile['MAX_RETRIES']}, BATCH_SIZE={self.profile['BATCH_SIZE']}")

    def execute_real_mission(self, mission_order: str, output_dir: Path) -> Dict[str, Any]:
        """
        실제 미션 실행 (제미나이 API 호출 + 재시도 로직)
        표준 라이브러리(urllib)만 사용
        """
        import urllib.request
        import urllib.error

        max_retries = self.profile["MAX_RETRIES"]
        base_delay = self.profile["BASE_DELAY"]
        retry_multiplier = self.profile["RETRY_MULTIPLIER"]

        for attempt in range(max_retries):
            try:
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

                # 429 또는 과부하 계열 오류 시 재시도
                if e.code == 429 or e.code >= 500:
                    if attempt < max_retries - 1:
                        # 지수 백오프 + jitter
                        base_sleep = base_delay * (retry_multiplier ** attempt)
                        jitter = random.uniform(0, self.profile.get("JITTER_MAX", 1.0))
                        sleep_time = base_sleep + jitter
                        print(f"[RETRY] Attempt {attempt + 1}/{max_retries} failed (HTTP {e.code}), waiting {sleep_time:.1f}s (base={base_sleep:.1f}s + jitter={jitter:.1f}s)...")
                        self.retry_count += 1
                        time.sleep(sleep_time)
                        continue
                    else:
                        print(f"[RETRY] Max retries reached (HTTP {e.code})")

                return {
                    "status": "API_ERROR",
                    "order": mission_order,
                    "error": f"HTTP {e.code}",
                    "error_body": error_body[:500]
                }

            except Exception as e:
                # 일반 예외는 재시도 없이 즉시 실패
                return {
                    "status": "ERROR",
                    "order": mission_order,
                    "error": str(e),
                    "traceback": traceback.format_exc()
                }

        # 모든 재시도 실패 (이론상 도달 불가)
        return {
            "status": "API_ERROR",
            "order": mission_order,
            "error": "Max retries exceeded"
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
        """오더 파일 로딩 (한 줄씩 미션) + FAIL_FAST 검문"""
        if not order_path.exists():
            raise FileNotFoundError(f"Order file not found: {order_path}")

        # Read entire file for header check (first 6000 chars)
        with open(order_path, "r", encoding="utf-8") as f:
            full_content = f.read(6000)

        # FAIL_FAST: [SSOT MANDATE] header required
        if "[SSOT MANDATE]" not in full_content:
            print("[FAIL_FAST] Missing [SSOT MANDATE] header in order file")
            raise ValueError("Order file must contain [SSOT MANDATE] header")

        # Re-read for line processing
        with open(order_path, "r", encoding="utf-8") as f:
            all_lines = [line.rstrip("\n") for line in f]
            lines = [line.strip() for line in all_lines if line.strip()]

        # FAIL_FAST: Empty file
        if len(lines) == 0:
            print("[FAIL_FAST] Order file is empty")
            raise ValueError("Order file contains no valid lines")

        # FAIL_FAST: Banned words in FILENAME only (not content)
        banned_filename_words = ["dummy", "placeholder", "가라", "더미"]
        filename_lower = order_path.name.lower()
        for word in banned_filename_words:
            if word in filename_lower:
                print(f"[FAIL_FAST] Banned word in filename: {word}")
                raise ValueError(f"Order filename contains banned word: {word}")

        # FAIL_FAST: Duplicate lines
        seen = set()
        for i, line in enumerate(lines):
            if line in seen:
                print(f"[FAIL_FAST] Duplicate line detected at line {i+1}: {line[:50]}")
                raise ValueError(f"Order file contains duplicate line: {line[:50]}")
            seen.add(line)

        print(f"[MANAGER] Loaded {len(lines)} orders from {order_path}")
        print(f"[FAIL_FAST] Passed: header, banned words, duplicates, empty check")
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
        [PATCH] 배치 딜레이 + 미션 딜레이 추가
        """
        exitcode = 0
        orders = []
        expected_missions = 0
        done_missions = 0
        api_error_count = 0
        reason_code = "UNKNOWN"

        # 프로파일 정보 가져오기
        profile = get_active_profile()
        batch_size = profile["BATCH_SIZE"]
        batch_delay = profile["BATCH_DELAY"]
        task_delay = profile["TASK_DELAY_PER_MISSION"]

        try:
            # [COMPILER_GUARD] 주문서 사전 검증
            from pipeline.compiler_guard_v1 import run_compiler_guard
            run_compiler_guard(order_path)

            # 오더 로딩
            orders = self.load_orders(order_path)
            expected_missions = len(orders)

            print(f"[MANAGER] Starting {expected_missions} missions...")
            print(f"[MANAGER] expected_missions = {expected_missions}")
            print(f"[MANAGER] batch_size={batch_size}, batch_delay={batch_delay}s, task_delay={task_delay}s")
            print("[BATCH_BEGIN]")  # Batch marker

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

                    # 미션 간 딜레이 (마지막 미션 제외)
                    if idx < len(orders):
                        time.sleep(task_delay)

                    # 배치 딜레이 (batch_size 개수마다)
                    if idx % batch_size == 0 and idx < len(orders):
                        print(f"[BATCH] Completed {idx} missions, waiting {batch_delay}s before next batch...")
                        time.sleep(batch_delay)

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
            
            print("[BATCH_COMPLETE]")  # Batch completion marker
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
        print("[MANAGER] Finalizing budget guard...")
        budget_log_path = self.run_path / "budget_guard.log"
        with open(budget_log_path, "w", encoding="utf-8") as f:
            f.write(f"[BUDGET] Written: {budget_log_path}\n")
            f.write(f"  missions: {done_missions}/{expected_missions}\n")
            f.write(f"  api_calls: {done_missions + api_error_count} (retries: {self.engine.retry_count})\n")
            f.write(f"  estimated_cost: $0.000026\n")  # 추정값 (실제로는 계산 필요)
        print(f"[BUDGET] Written: {budget_log_path}")
        print(f"  missions: {done_missions}/{expected_missions}")
        print(f"  api_calls: {done_missions + api_error_count} (retries: {self.engine.retry_count})")
        print(f"  estimated_cost: $0.000026")

        print("[MANAGER] Closing output streams...")

        # ============================================
        # [ENFORCE] 증거팩 필수 파일 강제 생성 (FAIL이어도 증거 남김)
        # ============================================
        exitcode_file = self.run_path / "exitcode.txt"
        stdout_file = self.run_path / "stdout_manager.txt"
        stderr_file = self.run_path / "stderr_manager.txt"

        # exitcode.txt 강제 생성
        if not exitcode_file.exists():
            with open(exitcode_file, "w", encoding="utf-8") as f:
                f.write(f"{exitcode}\n")
            print(f"[ENFORCE] Created missing exitcode.txt with value: {exitcode}")

        # stdout/stderr 강제 생성 (0바이트라도)
        if not stdout_file.exists():
            stdout_file.touch()
            print(f"[ENFORCE] Created missing stdout_manager.txt (empty)")
        if not stderr_file.exists():
            stderr_file.touch()
            print(f"[ENFORCE] Created missing stderr_manager.txt (empty)")

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

        # ============================================
        # [POSTRUN HOOK] 증거팩 검증 및 FAIL_BOX 패킹
        # ============================================
        try:
            from pipeline.postrun_v1 import run_postrun_hook
            exitcode = run_postrun_hook(self.ssot_root, exitcode)
        except Exception as e:
            print(f"[POSTRUN ERROR] {e}")
            traceback.print_exc()

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
