Command: workflow review slop-guards
Created: 2026-10-08
Base:    752ad6be9407e21c684b5345dbcfc0121c7e1e36
Inputs:  patch_plan.md @ 5c8f68a5e673e5fbc493060d8283fbe5bd2fb868
Status:  complete

## Scope and regression checks
- Reviewed `git diff 5c8f68a..752ad6b -- .github/skills/workflow/scripts` and both affected functions' dispatch paths.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s .github/skills/workflow/scripts/tests -v`: exit 0, 20 tests, OK.
- AST comparison against 5c8f68a: all 16 original test methods unchanged; assertion calls 18 before, 23 after.
- `git show --stat bc114fc` and `git show --stat 0e888de`: each changes only check-run.py; no test edits.
- `git diff --numstat 85b5b9e..752ad6b -- . ':(exclude).workflow'`: code +90/-3, tests +208/-0, net +295, ratio 2.31.
- Patch totals from 5c8f68a: code +5/-4, tests +22/-0, net +23. Largest touched files are 650 and 208 lines.
- Added-line escape-hatch scan: 0 matches. Tracked non-receipt dependency scan outside run folders: 0 matches.
- `git diff --check`: exit 0.

## CLI checks across the finding classes
Used the existing fixture module's `check`, `plan` and `BRIEF` in a one-off Python command. Each call creates a fresh temporary Git repository and runs the real CLI.
- Risk: missing, empty, whitespace-only, cheap, costly and irreversible in each of plan.md and patch_plan.md. All 12 cases print a summary without a traceback; only the first three emit the missing Risk warning.
- Budget: missing, empty, whitespace-only and valid zero in each of logic and contract T1 tickets, with +101 code lines. All 8 cases print a summary. Only zero emits the overrun warning; the other values emit the missing Budget warning.
- Zero budget with +101 code lines: pre-gate Created date and a stated deviation each suppress the warning. Both cases report 0 errors and 0 warnings.
Total: 22 cases pass. The suite separately verifies that receipt-only additions against zero remain clean.

## Historical failures and mutation
Created a detached worktree at 752ad6b under /private/tmp; tests remained unchanged throughout. Set PYTHONDONTWRITEBYTECODE=1.
- Replaced only check-run.py with its version at 6e8efc9, then ran `python3 -m unittest discover -s .github/skills/workflow/scripts/tests -k risk_empty`: exit 1, 1 test, 2 failures, one for each plan file.
- Replaced only check-run.py with its version at dd167fe, then ran the same command with `-k budget_values`: exit 1, 3 tests, 3 failures for empty logic, empty contract and zero overrun. The receipt-only case passes.
- Restored HEAD and inverted `if parts and net > OVERRUN * budget:` to use `<=`. Ran `-k budget_values`: exit 1, 3 tests, 2 failures for zero overrun and receipt-only additions.
- Restored the original checker; `git status --short` in the worktree is empty. No mutation was committed.

## Artifact validation
`python3 .github/skills/workflow/scripts/check-run.py --all` after completing cycle 2: 0 errors, 1 existing plan-length warning, no open fix-now findings, 0 repository warnings.
