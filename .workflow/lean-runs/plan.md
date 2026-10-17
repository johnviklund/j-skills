Command: workflow plan lean-runs
Created: 2026-10-17
Base:    b675349
Inputs:  .workflow/lean-runs/brainstorm.md @ 5ff0790
Status:  complete

Docs read: none in scope (j-skills has no PRODUCT.md or DESIGN.md)
Size: code 720 · tests 305 · ratio 0.42 · largest touched check-run.py 720, README.md 317, test_check_run.py 305 · over 1,000: none
Decisions: 1a LEAN_SINCE 2026-10-18 · 2a READMEs unchanged (B7 counts stale numbers only) · 3a tickets approved

## Execution state
Current: all tickets and C1-T1 done; review cycle 2 clean; next wrap · writer: GPT-6.1 Sol
T1 @ 3c64d1b
T2 @ c07710e
T3 @ 2b6835a
Session 1: T1, T2
Session 2: T3
Session 3: C1-T1
Session 3 baseline: 38 tests pass; check-run 0 errors, 0 warnings; no separate build or lint.
Session 2 baseline: 38 tests pass; check-run 0 errors, 0 warnings.
Baseline: 34 tests pass; check-run 0 errors, 0 warnings; no separate build or lint.
Uncommitted: none for this run; pre-existing test __pycache__/ remains untracked.
Pending decision: none.

## Findings
| # | What is true | What it changes |
|---|---|---|
| F1 | The skill lives at `.github/skills/workflow/`; `skills/workflow` is a symlink to it | Every path and Verify uses `.github/skills/workflow/` |
| F2 | `SKILL.md:88-89` wraps "≤ 15" and "behaviours" across two lines, so a line grep misses it | T3's count joins lines first (`tr '\n' ' '`) |
| F3 | Stale numbers today: `SKILL.md:88` "15 behaviours", `phase-0-brainstorm.md:143` "5–15", `phase-2-plan.md:29` and `tests.md:79-80` "3×"; the check-run docstring says "5-15" | T3 edits the four docs; T1 edits the docstring |
| F4 | Neither README states a behaviour, acceptance-line or ratio limit | B7 checks only that no stale number remains; READMEs stay unchanged (decision 2a) |
| F5 | `Doc.slop_gated(since)` (check-run.py:141) already gates by `Created:` date | Reuse it with a new `LEAN_SINCE`; no new gate helper |
| F6 | `Cycle N approved by human:` match at check-run.py:488-489 | `Split declined by human:` uses the same regex shape |
| F7 | `field(t, "Budget")` stops at `· why:`, and `field(t, "why")` returns the reason | D9 works with the existing parser |
| F8 | `check_overrun` errors only for `logic`, at `TEST_RATIO = 3` | T2 keeps 3×/logic before `LEAN_SINCE`, 1.5×/logic+contract from it (B5) |
| F9 | Reuse in tests: `check()`, `plan()`, `sized()`, `lines()` in test_check_run.py | New tests build on them; no new fixture module |
| F10 | `LEAN_SINCE = 2026-10-18` keeps this run (created 2026-10-17) and all earlier runs on today's rules | Decision 1 |
| F11 | Count rule and ratio rule sit in one module and lane but need 8 acceptance lines | Two tickets, not one: the 6-line cap wins over the ~40-line merge rule |

## Tickets

