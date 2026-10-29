Command: workflow review next-step · patch cycle 1
Created: 2026-10-29 · Claude Opus 5.5
Base:    1aa0b47
Inputs:  .workflow/next-step/review.md @ 1aa0b47
Status:  complete

Each behavioural fix (C1-T1, C1-T2, C1-T4, C1-T5) is two commits: the reproducing test, seen failing and committed alone (`Red: <sha>`), then the fix, which leaves every test file untouched. C1-T3 is test-only.

## Execution state
Current: C1-T1–C1-T5 done. Session 5 complete; next review.
C1-T1 @ e6a8e5d · writer: GPT-6.1 Sol · workflow 100, checkup 8 passed · receipts/c1-t1-verification.md
C1-T2 @ f2bba2b · writer: GPT-6.1 Sol · workflow 101, checkup 8 passed · receipts/c1-t2-verification.md
C1-T3 @ 0762b64 · writer: GPT-6.1 Sol · workflow 105, checkup 8 passed · receipts/c1-t3-verification.md
C1-T4 @ 6e87503 · writer: GPT-6.1 Sol · workflow 106, checkup 8 passed · receipts/c1-t4-verification.md
C1-T5 @ 08048cb · writer: GPT-6.1 Sol · workflow 107, checkup 8 passed · receipts/c1-t5-verification.md
Baseline: workflow 99, checkup 8 passed. No pre-existing failure or pending decision.

## Tickets

### C1-T1 — An open fix-now finding blocks wrap, whatever its cycle
Delivers: B4, B6 · Blocked by: none · Lane: logic
Fixes: C1-1 (P1)
Budget: code +10 · tests +12
Seam: `next-step.py <slug> --json` on a fixture `review.md`; `check-run.py`'s note on the same file
Change: one predicate in check-run.py for an open finding (disposition starts `fix now`, no `Resolved: @ <sha>`). `check_review` (:579-582) and next-step use it over every cycle; next-step.py:170-172's copy goes. Sites: `grep -n 'fix now\|Disposition' .github/skills/workflow/scripts/*.py`.
Accept:
- [x] cycle 1 `### P1`, `fix now`, `Resolved: —`; empty cycle 2 findings and verdict; no patch plan → blocker naming `C1-1`, command `workflow review x` (B4)
- [x] same run, that finding stamped `Resolved: @ <base>` → phase `wrap` (B6)
- [x] `grep -c Disposition scripts/next-step.py` → 0; test_check_run.py passes unchanged (B4)
Verify: `cd .github/skills/workflow && python3 -m unittest discover -s scripts/tests && grep -c Disposition scripts/next-step.py` (pre: 99 OK · 1)
Skills: none
Status: done @ e6a8e5d
Writer: GPT-6.1 Sol
Red: 29100c5

### C1-T2 — A receipt path in backticks resumes its operator ticket
Delivers: B3 · Blocked by: none · Lane: logic
Fixes: C1-2 (P1)
Budget: code +1 · tests +8
Seam: `next-step.py <slug> --json` on a fixture `awaiting-human` ticket; next-step.py:107
Change: the receipt pattern takes an optional backtick before `receipts/`. Sites: `grep -n 'receipt:' .github/skills/workflow/scripts/*.py` (next-step.py:107 parses the path; check-run.py:337 only checks `receipt:` is there).
Accept:
- [x] Verify ``receipt: `receipts/t3.txt` — ok``, file present → phase `execute`, ticket `T3`, blocker null; file absent → blocker `T3` (B3)
- [x] the plain form `receipt: receipts/t3.txt — ok` still resumes; the existing test is unchanged (B3)
Verify: `cd .github/skills/workflow && python3 -m unittest discover -s scripts/tests -p test_next_step.py` (pre: 16 OK)
Skills: none
Status: done @ f2bba2b
Writer: GPT-6.1 Sol
Red: 93339f6

### C1-T3 — Each surviving guard in next-step.py gets a failing test
Delivers: B3, B5, B6, B8 · Blocked by: none · Lane: logic
Fixes: C1-3 (P1)
Budget: code +0 · tests +45
Seam: test_next_step.py through the CLI; next-step.py unchanged
Change: one case per mutation in review.md C1-3: wrap card holds `- **Reset:** no` · T1 `todo` blocked by T2 listed before T2 `awaiting-human` → blocker `T2` · every ticket blocked by a missing `T9` → exit 1, `no ready ticket`, no Traceback · t3 and t4 handoffs present → only t3's in T3's action and reads · Why `T3 is awaiting human action.` and `T2 is ready.` · `C2-T1` with `Fixes: C1-1 (P1)` → `Patch cycle 2 · fix C1-1` · slug `../x` → exit 1, empty stdout · `--repo` a non-git dir → exit 1, `not inside a git repo`.
Accept:
- [x] the eight cases pass, and each C1-3 mutation applied alone in a throwaway copy turns test_next_step.py red, 8 of 8 (B3, B5, B6, B8)
- [x] the commit changes no line of next-step.py (B8)
Verify: `cd .github/skills/workflow && python3 -m unittest discover -s scripts/tests -p test_next_step.py` (pre: 16 OK, 8 mutations survive)
Skills: none
Status: done @ 0762b64
Writer: GPT-6.1 Sol

### C1-T4 — A P0 operator fix keeps its lane's human approval
Delivers: B5 · Blocked by: none · Lane: logic
Fixes: C1-4 (P2)
Budget: code +3 · tests +8
Seam: `next-step.py <slug> --json` on a fixture patch ticket; next-step.py:129
Change: a P0 ticket keeps `fix:P0`'s key, seat, model and fallback and takes `approval` from `fix:<lane>`; a missing lane row exits 1 by the existing missing-key path. The test fixture gains a `fix:operator` row.
Accept:
- [x] `Fixes: C1-1 (P0)`, `Lane: operator` → key `fix:P0`, seat `Heavy executor`, model GPT-6.1 Sol · high, approval `human` (B5)
- [x] `Fixes: C1-1 (P0)`, `Lane: logic` → approval `auto`; the existing severity cases pass unchanged (B5)
Verify: `cd .github/skills/workflow && python3 -m unittest discover -s scripts/tests -p test_next_step.py` (pre: 16 OK)
Skills: none
Status: done @ 6e87503
Writer: GPT-6.1 Sol
Red: 98b36d0

### C1-T5 — A parked run resumes at the phase it stopped in
Delivers: B7 · Blocked by: none · Lane: logic
Fixes: C1-5 (P2)
Budget: code +6 · tests +8
Seam: `next-step.py <slug> --json` on a parked fixture; next-step.py:141-149, :194
Change: a parked brief's step is worked out from the run's files as if the brief were complete; then `phase` becomes `parked` and `command` keeps that step's `workflow <phase> <slug>`.
Accept:
- [x] parked brief, plan with T1 done and T2 `todo` → phase `parked`, command `workflow execute x` (B7)
- [x] parked brief, nothing else → phase `parked`, command `workflow plan x`; the existing case is unchanged (B7)
Verify: `cd .github/skills/workflow && python3 -m unittest discover -s scripts/tests -p test_next_step.py` (pre: 16 OK)
Skills: none
Status: done @ 08048cb
Writer: GPT-6.1 Sol
Red: 97427b2

## Deviations
- C1-T1: the red commit removes the erroneous earlier-cycle wrap case identified by C1-1 and adds unresolved/resolved cases. The fix commit changes no tests. Assertion lines: 49 before, 51 after; existing assertions stay unchanged. The expected-zero grep returns 1 for no matches; the content gate checks that status explicitly.
