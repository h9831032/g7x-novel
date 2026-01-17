# Git Dangerous Command Ban List V1

## Overview
This document lists git commands that are **BANNED** or **REQUIRE EXPLICIT CONFIRMATION** in G7X workflows when using Claude Code or automation scripts.

## Philosophy

G7X follows the **evidence-first, safety-second** principle:
- All changes must be traceable
- Destructive operations must be reversible or explicitly confirmed
- Automation should never silently destroy work
- "Measure twice, cut once" approach to git operations

## Tier 1: ALWAYS BANNED (Never Auto-Execute)

These commands are **absolutely prohibited** without explicit user confirmation:

### 1. Force Push to Protected Branches
```bash
git push --force origin main
git push --force origin master
git push -f origin main
git push -f origin master
```

**Why banned**: Destroys remote history, breaks collaboration, irreversible.

**Safe alternative**: Create new branch or PR instead of rewriting main/master.

### 2. Hard Reset Without Safety Net
```bash
git reset --hard HEAD~N
git reset --hard <commit>
```

**Why banned**: Destroys uncommitted work, irreversible.

**Safe alternative**:
```bash
# Create safety branch first
git branch safety-backup
git reset --hard <commit>
```

### 3. Clean Working Directory
```bash
git clean -fd
git clean -fdx
```

**Why banned**: Deletes untracked files permanently.

**Safe alternative**:
```bash
# List what would be deleted first
git clean -fdn
# Then user manually confirms deletion
```

### 4. Branch Deletion (Remote)
```bash
git push origin --delete branch-name
git push origin :branch-name
```

**Why banned**: Remote branch deletion affects all collaborators.

**Safe alternative**: User deletes via GitHub UI or manual confirmation.

### 5. Rebase with Force
```bash
git rebase -i --force
git rebase --onto <newbase> <upstream> <branch>
```

**Why banned**: Rewrites history, can cause conflicts for collaborators.

**Safe alternative**: Only rebase local, unpushed branches with explicit confirmation.

## Tier 2: REQUIRE CONFIRMATION (Auto-Execute Only with User Approval)

These commands are **allowed but require explicit confirmation**:

### 1. Commit Operations
```bash
git commit -m "message"
git commit --amend
```

**Confirmation required**: "Should I create a commit with message 'X'?"

**Why**: Commits affect project history, user should approve message.

**Auto-approve exception**: If user explicitly says "commit these changes with message X".

### 2. Push Operations (Non-Force)
```bash
git push origin branch-name
git push
```

**Confirmation required**: "Should I push branch X to remote?"

**Why**: Pushes make changes public, user should confirm intent.

**Auto-approve exception**: Batch scripts that explicitly request push.

### 3. Branch Creation
```bash
git checkout -b new-branch
git branch new-branch
```

**Confirmation required**: "Should I create branch 'new-branch'?"

**Why**: Branch names should follow conventions (e.g., cc/YYYYMMDD_description).

**Auto-approve exception**: If branch name follows G7X convention.

### 4. Merge Operations
```bash
git merge branch-name
git merge --no-ff branch-name
```

**Confirmation required**: "Should I merge branch X into current branch?"

**Why**: Merges affect branch history, may cause conflicts.

**Auto-approve exception**: Never (always require confirmation).

### 5. Stash Operations with Pop
```bash
git stash pop
git stash apply
```

**Confirmation required**: "Should I apply stashed changes?"

**Why**: May cause merge conflicts with current work.

**Auto-approve exception**: If script explicitly handles conflicts.

## Tier 3: SAFE (Auto-Execute Without Confirmation)

These commands are **safe and can be auto-executed**:

### Read-Only Operations
```bash
git status
git status --short
git log
git log --oneline
git diff
git diff --cached
git show <commit>
git branch
git branch -a
git remote -v
```

**Why safe**: Read-only, no state changes.

### Safe Write Operations
```bash
git add <file>
git add .
git stash
git stash save "message"
git fetch
git fetch --all
```

**Why safe**:
- `git add`: Staging is reversible (`git reset`)
- `git stash`: Saves work temporarily, reversible
- `git fetch`: Only downloads data, doesn't modify working tree

