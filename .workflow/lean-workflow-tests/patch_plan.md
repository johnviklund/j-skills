Command: workflow review lean-workflow-tests · patch cycle 1
Created: 2026-10-31 · Opus 5.5
Base:    6c5a986
Inputs:  .workflow/lean-workflow-tests/review.md @ 6c5a986
Status:  complete

One mechanical ticket. It removes dead test code only; no assertion and no expected value changes, so it needs no Red commit.

## Execution state
Current: C1-T1 done; ready for review.
C1-T1 @ 961deed
writer: GPT-6.1 Sol
Baseline: workflow 112 tests in 51.373s OK; checkup 8 tests in 0.423s OK.
Final suites: workflow 112 tests in 51.784s OK; checkup 8 tests in 0.423s OK.
Content checks: no created parameters or expected_code; AST finds no unread result assignments.
Assertion calls: 87 · 78 · 126 before and after; expected values unchanged.
Reuse: existing run_command still checks each call; no new helper needed.
Mutation: none — mechanical ticket.
Uncommitted files: none. Pending decision: none.

## Tickets

### C1-T1 — Drop the dead parameters and bindings the folds left
Delivers: B1, B2, B3 · Blocked by: none · Lane: mechanical
Fixes: C1-1 (P2)
Budget: code +0 · tests +0
Seam: the three test files only
Change: `test_check_run.py` remove `created` from `review()` :391 and `run_review()` :421-422; `test_next_step.py:122` loop over keys only and assert `result.returncode` against `0` in the `review` branch; `test_run_worktree.py` drop `result = ` at :66, 72, 85, 115, 122, 132, 147, 268, 296, 313 and keep the call.
Accept:
- [x] `grep -nE 'def (review|run_review)\(.*created' test_check_run.py` → no match; `grep -c expected_code test_next_step.py` → 0 (C1-1)
- [x] an AST scan of `test_run_worktree.py` → no `result` assignment left unread (C1-1)
- [x] workflow suite → `Ran 112 tests` OK; assertion calls per file unchanged: 87 · 78 · 126 by `grep -cE 'self\.assert|self\.fails'` (C1-1)
Verify: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests && python3 -m unittest discover -s .github/skills/checkup/scripts/tests` (pre: 112 OK · 8 OK)
Skills: none
Status: done @ 961deed
Writer: GPT-6.1 Sol
