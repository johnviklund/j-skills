Command: workflow brainstorm run-ratio-and-retire
Created: 2026-10-23 · Claude Opus 5.5
Base:    43e006b
Inputs:  none
Status:  done

## Problem
Test suites in workflow repos grow a little every run and almost never shrink: cx-intelligence has 64.2k test lines against 83.6k code lines. The per-ticket ratio rule fires falsely (7 of 16 hits in the trial) and was absorbed by 13 waivers since 2026-10-17, while nothing at the end of a run removes tests that are no longer needed.

## Outcome
`check-run.py` judges test growth once per run, when the last ticket is done, so writers stop adding waivers for single tickets. `checkup` reports each repo's test growth next to its code growth and points at a `workflow improve` run when tests outgrow code.

## Behaviours
- B1 — every ticket done, tests net ≥ 100 and > 1.5× code added since plan.md's Base, no run waiver → `check-run.py` ERROR naming tests net, code added and the allowed number
- B2 — same run with `Ratio waived: run — <reason>` under `## Deviations` → WARN repeating the numbers and the reason; no ERROR
- B3 — tests net exactly 1.5× code added, or tests net 99 → no run-ratio message (boundary)
- B4 — a logic or contract ticket over 1.5× with no `Ratio waived:` line → WARN only; no ERROR from the ticket ratio
- B5 — a run with any ticket not done → no run-ratio check
- B6 — `grep` over `tests.md`, `phase-3-execute.md` and `phase-4-review.md` → each states the run rule and the run waiver; no text says the ticket ratio errors or needs a waiver
- B7 — `checkup` on cx-intelligence → reports test lines, tests ÷ code, and summed net tests vs net code over the last ~10 WORKLOG `Run:` lines; tests ÷ code > 1.0 or tests outgrowing code → recommends `workflow improve tests - goal: fewer tests, same coverage`
- B8 — the new gate, run over P1's 26 runs → flags only `live-run-guardrails` (receipt)

## Decisions
- D1 — The run gate compares tests net with code added, floor 100 — flags 1 of 26 recent runs; the net-code variant flags refactors (prototype: P1)
- D2 — The gate fires once every ticket is done, before review — the reviewer judges any waiver (product call)
- D3 — The ticket ratio becomes a warning that needs no waiver — writers still see bloat early; the 13 waivers go (product call)
- D4 — Shrinking comes from a `checkup` test trend that recommends `workflow improve`, not from wrap step 5b — most `Retired: none` lines are correct; tests grow by overlap and edits, which 5b does not look at (product call; code: cx-intelligence wraps)
- D5 — Limit 1.5×, same as the ticket rule (product call)
- D6 — The checkup trend uses WORKLOG `Run:` lines and `git ls-files`; no suite runtime, since WORKLOG records it unevenly (code: cx-intelligence WORKLOG.md)

## Test seams
- `scripts/tests/test_check_run.py` driving `check-run.py` on fixture runs — observes B1–B5 (existing)
- `grep` over `references/` — observes B6 (existing)
- `checkup` report on cx-intelligence, saved as a receipt — observes B7 (manual)
- P1's `measure.py` swapped for the new gate function — observes B8 (receipt)

## Out of scope
- Wrap step 5b changes — D4
- Suite runtime in `checkup` — D6
- A ratio rule for the mechanical lane — no false hits or bloat seen there
- The per-ticket Budget overrun rule — unchanged, not part of the trial's false hits
- Editing cx-intelligence or agent-cv — read-only references

Docs read: none in scope (workflow skill only)