## Special Cases

### Case 1: Amend Last Commit
```bash
git commit --amend --no-edit
git commit --amend -m "new message"
```

**Rule**: ONLY allowed if:
1. Commit was created in current session by Claude/user
2. Commit has NOT been pushed to remote
3. User explicitly requested amend

**Check before amend**:
```bash
# Verify commit is unpushed
git log origin/branch..HEAD --oneline
# Should show the commit to be amended
```

### Case 2: Interactive Rebase
```bash
git rebase -i HEAD~N
```

**Rule**: ALWAYS BANNED in automation.

**Why**: Requires interactive input, complex conflict resolution, high risk.

**Safe alternative**: User performs manually.

### Case 3: Cherry-Pick
```bash
git cherry-pick <commit>
```

**Rule**: REQUIRE CONFIRMATION.

**Why**: May cause conflicts, affects history.

**Confirmation**: "Should I cherry-pick commit X onto current branch?"

## Detection Patterns

Claude Code and automation scripts should detect these patterns:

### Pattern 1: Force Flag Detection
```regex
git\s+push\s+.*(-f|--force)
git\s+rebase\s+.*--force
```

**Action**: REJECT with error message.

### Pattern 2: Destructive Reset
```regex
git\s+reset\s+--hard
git\s+clean\s+-[fdx]+
```

**Action**: REJECT with error message.

### Pattern 3: Branch Deletion
```regex
git\s+branch\s+-[dD]
git\s+push\s+.*--delete
```

**Action**: REQUIRE CONFIRMATION.

### Pattern 4: History Rewrite
```regex
git\s+rebase\s+-i
git\s+commit\s+--amend
git\s+filter-branch
```

**Action**: REQUIRE CONFIRMATION + safety checks.

## Error Messages

When banned command is detected, show helpful error:

```
[GIT_DANGER] Command rejected: git push --force origin main

This command is BANNED because it destroys remote history.

Safe alternatives:
1. Create new branch: git checkout -b fix-branch
2. Push new branch: git push origin fix-branch
3. Create PR for review

If you absolutely must force-push, do it manually with explicit confirmation.
```

## G7X Workflow Integration

### Safe Git Flow for G7X
```bash
# 1. Create feature branch (auto-approve if follows convention)
git checkout -b cc/20260117_feature_name

# 2. Make changes and stage (auto-approve)
git add file1.py file2.py

# 3. Commit (REQUIRE CONFIRMATION)
git commit -m "feat: add feature X"
# Confirmation: "Should I create commit with message 'feat: add feature X'?"

# 4. Push (REQUIRE CONFIRMATION)
git push -u origin cc/20260117_feature_name
# Confirmation: "Should I push branch cc/20260117_feature_name to remote?"

# 5. Create PR (manual via GitHub UI)
```

### Auto-Approve Script Pattern
For batch scripts (e.g., run_real24_skeleton.ps1), git operations are allowed if:
1. User explicitly requested batch execution
2. Branch name follows G7X convention
3. NO force operations involved
4. Evidence files are generated before commit

## Exceptions and Overrides

### Emergency Recovery Scenarios

In case of emergency (e.g., corrupt state, urgent hotfix), user can:

1. **Temporarily disable git safety checks** (manual override):
   ```bash
   # User runs command manually, bypassing automation
   git reset --hard origin/main
   ```

2. **Use recovery branch** before destructive operation:
   ```bash
   git branch recovery-$(date +%Y%m%d_%H%M%S)
   git reset --hard <target>
   ```

3. **Document override** in evidence:
   ```
   [OVERRIDE] Executed banned command: git reset --hard
   Reason: Recovery from failed merge
   Evidence: recovery-20260117_143000 branch created
   ```

## Version History

- **V1** (2026-01-17): Initial git danger command ban list
  - Defined three-tier ban system
  - Listed banned, restricted, and safe commands
  - Established detection patterns
  - Documented G7X git workflow
  - Created error message templates

---

**Document ID**: GIT_DANGER_CMD_BAN_V1
**Created**: 2026-01-17
**Status**: ACTIVE
