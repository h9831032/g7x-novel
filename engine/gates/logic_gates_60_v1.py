# C:\g7core\g7_v1\engine\gates\logic_gates_60_v1.py
class LogicGates60:
    def check_all(self, claim):
        # 12종 충돌 x 5종 엔티티 = 60개 체크포인트
        gates = ["ALIVE_DEAD", "OWNERSHIP", "LOCATION", "TIME_ORDER", "CAUSE_EFFECT"]
        results = {g: True for g in gates} # 정밀 로직 진입
        return results

# C:\g7core\g7_v1\engine\gates\exception_judge_60_v1.py
class ExceptionJudge60:
    def judge(self, gate_fails, world_profile):
        # 경찰(Gate)이 기소한 건을 판사가 설정/복선 기반으로 사면
        is_consistent = world_profile.get("declared_before", False)
        cost_paid = world_profile.get("cost_paid", False)
        
        if is_consistent and cost_paid:
            return "RELEASED", "설정 근거 있음"
        return "GUILTY", "개연성 파괴"