### T1 — Run size limits: 8 behaviours, 20 acceptance lines
Delivers: B1, B2, B5 · Blocked by: none · Lane: logic
Budget: code +35 · tests +35
Seam: `check-run.py` run as a subprocess on fixture runs (`check()` in test_check_run.py)
Accept:
- [x] Brief created 2026-10-18, 9 behaviours, no `Split declined by human:` → ERROR naming `9 behaviours` and `8` (B1)
- [x] The same brief with `Split declined by human: 2026-10-18`, and a 1-behaviour brief → no behaviours ERROR, no behaviours warning (B1)
- [x] Complete plan, 21 acceptance lines across tickets → ERROR naming `21 acceptance lines` and `20` (B2)
- [x] 20 lines, and 21 lines with `Split declined by human:` → no acceptance-count ERROR (B2)
- [x] Brief with 9 behaviours and plan with 21 lines, both created 2026-10-16 → `0 errors` (B5)
Verify: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests -k LimitTests` (pre: NO TESTS RAN)
Skills: none
Status: done @ 3c64d1b
Writer: GPT-6.1 Sol

### T2 — Tests within 1.5× code, Budget reasons
Delivers: B3, B4, B5 · Blocked by: T1 · Lane: logic
Budget: code +30 · tests +30
Seam: `check-run.py` run as a subprocess on fixture runs with a committed `done @` ticket
Accept:
- [x] Contract and logic lanes, plan created 2026-10-18, commit code +50 · tests +76 → ERROR `tests +76 over 1.5× code +50` (B3)
- [x] The same commit with tests +75 → no ratio ERROR, both lanes (B3)
- [x] `Budget: code +60 · tests +120`, no `why:` → warn naming `tests +120` and `code +60`; with `· why: x` → no warn (B4)
- [x] Contract lane, plan created 2026-10-16, code +50 · tests +76 → `0 errors` (B5)
Verify: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests -k RatioTests` (pre: NO TESTS RAN)
Skills: none
Status: done @ c07710e
Writer: GPT-6.1 Sol

### T3 — Docs state the new limits, one test per behaviour
Delivers: B6, B7, B8 · Blocked by: T1, T2 · Lane: mechanical
Seam: the workflow docs, counted with grep
Accept:
- [x] `grep -c "Each acceptance line is one test" references/phase-2-plan.md` → 0; `grep -c "one test per behaviour"` there → ≥ 1 (B6)
- [x] phase-2-plan.md's *Inherited semantics* bullet contains "at risk" (B6)
- [x] Workflow `*.md` and root README, minus SKILL-IMPACT/WORKLOG, lines joined: "15 behaviours", "5–15", "3×" → 0 (B7)
- [x] `SKILL.md` contains "8 behaviours" and "20 acceptance lines"; `tests.md` contains "1.5×" (B7)
- [x] `receipts/t3-net-lines.txt`: numstat of workflow `*.md` minus SKILL-IMPACT/WORKLOG, b675349..HEAD → net ≤ 0 (B8)
Verify: `W=.github/skills/workflow; grep -c "Each acceptance line is one test" $W/references/phase-2-plan.md; ls $W/*.md $W/references/*.md README.md | grep -vE 'SKILL-IMPACT|WORKLOG' | xargs cat | tr '\n' ' ' | tr -s ' ' | grep -oE '15 behaviours|5–15|3×' | wc -l` (pre: 1 · 5)
Skills: none
Status: done @ 2b6835a
Writer: GPT-6.1 Sol

## Coverage
- Outcome → T1, T2 (check-run ERRORs on the next run's brief, plan and ticket commits) · T3 (plan reference asks one test per behaviour)
- B1 → T1 · B2 → T1 · B3 → T2 · B4 → T2 · B5 → T1, T2 · B6 → T3 · B7 → T3 · B8 → T3
- Out of scope: `check_worklog` bug, ratchets/simplify/retiring, patch-plan sizing, cx-intelligence edits, tickets per session → untouched

## Risks
- T2: two ratio rules by date in one function; a wrong gate turns old runs red (B5's line guards it).
- check-run's ERRORs gate every phase's commit, so a false ERROR blocks the next cx-intelligence run.
- Not taken: one combined ticket (8 acceptance lines, over the cap of 6).

## TODO impacts
none (D1 keeps the `check_worklog` item out)

## Product doc impacts
No PRODUCT.md, DESIGN.md or ROADMAP.md at repo root. `.github/skills/workflow/ROADMAP.md`: no changes.

## Deviations
- T3 also aligns execute’s Red step with behaviour tests; its old per-acceptance instruction contradicted B6.
