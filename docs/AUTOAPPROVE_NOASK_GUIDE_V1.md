# Claude Code Auto-Approve and No-Ask Switch Guide V1

## Overview
This guide documents the auto-approval and no-ask behavior settings for Claude Code when working with G7X project automation scripts and tools.

## Philosophy

G7X is a batch automation system designed for:
- **Unattended execution**: Night runs, batch processing
- **Deterministic behavior**: Same input → same output
- **Evidence-based validation**: Trust but verify with evidence packs
- **Fail-fast safety**: Errors stop execution immediately

Claude Code should operate in **autonomous mode** when executing G7X workflows to avoid blocking on confirmation prompts during batch runs.

## Auto-Approval Rules

### Tier 1: Always Auto-Approve (No Confirmation)

These operations are safe, deterministic, and essential for G7X workflows:

#### File Reading
- Reading any `.py`, `.ps1`, `.txt`, `.md`, `.json` files in G7X project
- Reading GPTORDER files
- Reading evidence files (verify_report.json, exitcode.txt, etc.)
- Reading checkpoint files

#### Script Execution - Validation Tools
- `tools/check_run_artifacts_v1.py`
- `tools/error_log_check_v1.py`
- `tools/stop_gate_v1.py`
- `tools/order_scan_encoding_v1.ps1`
- `tools/verify_e2e_v1.ps1`
- `main/pipeline/compiler_guard_v1.py`

#### Script Execution - Read-Only Operations
- `tools/summarize_latest_run_v1.py`
- `tools/build_daily_report_v1.py`
- `tools/build_next_top10_v1.py`

#### Git Operations - Safe
- `git status`
- `git diff`
- `git log`
- `git show`
- `git branch` (list only)

### Tier 2: Auto-Approve with Logging (Silent Confirmation)

These operations modify state but are reversible and evidence-tracked:

#### Script Execution - Batch Runners
- `tools/run_real24_skeleton.ps1`
- `tools/run_real24_3p3x4_day_night.ps1`
- `tools/run_real30_3p3x5_day_night.ps1`
- `tools/run_real36_3p3x6_day_night.ps1`
- `tools/run_real_smoke_pack_v1.ps1`

**Why auto-approve?**
- These scripts have built-in STOP gates
- All operations generate evidence packs
- Exit codes indicate success/failure
- Can be audited post-execution

#### File Writing - Evidence and Reports
- Writing to `runs/RUN_*/` directories
- Writing to `DEVLOG/` directories
- Writing to `STATE_PACK/` directories
- Writing to `docs/` for documentation updates

#### Manager Execution
- `main/manager.py` with valid GPTORDER file
- Creates RUN folder with full evidence
- Fail-fast on errors
- Auto-stops on API errors

### Tier 3: Require Confirmation (Critical Operations)

These operations are irreversible or affect external systems:

#### Git Operations - Dangerous
- `git push` (requires confirmation)
- `git reset --hard` (requires confirmation)
- `git clean -fd` (requires confirmation)
- Creating commits (can auto-approve if user explicitly requested)

#### File Operations - Destructive
- Deleting files outside `runs/` or temp directories
- Modifying core pipeline files (`main/*.py`, `pipeline/*.py`) without explicit instruction
- Removing directories

#### External System Calls
- API calls outside manager.py execution
- Network requests
- System configuration changes

## No-Ask Switch

### When to Enable NO_ASK Mode

Claude Code should enable NO_ASK mode when:

1. **User explicitly requests batch execution**
   ```
   User: "Run REAL24 in 4 batches, don't ask me anything"
   User: "Execute all 24 orders, no questions"
   User: "묻지말고 진행시켜" (Don't ask, just proceed)
   ```

2. **Executing from trusted scripts**
   - PowerShell runner scripts (`run_real*.ps1`)
   - Validation scripts (`check_*.py`)
   - Evidence generation scripts

3. **During night/batch mode**
   - When `G7_RUN_PROFILE=NIGHT` is set
   - When running from automated scheduler
   - When explicit "unattended" flag is present

### NO_ASK Behavior

In NO_ASK mode, Claude Code should:

