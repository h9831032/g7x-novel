# SSOT Order Standard V2

## Overview
This document defines the standard format and requirements for GPTORDER files in the G7X SSOT (Single Source of Truth) system.

## Purpose

GPTORDER files are the **mission manifest** for G7X execution. They define:
- What missions to execute
- Execution metadata (profile, constraints)
- Validation requirements
- Evidence expectations

## File Naming Convention

### Format
```
{TYPE}{NUMBER}_{DESCRIPTOR}_{VERSION}.txt
```

### Components

**TYPE**: Mission type identifier
- `REAL` - Production missions (actual AI execution)
- `TEST` - Test missions (validation, smoke testing)
- `GPTORDER_G7X` - Numbered order specification

**NUMBER**: Mission count or order ID
- `REAL06` - 6 real missions
- `REAL24` - 24 real missions
- `REAL30` - 30 real missions
- `REAL36` - 36 real missions
- `TEST_REAL12_VERIFY` - 12 verification missions

**DESCRIPTOR**: Human-readable purpose
- `SMOKE` - Smoke test
- `DAY_S1` - Day profile, Slice 1
- `NIGHT_S2` - Night profile, Slice 2
- `FAILBOX_INTENTIONAL` - Intentional failure test

**VERSION** (optional): Date stamp
- `20260117` - January 17, 2026

### Examples
```
REAL06_SMOKE_20260117.txt
REAL24_DAY_S1.txt
REAL30_NIGHT_S3.txt
TEST_REAL12_VERIFY.txt
GPTORDER_G7X_01_REAL12_SMOKE_RUN_V1_20260117.txt
```

## File Structure

### Required Header

Every GPTORDER file MUST start with:
```
[SSOT MANDATE]
- REAL execution only
- No dummy/simulation missions
- Evidence pack required
```

**Why**: FAIL_FAST validation checks for this header. Missing header = instant rejection.

### Optional Metadata

Additional constraints can be specified:
```
[SSOT MANDATE]
- REAL execution only
- No dummy/simulation missions
- Evidence pack required
- Profile: NIGHT
- Max retries: 5
- Batch size: 3
```

### MODEL Field (REQUIRED)

**[MODEL]** field is MANDATORY in all SSOT orders:
```
[MODEL] SONNET
```
or
```
[MODEL] OPUS
```

**Model Selection Rules**:
- **SONNET**: Default for all general tasks (documents, simple scripts, order files)
- **OPUS**: Only for 3 cases:
  1. Structure/welding (entry points, runners, gates, core pipeline)
  2. FAIL_FAST/guards (duplicate check, header validation, encoding, evidence, checkpoint)
  3. Final repair after 2+ SONNET failures

**MODEL_STAMP Field (REQUIRED)**:
Every work output MUST include MODEL_STAMP in the first line:
```
MODEL_STAMP: Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)
```

**Missing MODEL or MODEL_STAMP = FAIL_FAST**

### Mission Lines

After header, one mission per line:
```
Generate a 3-sentence professional summary of cloud computing benefits.
Write 5 bullet points about remote work best practices.
Create a simple to-do list with 4 items for a software project.
```

### Mission Line Rules

1. **One mission per line** - Each line is one API call
2. **No empty lines** - Empty lines are stripped (but avoided for clarity)
3. **No duplicates** - Duplicate mission lines trigger FAIL_FAST
4. **Clear instructions** - Each line should be a complete, actionable prompt
5. **Reasonable length** - Avoid extremely long or short missions

## Validation Rules (FAIL_FAST)

Before execution, manager.py validates:

### V1: Header Check
```python
if "[SSOT MANDATE]" not in content:
    raise ValueError("Missing [SSOT MANDATE] header")
```

### V2: Filename Banned Words
Banned words in **filename only**:
- `dummy`
- `placeholder`
- `가라` (Korean: fake)
- `더미` (Korean: dummy)

```python
banned_words = ["dummy", "placeholder", "가라", "더미"]
for word in banned_words:
    if word in filename.lower():
        raise ValueError(f"Banned word in filename: {word}")
```

### V3: Duplicate Lines
```python
if len(lines) != len(set(lines)):
    raise ValueError("Duplicate mission lines detected")
```

### V4: Empty File
```python
if len(lines) == 0:
    raise ValueError("Order file is empty")
```

## Mission Types

### Type 1: REAL (Production)

Real AI execution missions for actual output generation.

**Characteristics**:
- Calls Gemini API
- Generates real content
- Consumes quota
- Creates evidence pack

**Example**: REAL30.txt
```
[SSOT MANDATE]
- REAL execution only
Write a professional email template for project status updates.
Create a bullet-point summary of agile methodology benefits.
Generate a code review checklist with 8 items.
...
```

### Type 2: TEST (Validation)

Test missions for system validation, no production output.

**Characteristics**:
- May or may not call API (depending on test type)
- Focus on system behavior validation
- Used for smoke tests, artifact checks

**Example**: TEST_REAL12_VERIFY.txt
```
[SSOT MANDATE]
- REAL execution only
- Verification run for artifact generation
Generate a simple greeting message.
List 3 programming best practices.
...
```

### Type 3: FAILBOX (Intentional Failure)

Missions designed to trigger errors for testing error handling.

**Characteristics**:
- Intentionally impossible or rate-limit-inducing requests
- Tests FAIL_FAST, error logging, evidence generation on failure

