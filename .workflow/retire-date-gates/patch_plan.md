Command: workflow review retire-date-gates
Created: 2026-10-21 · Claude Opus 5.5
Base:    188f48a
Inputs:  .workflow/retire-date-gates/review.md @ 188f48a
Status:  complete

## Execution state
- Current: C1-T1 done; C1-T2 ready.
- C1-T1 @ fbb1fdc
- C1-T1 red @ 380c292
- writer: GPT-6.1 Sol
- Verification: 49 tests pass; --all has 0 errors and 0 warnings.
- Reuse: parse_tickets, field, git_has, Report.missing_sha; no helper added.
- Baseline: 47 tests pass; `check-run.py --all` 0 errors.

## Findings
- C1-1: done runs skip every `@ <sha>` pointer outside the header. Sites today: check-run.py:336-337 (ticket `done @`), 538-539 (finding `Resolved: @`), 550-552 (`## Resolved` table).
- C1-2: `strict` at check-run.py:197 includes `parked`; only the behaviour limit (209) needs it.
- Reuse: `git_has`, `rep.missing_sha`, `SHA`, `Doc`; tests reuse `check()`, `plan()`, `BRIEF`, `review()`. No new fixture helper.

## Tickets

### C1-T1 — A done run still warns on dangling ticket and Resolved shas
Delivers: C1-1, B5 · Blocked by: none · Lane: logic · Budget: code +12 · tests +12 · why: one test per pointer kind
Seam: check-run CLI through `check()` in `.github/skills/workflow/scripts/tests/test_check_run.py`
Accept:
- [x] committed done brief + plan with `T1 … done @ deadbee`, `--all` → `warn … T1: done @ deadbee is not a commit` and `0 errors` (B5)
- [x] committed done brief + review.md with `Resolved: @ deadbee` and a `## Resolved` row `@ deadbee`, `--all` → both warn, `0 errors`, no rule check message such as `Size:` (B5)
- [x] every site listed in Findings C1-1 is covered for done runs: plan.md, patch_plan.md, review.md
Verify: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests` (pre: 47 passed; the new cases fail)
Skills: none
Status: done @ fbb1fdc
Writer: GPT-6.1 Sol
Red: commit the new test alone, seen failing, before the fix

### C1-T2 — A parked draft brief warns on missing sections; the behaviour limit still errors
Delivers: C1-2, B6 · Blocked by: none · Lane: logic · Budget: code +2 · tests +8
Seam: check-run CLI through `check()` in `.github/skills/workflow/scripts/tests/test_check_run.py`
Accept:
- [ ] parked brief with `## Parked`, no `## Outcome` → `warn … missing section` and `0 errors` (B6)
- [ ] `test_parked_brief_uses_the_same_limit` still passes: 9 behaviours parked → ERROR `9 behaviours; at most 8` (B6)
Verify: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests` (pre: 47 passed; the new case fails)
Skills: none
Status: todo
Red: commit the new test alone, seen failing, before the fix

## Coverage
- C1-1 → C1-T1 · C1-2 → C1-T2
- Out of scope: C1-3 (P3, deferred), thresholds, docs, cx-intelligence runs.

## Risks
- C1-T1 must not bring back rule checks for done runs: the second acceptance line asserts a rule message stays absent.
