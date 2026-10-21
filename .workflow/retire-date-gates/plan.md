Command: workflow plan retire-date-gates
Created: 2026-10-21 · Claude Opus 5.5
Base:    6a2dec0
Inputs:  .workflow/retire-date-gates/brainstorm.md @ 6a2dec0
Status:  complete

Docs read: none in scope (no PRODUCT.md or DESIGN.md in this repo)
Decisions: 1a (a done run is history once its `done` status is committed) · ticket list approved 2026-10-21
Size: code 794 · tests 436 · ratio 0.55 · largest touched check-run.py 794, test_check_run.py 436 · over 1,000: none

## Execution state
Current: T1 and T2 done; ready for cross-vendor review.
T1 @ fc99027
T2 @ 281f4a9
writer: GPT-6.1 Sol
Session 1: T1, T2
Baseline: 44 passed; T1 and T2 final suites: 47 passed each; no baseline failures.
No separate build, lint or typecheck declared; --all and T2 content checks passed.
Reuse: Report.done and git_out; no helper added.
Receipts: receipts/t1-verification.md, receipts/t2-verification.md
Uncommitted: none after ledger commit. Pending decision: none; push approved by user 2026-10-21 (1a).
Limit: Copilot registration check could not start; launcher DNS failed.

## Findings
| # | What is true | What it changes |
|---|---|---|
| F1 | Ungating every `*_SINCE` (scratch copy, `--all`) gives exactly 6 errors: run-sizing 1 (12 behaviours), slop-guards 5 (15 behaviours, T1 ratio, 32 acceptance lines, WORKLOG Seats and Skills) | confirms D1's count |
| F2 | The Retired: and WORKLOG checks fire only on a done `wrap.md` (check-run.py:591-599), and wrap 9a sets `brainstorm.md` done in the same commit (wrap.md:159), so D1's skip keyed on `Report.done` would switch both checks off for every future run | decision 1a: `Report.done` needs the brief done and committed; T1 |
| F3 | The tests never see that state: wrap fixtures pair a done `wrap.md` with a complete brief (test_check_run.py:384-414) | T1 adds a fixture with the brief done too |
| F4 | `phase-2-plan.md:32` also says "From 2026-10-18" and is missing from B7's doc list | T2 edits it; B7's grep covers it |
| F5 | `agent-docs/SKILL.md:151` already states "no start dates" and "finished runs are skipped unless `--all`"; under D1 `--all` shows them but runs no rule checks | T2 adjusts that sentence |
| F6 | `deviated()` (check-run.py:387) exists only for the pre-GROWTH branch; `LEGACY_TEST_RATIO` only for pre-LEAN; `BEHAVIOURS_MIN/MAX` only for the pre-LEAN brief branch | all removed in T1 (D4) |
| F7 | Reuse: `Report.done` (check-run.py:83, set at 713) is the only done flag; `git_out` (682) runs git | the gate reuses both; no new helper |
| F8 | Baseline: `python3 -m unittest discover -s scripts/tests` → 44 passed; date-pinned tests at test_check_run.py:109-237, 279-280, 374-375 | rewritten to dateless cases, not added to |

## Tickets

### T1 — One rule set for every run not yet done
Delivers: B1, B2, B3, B4, B5, B6 · Blocked by: none · Lane: logic
Budget: code +25 · tests +60 · why: replaces date-pinned cases and adds the uncommitted-done fixture (F3, F8)
Seam: `check-run.py` as a subprocess on fixture repos (`scripts/tests/test_check_run.py`, `check()`)
Accept:
- [x] plan Created 2026-10-08, logic T2 without Budget → `T2: no Budget: line` warning (B1)
- [x] brief Created 2026-10-08 with 9 behaviours → ERROR `9 behaviours; at most 8`; 4 behaviours → no `behaviours;` message (B2)
- [x] plan Created 2026-10-08, done logic T1 with tests net +76, code +50, bare `T1:` deviation → ERROR `tests net +76` (B3)
- [x] review Created 2026-10-09 with a Cycle 3 and no approval → ERROR `cycle 3 needs` (B4)
- [x] brief committed done, 9 behaviours, `--all` → `0 errors`; same brief done but uncommitted, done wrap without Retired → ERROR `no Retired:` (B5)
- [x] parked brief with `## Parked` and 9 behaviours → ERROR `9 behaviours; at most 8` (B6)
Verify: `python3 -m unittest discover -s skills/workflow/scripts/tests` (pre: 44 passed)
Skills: none
Status: done @ fc99027
Writer: GPT-6.1 Sol

### T2 — Docs drop the start dates
Delivers: B7 · Blocked by: T1 · Lane: mechanical
Budget: code +0 · tests +0
Seam: check-run.py docstring, `references/tests.md`, `phase-3-execute.md`, `phase-2-plan.md`, `MAINTAINING.md`, `agent-docs/SKILL.md:151`
Accept:
- [x] grep `_SINCE|LEGACY_TEST_RATIO|slop_gated` in check-run.py → 0 matches (B7)
- [x] grep -i `older plans|earlier plans|from 2026|keep their rules` in the four docs and check-run.py → 0 matches (B7)
- [x] `MAINTAINING.md` says the rule checks apply to `every run not yet done` → 1 match (B7)
- [x] `agent-docs/SKILL.md` says finished runs get `header, sha and layout checks only` → 1 match (B7)
Verify: `! grep -nE "_SINCE|LEGACY_TEST_RATIO|slop_gated" skills/workflow/scripts/check-run.py && ! grep -niE "older plans|earlier plans|from 2026|keep their rules" skills/workflow/references/{tests,phase-3-execute,phase-2-plan}.md skills/workflow/MAINTAINING.md skills/workflow/scripts/check-run.py && grep -c "every run not yet done" skills/workflow/MAINTAINING.md && grep -c "header, sha and layout checks only" skills/agent-docs/SKILL.md` (pre: fails, 9 date lines and 0 MAINTAINING match)
Skills: skills/agent-docs/SKILL.md
Status: done @ 281f4a9
Writer: GPT-6.1 Sol

## Coverage
- Outcome → T1 (rules on every run not done, on the checker's output) · T2 (docs)
- B1 → T1 · B2 → T1 · B3 → T1 · B4 → T1 · B5 → T1 · B6 → T1 · B7 → T2
- Out of scope: run-level ratio gate, simplify pass → untouched · thresholds (8, 20, 1.5×) → untouched · finished and cx-intelligence runs → untouched · TODO.md → untouched

## Risks
- T1: the "done once committed" gate calls `git status` per run; a dirty done brief on an old run (a typo fix) would show its rule errors until committed.
- Removing `deviated()` makes a bare `## Deviations` mention stop skipping the overrun check on any live plan; none is live today.
- Option not taken: exempt the wrap checks from D1 (1b), which left 2 permanent errors on slop-guards.

## TODO impacts
none (the brief names no TODO.md item)

## Product doc impacts
- PRODUCT.md, DESIGN.md: absent in this repo.
- ROADMAP.md (skills/workflow/ROADMAP.md): step 2 is delivered by this run; wrap marks it done.

## Deviations
- T1: existing date-exemption and legacy-ratio assertions now assert the approved universal rules; assertions 61 → 66.
- T1: clean fixture Budgets now give a reason for larger test budgets; existing clean assertions remain unchanged.
- T1: the old plan-limit fixture now isolates acceptance lines instead of also exceeding the behaviour limit.
- T2: Copilot registration and CLI trigger checks remain unverified; launcher could not resolve its download hosts. Triggers unchanged.
- Handoff: automatic approval review initially rejected git push origin main; the user explicitly approved it with 1a on 2026-10-21.
