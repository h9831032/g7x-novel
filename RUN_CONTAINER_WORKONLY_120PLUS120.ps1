# [V1.0] 120+120 트럭 통합 러너
# PERSISTENCE_GUARD: 작업 성공/실패 관계없이 창 유지

$SSOT_ROOT = "C:\g7core\g7_v1"
$RUN_ID = "REAL_BATTLE_FINAL"
$RUN_DIR = "$SSOT_ROOT\runs\$RUN_ID"

try {
    # 1. 패킷 생성 (6x20 포장)
    python "$SSOT_ROOT\tools\dispatch\packet_generator_slots_v3.py"

    # 2. 트럭 A 주행 (20번들)
    for ($i=1; $i -le 20; $i++) {
        python "$SSOT_ROOT\tools\run_bundle_v4.py" "A" $i $RUN_DIR
        if ($LASTEXITCODE -eq 3) { throw "BUDGET_GUARD_TRIP" }
    }
    Write-Host ">>> [SUCCESS] TRUCK A SEALED." -ForegroundColor Green

    # 3. 트럭 B 주행 (20번들)
    for ($i=1; $i -le 20; $i++) {
        python "$SSOT_ROOT\tools\run_bundle_v4.py" "B" $i $RUN_DIR
        if ($LASTEXITCODE -eq 3) { throw "BUDGET_GUARD_TRIP" }
    }
    Write-Host ">>> [SUCCESS] TRUCK B SEALED." -ForegroundColor Green

} catch {
    Write-Host "!!! [CRITICAL_FAIL] $_" -ForegroundColor Red
} finally {
    Read-Host "Audit Done. (엔터 시 종료)"
}