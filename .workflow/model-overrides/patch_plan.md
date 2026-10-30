Command: workflow review model-overrides · patch cycle 1
Created: 2026-10-30 · Opus 5.5
Base:    ad0afd9
Inputs:  .workflow/model-overrides/review.md @ ad0afd9
Status:  complete

Both tickets run in one session: `fix:logic` and `fix:mechanical` share GPT-6.1 Sol · medium.
C1-T1 is a behavioural bug: a Red commit with only the two new tests, then the fix.

## Execution state
Current: all patch tickets done; ready for review.
C1-T1 @ 5d2d876
C1-T2 @ a4135aa
writer: GPT-6.1 Sol
Red: 4b37b24, two new cases failed; only test files changed.
Final: workflow 119 tests OK; checkup 8 tests OK.
Receipt: receipts/c1-verification.md.
Uncommitted: none after state commit. Pending decision: none.

## Tickets

### C1-T1 — A done run's routing.md is history, not a live override
Delivers: B6 · Blocked by: none · Lane: logic
Fixes: C1-1 (P2)
Budget: code +3 · tests +14
Seam: `next-step.py x --json` on a done brief; `check-run.py --all` on a committed done brief
Change: in `next-step.py` read `brief` (now :117) before the override block (:107-116) and guard it with `brief.status() != "done"`; in `check-run.py:815` add `and not rep.done`. The module docstring's done-run sentence then holds as written.
Accept:
- [x] done brief + routing.md `| execute:mechanical | OpenAI · GPT-6 Sol | high |`, a key the test ROUTING.md lacks → next-step exits 0, JSON `phase` `done` (C1-1)
- [x] committed done brief + routing.md `| execute:nope | OpenAI · Sol | high |` → `check-run.py --all` prints `0 errors` (C1-1)
- [x] `test_override_bad_rows_name_key_without_json` and `test_override_validation` pass unchanged, so live runs still reject bad rows (B6)
- [x] the Red commit changes only test files and both new cases fail there; the fix commit changes no test file (C1-1)
Verify: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests && python3 -m unittest discover -s .github/skills/checkup/scripts/tests` (pre: 117 OK · 8 OK; at Red the two new cases fail)
Skills: none
Status: done @ 5d2d876
Writer: GPT-6.1 Sol

### C1-T2 — Review and execute read a run's models from its routing.md first
Delivers: B1 · Blocked by: none · Lane: mechanical
Fixes: C1-2 (P2)
Budget: code +0 · tests +0
Seam: `grep` of `phase-4-review.md` and `phase-3-execute.md` in `.github/skills/workflow/references/`
Change: `phase-4-review.md:7` becomes ``the run's `routing.md`, else `ROUTING.md`; if one matches yours, this is a``. In `phase-3-execute.md:138`, ``as `ROUTING.md`'s seat mapping names it`` becomes ``as the run's `routing.md`, else `ROUTING.md`'s seat mapping, names it``. No other line changes.
Accept:
- [x] `grep -cF 'routing.md`, else `ROUTING.md'` returns 1 in each file (C1-2)
- [x] `git diff --stat` for the ticket commit shows 1 insertion and 1 deletion in each file (C1-2)
Verify: `cd .github/skills/workflow/references && grep -cF 'routing.md`, else `ROUTING.md' phase-4-review.md phase-3-execute.md` (pre: 0 · 0)
Skills: .github/skills/agent-docs/SKILL.md
Status: done @ a4135aa
Writer: GPT-6.1 Sol
