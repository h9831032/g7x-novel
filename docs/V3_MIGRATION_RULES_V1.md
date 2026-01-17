# G7X V3 Migration Rules V1

## Overview
This document establishes migration rules for transitioning from G7X legacy patterns to V3 standardized patterns.

## Migration Philosophy

**Goal**: Consolidate fragmented code into unified, evidence-tracked pipeline.

**Principle**: "Don't rewrite, refactor incrementally with evidence at each step."

## What is V3?

V3 refers to the **third-generation G7X architecture** characterized by:

1. **Single Source of Truth (SSOT)**: One main entry point (`manager.py`)
2. **Evidence-First**: Every operation generates evidence pack
3. **Pipeline Modularization**: Separate concerns (evidence, catalog, devlog, runner)
4. **FAIL_FAST**: Early validation, no silent failures
5. **Batch Safety**: Checkpoint system, STOP gates between batches

## Migration Triggers

Migrate to V3 when:
1. Creating new functionality (always use V3 patterns)
2. Fixing bugs in legacy code (opportunistic migration)
3. Consolidating duplicate implementations
4. Adding evidence tracking to existing features

Do NOT migrate:
- Working production code unless fixing bugs
- Code scheduled for deprecation
- External dependencies or third-party integrations

## V3 Pattern Requirements

### R1: Main Entry Point
All execution flows through `main/manager.py`:
```python
# BAD (V1/V2): Direct script execution
python tools/some_script.py

# GOOD (V3): Via manager with GPTORDER
python main/manager.py GPTORDER/REAL06.txt
```

### R2: Evidence Pack Generation
Every run must create evidence:
```python
# Required files in runs/RUN_*/
- exitcode.txt         # Exit status (0 or non-zero)
- stdout_manager.txt   # Standard output
- stderr_manager.txt   # Standard error
- verify_report.json   # Mission completion report
- stamp_manifest.json  # Hash manifest
- final_audit.json     # Final audit trail
- apply_diff.txt       # Change summary
```

### R3: Pipeline Modularity
Use pipeline modules for specific concerns:
```python
# BAD: Monolithic script
def do_everything():
    # 500 lines of mixed logic

# GOOD: Modular pipeline
from pipeline.evidence import EvidenceWriter
from pipeline.catalog import CatalogBuilder
from pipeline.devlog import DevlogWriter

writer = EvidenceWriter(run_path)
writer.finalize(exitcode, stats)
```

### R4: FAIL_FAST Validation
Validate inputs before execution:
```python
# REQUIRED: Pre-flight checks
def load_orders(order_path):
    # Check [SSOT MANDATE] header
    if "[SSOT MANDATE]" not in content:
        raise ValueError("Missing [SSOT MANDATE] header")

    # Check banned words
    # Check duplicates
    # Check empty file

    return orders
```

### R5: Checkpoint Integration
Long-running operations use checkpoints:
```python
# Update checkpoint after each batch
writer._update_checkpoint(exitcode, stats)

# Validate checkpoint before next batch
python tools/stop_gate_v1.py --batch S2
```

## Migration Steps

### Step 1: Identify Legacy Pattern
Example: Direct API call without evidence
```python
# Legacy (V1)
def run_mission(prompt):
    response = gemini_api.call(prompt)
    print(response)
    return response
```

### Step 2: Plan V3 Equivalent
```python
# V3 Target
def execute_mission(mission_id, mission_order):
    result = self.engine.execute_real_mission(mission_order, self.run_path)

    # Write evidence
    self.evidence.write_receipt(mission_id, result)

    # Log API call
    self.evidence.log_api_call(
        mission_id,
        result.get("status"),
        result.get("latency", 0)
    )

    return result
```

### Step 3: Incremental Migration
Don't rewrite everything at once:
```python
# Phase 1: Add evidence tracking (keeping legacy logic)
def run_mission_v2(prompt):
    response = gemini_api.call(prompt)  # Legacy call

    # NEW: Evidence tracking
    evidence = {
        "prompt": prompt[:100],
        "status": "SUCCESS",
        "timestamp": datetime.now().isoformat()
    }
    write_evidence(evidence)  # V3 pattern

    return response

# Phase 2: Replace legacy API call (in next iteration)
# Phase 3: Integrate with manager.py (final step)
```

### Step 4: Validate with Evidence
After migration, verify:
```bash
# Run migrated code
python main/manager.py GPTORDER/TEST.txt

# Check evidence pack
python tools/check_run_artifacts_v1.py

# Verify error log
python tools/error_log_check_v1.py
```

## Forbidden Migration Patterns

