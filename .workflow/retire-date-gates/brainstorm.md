Command: workflow brainstorm retire-date-gates
Created: 2026-10-21 · Sonnet 5.5
Base:    118ec61
Inputs:  none
Status: done

## Problem
`check-run.py` picks the rules for a run from its `Created:` date (`SLOP_SINCE`, `SIZING_SINCE`, `LEAN_SINCE`, `GROWTH_SINCE`) and keeps legacy branches for older runs. A rule shipped today silently skips today's runs, and the user found this confusing (ROADMAP step 2).

## Outcome
`python3 skills/workflow/scripts/check-run.py` applies one rule set to every run that is not `done`, whatever its `Created:` date. Done runs keep header, sha and layout checks only. The docs no longer say "earlier plans keep their rules".

## Behaviours
- B1 — a plan created before 2026-10-09 with a logic ticket and no `Budget:` line → the same warning a new plan gets
- B2 — a complete brief with 9 behaviours and no `Split declined by human:` → error, whatever its date; a brief with 4 behaviours → no warning
- B3 — a done logic ticket with tests net +76 over code +50 → error unless `Ratio waived: T# — <reason>`, whatever the plan's date; a bare mention of the ticket under `## Deviations` no longer skips the Budget check
- B4 — a review with a third cycle and no `Cycle 3 approved by human:` → error, whatever its date
- B5 — a run whose brief is `done` → none of B1–B4 fire under `--all`; a dangling sha or stray top-level file still reports
- B6 — a parked run with a complete-looking plan → checked exactly like a live run (no special case)
- B7 — grep of `check-run.py` for the four `*_SINCE` names, `LEGACY_TEST_RATIO` and `slop_gated` → no match; grep of `tests.md`, `phase-3-execute.md`, `MAINTAINING.md` and the docstring for "older plans\|Earlier plans\|from 2026" → no match

## Decisions
- D1 — done runs skip the rule checks under `--all` — history; ungating would add 6 errors on `run-sizing` and `slop-guards` (product call)
- D2 — a parked run is not done, so it is checked like a live one (product call)
- D3 — the docs that mention the dates change in the same run (product call)
- D4 — the 5-behaviour minimum and the 5–15 warning go; the lean maximum of 8 stays — they live only in the legacy branch (code: scripts/check-run.py:226)
- D5 — gates use the existing `Report.done`, no new flag (code: scripts/check-run.py:713)

## Test seams
- `check-run.py` through `scripts/tests/test_check_run.py` — observes B1–B6 (existing); B7 is a grep receipt

## Out of scope
- run-level ratio gate, simplify pass — ROADMAP step 3, decided after this run
- changing any threshold (8 behaviours, 20 acceptance lines, 1.5× ratio) — this run moves no limit
- editing finished runs or the cx-intelligence parked runs — history stays as written
- TODO.md items — none match

Docs read: none in scope (no PRODUCT.md or DESIGN.md in this repo)
