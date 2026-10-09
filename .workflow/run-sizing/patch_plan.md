Command: workflow review run-sizing
Created: 2026-10-10
Base:    e1bc18b8792c33efbb8c8930b3914c8c012e4f28
Inputs:  .workflow/run-sizing/review.md @ e1bc18b8792c33efbb8c8930b3914c8c012e4f28
Status:  complete

## Execution state
- Current: C1-T2 (todo, mechanical · medium)
- C1-T1 @ 36b844d
- writer: Opus 5.5 — outside the executor chain; review must stay OpenAI or note degraded
- Session 2 recorded in `plan.md` (the run-wide ledger C1-T2 sets up)
- Baseline: 30 tests pass; no production-code defect reproduced. Now 31.
- Uncommitted: none · Pending decision: none
- Verification: `receipts/c1-verification.md` records both findings and current command results.

## Findings
- C1-1: B4's six-line success case is missing from the test suite; a boundary mutation survives.
- C1-2: execute writes patch sessions into the active patch plan, while wrap counts only the original plan.
- Reuse: `SizingTests`, `plan(accept=...)`, and `check(...)` already provide the subprocess test seam. Add no fixture or abstraction.
- Session sites: phase-3-execute.md lines 10, 45, 67, 101–105; wrap.md lines 139–140, 147–148; learning-worklog.md line 106.

## Tickets

### C1-T1 — Assert that six acceptance lines pass
Delivers: C1-1, B4 · Blocked by: none · Lane: logic · Budget: code +0 · tests +6
Seam: check-run CLI through the existing subprocess fixtures in `.github/skills/workflow/scripts/tests/test_check_run.py`
Accept:
- [x] `test_sizing_six_acceptance_lines_are_valid`: a six-line ticket reports `0 errors`; the existing seven-line rejection still passes.
- [x] The `< ACCEPT_MAX` mutation fails the new test; restored code passes all tests. Record the mutation and result in a receipt.
Verify: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests -k six_acceptance` (pre: Ran 0 tests, OK)
Skills: none · Status: done @ 36b844d
Writer: Opus 5.5
This is a test-coverage fix. Production behavior already passes B4. Use a temporary mutation for red, restore it, and commit only the added assertion.

### C1-T2 — Keep patch sessions in the run's session ledger
Delivers: C1-2, B9, B11 · Blocked by: none · Lane: mechanical
Seam: `.github/skills/workflow/references/phase-3-execute.md` and `references/wrap.md`, checked by content and a session trace
Accept:
- [ ] Execute says `Session ledger: plan.md` and records normal and patch sessions there, preserving entries and continuing N across patch cycles.
- [ ] Wrap says its count `includes patch sessions`; a trace with one initial session and two patch sessions reports 3 before cleanup.
Verify: `grep -c 'Session ledger: plan.md' .github/skills/workflow/references/phase-3-execute.md; grep -c 'includes patch sessions' .github/skills/workflow/references/wrap.md` → 1, 1 (pre: 0, 0)
Skills: .github/skills/agent-docs/SKILL.md · Status: todo
Replace the existing session instructions. Ticket status and commit records stay in the active plan; only the session ledger is run-wide.
This is a document correction: verify the text and save the trace in receipts; no source-text unit test or new script.

## Coverage
- C1-1 → C1-T1 · C1-2 → C1-T2
- Out of scope: production checker logic, model routing, ticket limits, and review-cycle policy.

## Risks
Keep earlier session entries when a new patch cycle replaces its plan. Count each execute session once.

## TODO impacts
None.

## Product doc impacts
Only the execute and wrap references need correction.
