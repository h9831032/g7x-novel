# G7X Delay Policy V1

## Overview
This document clarifies the delay/retry policy for G7X mission execution to prevent API rate limiting (429 errors) and ensure reliable execution.

## Profiles

G7X supports two execution profiles controlled by the `G7_RUN_PROFILE` environment variable:

### DAY Profile (Default)
Faster execution for daytime testing and development.

```
MAX_RETRIES: 5
BASE_DELAY: 2.0 seconds
RETRY_MULTIPLIER: 2.0
BATCH_SIZE: 3 missions
BATCH_DELAY: 20.0 seconds
TASK_DELAY_PER_MISSION: 8.0 seconds
JITTER_MAX: 1.0 seconds
```

### NIGHT Profile
Slower, more conservative execution for overnight batch runs.

```
MAX_RETRIES: 6
BASE_DELAY: 5.0 seconds
RETRY_MULTIPLIER: 2.0
BATCH_SIZE: 3 missions
BATCH_DELAY: 75.0 seconds
TASK_DELAY_PER_MISSION: 25.0 seconds
JITTER_MAX: 2.0 seconds
```

## Delay Components

### 1. TASK_DELAY_PER_MISSION
Delay **between** individual mission executions.
- DAY: 8 seconds
- NIGHT: 25 seconds
- Applied after each mission (except the last one)

### 2. BATCH_DELAY
Extended delay after completing a batch of missions.
- DAY: 20 seconds (after every 3 missions)
- NIGHT: 75 seconds (after every 3 missions)
- Applied when: `mission_count % BATCH_SIZE == 0`

### 3. RETRY_DELAY
Exponential backoff for API retry attempts.
- Formula: `BASE_DELAY * (RETRY_MULTIPLIER ** attempt)`
- DAY example:
  - Retry 1: 2.0 * 2^1 = 4.0s
  - Retry 2: 2.0 * 2^2 = 8.0s
  - Retry 3: 2.0 * 2^3 = 16.0s
- NIGHT example:
  - Retry 1: 5.0 * 2^1 = 10.0s
  - Retry 2: 5.0 * 2^2 = 20.0s
  - Retry 3: 5.0 * 2^3 = 40.0s

### 4. JITTER
Random variation added to delays to prevent synchronized requests.
- DAY: 0 to 1.0 seconds
- NIGHT: 0 to 2.0 seconds
- Applied to: TASK_DELAY, BATCH_DELAY

## Usage

### Set Profile via Environment Variable

**Windows (PowerShell)**:
```powershell
$env:G7_RUN_PROFILE = "NIGHT"
python main/manager.py GPTORDER/REAL30.txt
```

**Windows (cmd)**:
```cmd
set G7_RUN_PROFILE=NIGHT
python main/manager.py GPTORDER/REAL30.txt
```

**Linux/Mac**:
```bash
export G7_RUN_PROFILE=NIGHT
python main/manager.py GPTORDER/REAL30.txt
```

### Default Behavior
If `G7_RUN_PROFILE` is not set, **DAY** profile is used.

## Execution Timeline Example

### DAY Profile (6 missions)
```
Mission 1: Execute
  + 8s task delay
Mission 2: Execute
  + 8s task delay
Mission 3: Execute
  + 8s task delay + 20s batch delay (3 missions completed)
Mission 4: Execute
  + 8s task delay
Mission 5: Execute
  + 8s task delay
Mission 6: Execute (last, no delay)

Total time: ~52 seconds (6 missions)
```

### NIGHT Profile (6 missions)
```
Mission 1: Execute
  + 25s task delay
Mission 2: Execute
  + 25s task delay
Mission 3: Execute
  + 25s task delay + 75s batch delay (3 missions completed)
Mission 4: Execute
  + 25s task delay
Mission 5: Execute
  + 25s task delay
Mission 6: Execute (last, no delay)

Total time: ~175 seconds (6 missions)
```

## Retry Strategy

When API returns 429 (rate limit):
1. Wait: `BASE_DELAY * (2 ** attempt)` + jitter
2. Retry up to MAX_RETRIES times
3. If all retries fail: Mark mission as API_ERROR

## Configuration Location

All delay parameters are defined in `main/manager.py`:
- `DAY_PROFILE` dictionary (lines 34-42)
- `NIGHT_PROFILE` dictionary (lines 44-52)
- `get_active_profile()` function (lines 54-59)

## FAIL_FAST Rule

If `G7_RUN_PROFILE` is set to an invalid value (not "DAY" or "NIGHT"), the system defaults to DAY profile. No FAIL_FAST error is raised.

## Version History

- **V1** (2026-01-17): Initial delay policy documentation
  - Defined DAY and NIGHT profiles
  - Documented delay components and retry strategy
  - Added usage examples

---

**Document ID**: DELAY_POLICY_V1
**Created**: 2026-01-17
**Status**: ACTIVE
