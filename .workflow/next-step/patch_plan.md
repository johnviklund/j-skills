Command: workflow review next-step · patch cycle 3
Created: 2026-10-30 · Claude Opus 5.5
Base:    10f7539
Inputs:  .workflow/next-step/review.md @ e4d3a58
Status:  complete

Cycle 4 approved by human (1a). C3-T1 is test-only: one commit, no red commit, and check-run.py stays unchanged.

## Execution state
Current: C3-T1 done · writer: GPT-6.1 Sol · baseline and final: workflow 109, checkup 8 passed; next review.
C3-T1 @ 3b72722 · receipts/c3-t1-verification.md

## Tickets

### C3-T1 — The Resolved-table filter has a failing test
Delivers: B4 · Blocked by: none · Lane: logic
Fixes: C3-1 (P1)
Budget: code +0 · tests +1
Seam: test_next_step.py `test_folded_resolved_findings_keep_open_ids` (:265-277) through `next-step.py --json`; check-run.py unchanged
Change: end the test's `## Resolved` table with a blank line, as every real review.md does: `+ "\n"` after the rows at test_next_step.py:271. Sites: `grep -n '## Resolved' .github/skills/workflow/scripts/tests/*.py` gives test_next_step.py:270, this one, and test_check_run.py:438, a done-run sha check whose table ends the file; it stays as is, since one test pins the filter.
Accept:
- [x] the test's `## Resolved` table is followed by a blank line before `## Cycle 2 findings`; test_next_step.py passes, 25 OK (B4)
- [x] `if text.startswith("|")` deleted from check-run.py:534 in a throwaway copy → test_next_step.py fails both subtests; the commit changes no line of check-run.py (B4)
Verify: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests -p test_next_step.py` (pre: 25 OK; deleting the filter also stays 25 OK)
Skills: none
Status: done @ 3b72722
Writer: GPT-6.1 Sol