### ❌ Don't: Big Bang Rewrite
```python
# BAD: Rewrite entire file at once
# File: legacy_system.py (300 lines)
# Change: Replace all 300 lines with new implementation
```

**Why**: High risk, no rollback, breaks existing workflows.

### ❌ Don't: Silent Breaking Changes
```python
# BAD: Change function signature without deprecation
# Old: process(data)
# New: process(data, config)  # Breaks all callers
```

**Why**: Existing code will fail at runtime.

### ❌ Don't: Remove Evidence Generation
```python
# BAD: Optimize by removing "unnecessary" logging
def quick_run():
    result = do_work()
    # Removed: write_evidence(result)  # "Not needed"
    return result
```

**Why**: Violates evidence-first principle, makes debugging impossible.

## Recommended Migration Patterns

### ✅ Do: Wrapper-First Migration
```python
# GOOD: Add V3 wrapper around legacy code
def legacy_function():
    # Old implementation (unchanged)
    return result

def v3_wrapper():
    # V3: Evidence collection
    start = time.time()
    result = legacy_function()  # Call legacy
    latency = time.time() - start

    # V3: Write evidence
    write_evidence({
        "status": "SUCCESS",
        "latency": latency,
        "result_size": len(result)
    })

    return result
```

### ✅ Do: Deprecation Warnings
```python
# GOOD: Warn users about legacy usage
def old_function():
    warnings.warn(
        "old_function is deprecated, use new_function instead",
        DeprecationWarning
    )
    return new_function()
```

### ✅ Do: Side-by-Side Validation
```python
# GOOD: Run both legacy and V3, compare results
def validate_migration():
    legacy_result = legacy_function()
    v3_result = v3_function()

    if legacy_result != v3_result:
        raise ValueError("Migration validation failed")

    return v3_result
```

## V3 Compliance Checklist

Before marking migration complete:

- [ ] Code flows through `manager.py` or documented entry point
- [ ] Evidence pack generated (all 7 required files)
- [ ] FAIL_FAST validation on inputs
- [ ] Checkpoint integration (if batch operation)
- [ ] Error handling with proper exit codes
- [ ] No silent failures (all errors logged)
- [ ] Backward compatibility maintained (or deprecation notice)
- [ ] Documentation updated (function docstrings, INTEGRATION_MAP)
- [ ] Test execution with REAL06 or equivalent
- [ ] Verification with `check_run_artifacts_v1.py`

## Migration Tracking

Document all migrations in INTEGRATION_MAP:
```json
{
  "migration": {
    "mission_executor": {
      "from": "tools/run_mission.py (V1)",
      "to": "main/manager.py::execute_mission (V3)",
      "date": "2026-01-17",
      "status": "COMPLETE",
      "evidence": "runs/RUN_20260117_183339_708382"
    }
  }
}
```

## Examples

### Example 1: Migrating Batch Runner

**Legacy (V1)**:
```python
# tools/run_batch.py
for mission in missions:
    result = api.call(mission)
    print(result)
```

**V3 Migration**:
```python
# main/manager.py (integrated)
def run(self, order_path):
    orders = self.load_orders(order_path)  # FAIL_FAST

    for idx, order in enumerate(orders, 1):
        result = self.execute_mission(f"mission_{idx:04d}", order)
        # Evidence auto-generated

    self.evidence.finalize(exitcode, stats)
```

### Example 2: Migrating Evidence Writer

**Legacy (V2)**: Multiple evidence writers scattered across codebase

**V3 Migration**: Consolidated into `pipeline/evidence.py`
```python
# Single evidence writer class
class EvidenceWriter:
    def finalize(self, exitcode, stats):
        # Write all evidence files
        self._write_verify_report(stats)
        self._write_stamp_manifest(stats)
        self._write_audit(exitcode, stats)
        self._update_checkpoint(exitcode, stats)
```

### Example 3: Migrating Validation

**Legacy (V1)**: No validation, runtime errors

**V3 Migration**: FAIL_FAST pre-flight checks
```python
# V3: Validate before execution
def load_orders(self, order_path):
    # Header check
    if "[SSOT MANDATE]" not in content:
        raise ValueError("Missing header")

    # Banned words
    for word in BANNED_WORDS:
        if word in filename:
            raise ValueError(f"Banned word: {word}")

    # Duplicates
    if len(lines) != len(set(lines)):
        raise ValueError("Duplicate lines")

    return lines
```

## Version History

- **V1** (2026-01-17): Initial V3 migration rules
  - Defined V3 architecture characteristics
  - Established migration triggers and requirements
  - Documented forbidden and recommended patterns
  - Created compliance checklist

---

**Document ID**: V3_MIGRATION_RULES_V1
**Created**: 2026-01-17
**Status**: ACTIVE
