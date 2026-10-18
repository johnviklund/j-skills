Command: workflow review growth-ratchets
Created: 2026-10-18
Base:    c8f2e48
Inputs:  .workflow/growth-ratchets/review.md @ c8f2e48
Status:  complete

## Execution state
- Current: C2-T1 ready; review cycle 3 after it.
- Cycle 1's C1-T1 is done @ ee191dc; its text stays in git.
- Baseline: 42 tests pass; check-run --all 0 errors. No code defect reproduces today; this is a missing assertion.
- Uncommitted: none. Pending decision: none.

## Findings
- C2-1: `waiver()` keys on its kind (`check-run.py:389`), but no growth case puts one kind's line against the other check, so replacing `kind` with `(?:Ratio|Budget)` stays green.
- Sites: `waiver()` has two callers, Ratio (`check-run.py:432`) and Budget (`:422`). Each gets one wrong-kind case.
- Reuse: `test_growth_ratio_waivers` and `test_growth_budget_waivers` in `test_check_run.py` already loop over Deviations lines. No new fixture or helper.

## Tickets

### C2-T1 — Assert a waiver of one kind does not waive the other check
Delivers: C2-1, B3, B5 · Blocked by: none · Lane: logic · Budget: code +0 · tests +2
Seam: check-run CLI through the subprocess fixtures in `.github/skills/workflow/scripts/tests/test_check_run.py`
Accept:
- [ ] `test_growth_ratio_waivers` gains the case `Budget waived: T1 — wrong kind` → the T1 ratio ERROR stands (`1 errors`, no ratio waiver warn) (B3)
- [ ] `test_growth_budget_waivers` gains the case `Ratio waived: T1 — wrong kind` → the overrun warn stands (`0 errors · 1 warnings`) (B5)
- [ ] With `kind` replaced by `(?:Ratio|Budget)` at `check-run.py:389`, both new cases fail; restored, all tests pass. A receipt records the mutation and result.
Verify: `python3 -B -m unittest discover -s .github/skills/workflow/scripts/tests -k growth` (pre: Ran 4 tests, OK; neither new case exists)
Skills: none · Status: todo
Test-only fix: commit just the two added cases. Red is the temporary mutation, not a committed failing test.

## Coverage
- C2-1 → C2-T1, both callers of `waiver()`
- Out of scope: check-run logic, docs, C1-2 (deferred to TODO.md), C1-3.

## Risks
- None beyond the test file; each case adds one tuple to an existing loop.
