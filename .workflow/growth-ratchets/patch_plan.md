Command: workflow review growth-ratchets
Created: 2026-10-18
Base:    c4ce7f0
Inputs:  .workflow/growth-ratchets/review.md @ c4ce7f0
Status:  complete

## Execution state
- Current: C1-T1
- Baseline: 42 tests pass; check-run --all 0 errors. No code defect reproduces today; this is a missing assertion.

## Findings
- C1-1: `waiver()` matches the ticket ID (`check-run.py:389`), but no growth case names another ticket, so loosening the key to `T\d+` stays green.
- Reuse: `RatioTests.test_growth_ratio_waivers`, `plan()`, `check()` and `lines()` in `test_check_run.py`. No new fixture.

## Tickets

### C1-T1 — Assert a waiver for another ticket does not waive T1
Delivers: C1-1, B3 · Blocked by: none · Lane: logic · Budget: code +0 · tests +1
Seam: check-run CLI through the subprocess fixtures in `.github/skills/workflow/scripts/tests/test_check_run.py`
Accept:
- [ ] `test_growth_ratio_waivers` gains the case `Ratio waived: T2 — other ticket` → the T1 ratio ERROR stands (`1 errors`, no waiver warn) (B3)
- [ ] With `re.escape(tid)` replaced by `r"T\d+"` at `check-run.py:389`, that case fails; restored, all tests pass. A receipt records the mutation and result.
Verify: `python3 -B -m unittest discover -s .github/skills/workflow/scripts/tests -k growth` (pre: Ran 4 tests, OK; the new case does not exist)
Skills: none · Status: todo
Test-only fix: commit just the added case. Red is the temporary mutation, not a committed failing test.

## Coverage
- C1-1 → C1-T1
- Out of scope: C1-2 (deferred to TODO.md), C1-3, check-run logic, docs.

## Risks
- None beyond the test file; the case adds one tuple to an existing loop.
