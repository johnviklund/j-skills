Command: workflow review run-ratio-and-retire
Created: 2026-10-23 · Claude Opus 5.5
Base:    db90b60
Inputs:  .workflow/run-ratio-and-retire/review.md @ db90b60
Status:  complete

## Execution state
- Current: C1-T1 ready.

## Findings
- C1-1: the run gate reads a ticket's done sha with `re.fullmatch`, so a Status with a note after the sha skips the gate. Sites that parse `done @ <sha>` today: `check-run.py:334` (`\b`, correct), `:425` (`fullmatch`, the bug), `:724` (`\b`, correct); `.workflow/run-ratio-and-retire/scripts/replay.py` uses `startswith` and needs no change.
- Reuse: the `\b` pattern at `:334`; tests reuse `check()`, `plan()`, `lines()` and the `test_run_ratio_at_completion` table. No new helper or test method.

## Tickets

### C1-T1 — The run gate counts a done ticket whose Status carries a note
Delivers: C1-1, B1 · Blocked by: none · Lane: logic · Budget: code +1 · tests +2
Seam: check-run CLI through `check()` in `.github/skills/workflow/scripts/tests/test_check_run.py`
Accept:
- [ ] B1's run (tests +151, code added +100) with T2 `Status: done @ <sha> · T2 delegated on 2026-10-02` → ERROR containing `run: tests net +151 over 1.5× code added +100 (allowed 150)` and `1 errors` (B1)
- [ ] same run with T2 `Status: done @ <sha> (proof in receipts/t2.md)` → the same ERROR and `1 errors` (B1)
- [ ] every site in Findings C1-1 matches `done @ <sha>` followed by text; `receipts/c1-t1-replay.txt`: replay over the same 3 repos still reports `26 runs; 1 flagged`
Verify: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests -k ratio` (pre: 5 passed; the two new cases fail) and `python3 .workflow/run-ratio-and-retire/scripts/replay.py /home/john/cx-intelligence /home/john/agent-cv /home/john/j-skills`
Skills: none
Status: todo
Red: commit the new cases alone, seen failing, before the fix

## Coverage
- C1-1 → C1-T1
- Out of scope: C1-2, C1-3, C1-4 (P3, deferred), thresholds, docs, cx-intelligence and agent-cv (read only).

## Risks
- The fix must not loosen what counts as done: `todo` and `awaiting-human` cases in `test_run_ratio_at_completion` stay green.