**Example**: REAL06_FAILBOX_INTENTIONAL.txt
```
[SSOT MANDATE]
- REAL execution only
- INTENTIONAL FAILURE BOX for testing
Generate a response that is exactly 100000 characters long with random text.
List all prime numbers between 1 and 1000000000000.
...
```

## Batch Slicing Pattern

Large order sets are split into batches using slice notation:

### 3+3×N Pattern

For 24 missions (N=4):
- `REAL24_DAY_S1.txt` - Missions 1-6
- `REAL24_DAY_S2.txt` - Missions 7-12
- `REAL24_DAY_S3.txt` - Missions 13-18
- `REAL24_DAY_S4.txt` - Missions 19-24

For 30 missions (N=5):
- `REAL30_NIGHT_S1.txt` - Missions 1-6
- `REAL30_NIGHT_S2.txt` - Missions 7-12
- `REAL30_NIGHT_S3.txt` - Missions 13-18
- `REAL30_NIGHT_S4.txt` - Missions 19-24
- `REAL30_NIGHT_S5.txt` - Missions 25-30

### Slice Naming Convention
```
{BASE}_{PROFILE}_S{N}.txt

BASE: REAL24, REAL30, REAL36
PROFILE: DAY, NIGHT
N: Slice number (1-based)
```

## Profile Integration

### DAY Profile
Fast execution for development/testing:
```
REAL24_DAY_S1.txt
REAL24_DAY_S2.txt
...
```

Characteristics:
- Shorter delays (8s between missions)
- Faster batch delay (20s)
- 5 max retries

### NIGHT Profile
Conservative execution for overnight batch runs:
```
REAL24_NIGHT_S1.txt
REAL24_NIGHT_S2.txt
...
```

Characteristics:
- Longer delays (25s between missions)
- Extended batch delay (75s)
- 6 max retries

## Evidence Requirements

Every GPTORDER execution MUST generate evidence pack:

### Required Files (7 minimum)
```
runs/RUN_{timestamp}/
├── exitcode.txt          # 0 = success, non-zero = failure
├── stdout_manager.txt    # Execution output
├── stderr_manager.txt    # Error output (should be empty)
├── verify_report.json    # Mission completion report
├── stamp_manifest.json   # Hash manifest
├── final_audit.json      # Audit trail
└── apply_diff.txt        # Change summary
```

### Evidence Validation
```bash
# Automated validation
python tools/check_run_artifacts_v1.py

# Expected output:
# [PASS] All required artifacts present!
# [VERIFY_MIN] PASS - Files exist and valid
```

## Example GPTORDER Files

### Example 1: REAL06_SMOKE_20260117.txt
```
[SSOT MANDATE]
- REAL execution only
- No dummy/simulation missions
- Evidence pack required
Generate a 3-sentence professional summary of cloud computing benefits.
Write 5 bullet points about remote work best practices.
Create a simple to-do list with 4 items for a software project.
Draft a polite email template for meeting requests.
List 3 key principles of agile project management.
Summarize the importance of code reviews in 2-3 sentences.
```

### Example 2: REAL24_DAY_S1.txt (First 6 of 24)
```
[SSOT MANDATE]
- REAL execution only
- Profile: DAY
- Batch: S1 (1-6 of 24)
Write a professional introduction email for a software engineer.
Create a list of 5 effective communication strategies for remote teams.
Generate a brief explanation of the SOLID principles in programming.
Draft a concise project proposal template.
List 4 best practices for writing clean code.
Summarize the benefits of continuous integration in 3 sentences.
```

### Example 3: TEST_REAL12_VERIFY.txt
```
[SSOT MANDATE]
- REAL execution only
- Verification run for artifact generation
Generate a hello world message.
List 3 colors.
Count from 1 to 5.
Name 4 seasons.
List 3 programming languages.
Name 5 common fruits.
List 4 cardinal directions.
Name 3 primary colors.
List 5 days of the week.
Name 4 common animals.
List 3 geometric shapes.
Name 5 common vegetables.
```

## Anti-Patterns

### ❌ Don't: Empty Header
```
# BAD: No header
Write a professional email.
Create a summary.
```

### ❌ Don't: Banned Words in Filename
```
# BAD: Contains "dummy"
REAL06_DUMMY_TEST.txt
REAL12_PLACEHOLDER_SMOKE.txt
```

### ❌ Don't: Duplicate Missions
```
[SSOT MANDATE]
Generate a greeting.
Write a summary.
Generate a greeting.  # DUPLICATE - FAIL_FAST
```

### ❌ Don't: Empty File
```
[SSOT MANDATE]

# BAD: No mission lines
```

### ✅ Do: Follow Standard
```
# GOOD: Complete, valid GPTORDER
[SSOT MANDATE]
- REAL execution only
Generate a professional greeting.
Write a concise project summary.
Create a list of 5 best practices.
```

## Migration from V1

If you have legacy order files:

### V1 Format (Legacy)
```
mission1.txt:
  Generate greeting

mission2.txt:
  Write summary
```

### V2 Format (Current)
```
REAL02_MIGRATION.txt:
[SSOT MANDATE]
- REAL execution only
Generate greeting
Write summary
```

## Version History

- **V2** (2026-01-17): Major update for G7X V3
  - Added FAIL_FAST validation rules
  - Defined batch slicing pattern (3+3×N)
  - Established evidence requirements
  - Documented profile integration
  - Added FAILBOX mission type

- **V1** (2026-01-12): Initial SSOT order standard
  - Basic header format
  - One mission per line rule

---

**Document ID**: SSOT_ORDER_STANDARD_V2
**Created**: 2026-01-17
**Status**: ACTIVE