1. **Auto-approve Tier 1 and Tier 2 operations** without confirmation prompts
2. **Log all operations** to evidence files for post-execution audit
3. **Fail fast on errors** instead of asking for retry/continue
4. **Respect STOP gates** - checkpoint validation still runs
5. **Generate full evidence** for every operation
6. **Exit with clear status codes** (0 = success, non-zero = failure)

### Disabling NO_ASK Mode

NO_ASK mode should auto-disable when:
- User explicitly asks a question (re-entering interactive mode)
- Tier 3 operation is encountered
- Unexpected error requires user decision
- Batch execution completes (success or failure)

## Configuration Patterns

### Pattern 1: Explicit NO_ASK Request
```
User: "Run all 24 orders in 4 batches, no confirmation needed"

Claude: [Enables NO_ASK mode]
[Executes Batch S1]
[Generates evidence]
[Checks STOP gate]
[Executes Batch S2]
...
[Reports final status with evidence paths]
```

### Pattern 2: Script-Triggered NO_ASK
```
User: "Execute run_real24_3p3x4_day_night.ps1"

Claude: [Detects batch runner script]
[Enables NO_ASK mode for script execution]
[Script runs with auto-approval]
[Reports completion with exit code]
```

### Pattern 3: Interactive Mode (Default)
```
User: "Should I run REAL24 now?"

Claude: [Stays in interactive mode]
"I can run REAL24 for you. Would you like me to execute it in 4 batches?"
[Waits for confirmation]
```

## Safety Mechanisms

Even in NO_ASK mode, these safety checks remain active:

1. **FAIL_FAST validation** - Compiler guard, header checks
2. **STOP gates** - Checkpoint validation between batches
3. **Evidence pack requirements** - All runs must generate evidence
4. **Error log zero rule** - api_error_count > 0 triggers FAIL
5. **Exit code enforcement** - exitcode ≠ 0 triggers FAIL

## Evidence Trail

All NO_ASK operations must generate evidence:
- Command executed (full command line)
- Timestamp (ISO 8601 format)
- Exit code
- Output summary (stdout/stderr)
- RUN_PATH (if applicable)
- Checkpoint state (before/after)

This evidence is written to:
- `runs/RUN_*/stdout_manager.txt`
- `runs/RUN_*/stderr_manager.txt`
- `STATE_PACK/CHECKPOINT_LATEST.txt`
- `DEVLOG/DAILY_REPORT_*.md`

## Examples

### Example 1: Batch Execution with NO_ASK
```
User: "Execute 24 SSOT orders, 6 at a time, don't ask questions"

Claude: [NO_ASK enabled]
[Batch S1] Executing ORDER_01-06...
  - ORDER_01: PASS
  - ORDER_02: PASS
  ...
  - ORDER_06: PASS
[STOP_GATE] Checkpoint validated
[Batch S2] Executing ORDER_07-12...
  ...

[COMPLETE] All 24 orders executed
Evidence: C:\g7core\g7_v1\runs\RUN_20260117_...
Exit code: 0
```

### Example 2: Interactive Confirmation (NO_ASK disabled)
```
User: "What should I do next?"

Claude: [Interactive mode]
"Based on the checkpoint, you've completed Batch S1. The next step would be Batch S2 (ORDER_07-12). Should I proceed?"

User: "Yes, but ask before each batch"

Claude: [Stays in interactive mode]
[Executes ORDER_07-12 with confirmation prompts]
```

### Example 3: Error Handling in NO_ASK
```
User: "Run REAL24, no questions"

Claude: [NO_ASK enabled]
[Batch S1] Executing...
[ORDER_03] API_ERROR detected
[FAIL_FAST] Stopping execution
[Evidence generated]
Exit code: 1
RUN_PATH: C:\g7core\g7_v1\runs\RUN_20260117_...
Error: api_error_count = 1 (see verify_report.json)
```

## Version History

- **V1** (2026-01-17): Initial auto-approve and no-ask guide
  - Defined three-tier approval system
  - Established NO_ASK mode triggers and behavior
  - Documented safety mechanisms
  - Provided execution examples

---

**Document ID**: AUTOAPPROVE_NOASK_GUIDE_V1
**Created**: 2026-01-17
**Status**: ACTIVE
