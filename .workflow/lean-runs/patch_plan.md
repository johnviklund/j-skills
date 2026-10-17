Command: workflow review lean-runs
Created: 2026-10-17
Base:    aafea80
Inputs:  .workflow/lean-runs/review.md @ aafea80
Status:  complete

## Execution state
- Current: C1-T1
- Baseline: 38 tests pass; check-run 0 errors. No code defect reproduces today; this is a missing assertion.

## Findings
- C1-1: T2's B5 case (contract, 2026-10-16, +76/+50) passes under both the lane gate and the legacy 3× ratio, so removing the lane gate at `check-run.py:414` stays green.
- Reuse: `RatioTests.test_committed_test_ratio`, `plan()`, `check()` and `lines()` in `test_check_run.py`. No new fixture.

## Tickets

### C1-T1 — Assert old contract tickets keep the old ratio
Delivers: C1-1, B5 · Blocked by: none · Lane: logic · Budget: code +0 · tests +2
Seam: check-run CLI through the subprocess fixtures in `.github/skills/workflow/scripts/tests/test_check_run.py`
Accept:
- [ ] `test_committed_test_ratio` gains the case contract lane, plan created 2026-10-16, code +50 · tests +151 → `0 errors` (B5)
- [ ] With `lanes = ("logic", "contract")` forced at `check-run.py:414`, that case fails; restored, all tests pass. A receipt records the mutation and result.
Verify: `python3 -B -m unittest discover -s .github/skills/workflow/scripts/tests -k RatioTests` (pre: Ran 2 tests, OK; the new case does not exist)
Skills: none · Status: todo
Test-only fix: commit just the added case. Red is the temporary mutation, not a committed failing test.

## Coverage
- C1-1 → C1-T1
- Out of scope: the P3s C1-2 to C1-4, check-run logic, docs.

## Risks
- None beyond the test file; the case adds one tuple to an existing loop.
