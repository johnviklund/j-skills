Command: workflow review run-ratio-and-retire
Created: 2026-10-23 · Claude Opus 5.5
Base:    d1f9b5f
Inputs:  .workflow/run-ratio-and-retire/plan.md @ cafdfaa
Status:  done

## Coverage
- [x] T1 — acceptance 6/6 tested and passing (`test_run_ratio_at_completion`, `test_run_ratio_floor_and_waiver`, `test_committed_test_ratio`; replay receipt re-checked: 26 runs, 1 flagged)
- [x] T2 — acceptance 4/4: the plan's Verify greps re-run (1 · 1 · 1 · 1 · no output · 1); checkup block re-run on work-repo `50ef5321^..a5f0f341` → `tests net +3535 · code net +2885 · tracked tests/code 0.09 · ⚠️ …`, same as the receipt
- [x] C1-T1 — acceptance 3/3: both note forms give `1 errors` with the B1 message; replay re-run → `27 runs; 1 flagged` (`live-run-guardrails` +679 / +442)
- [x] B1–B8 delivered · Outcome observed via `check-run.py` output (this run: 0 errors; `--all` on work-repo: no `run: tests net` on any live run) and the checkup line on work-repo · manual, no verify skill (skill repo; check-run is the surface) · out of scope untouched
- [x] .workflow/ dependency check — no hit outside `.workflow/`
- [x] full suite: 49 passed (baseline 51; −2 planned merges, F7) · `-k ratio`: 5 passed
- [x] assertions in `test_check_run.py`: 74 after C1-T1, unchanged (two table rows added)
- [x] escape-hatch scan: no hits
Size: +43 code · +47 tests · ratio 1.09 · net +17 (code +16, tests +1) · over 1,000: none
Reachability: no new file or export in cycle 2 · guards shown failing: cycle 1 M1–M8; cycle 2 M9 `\b` → `$` at check-run.py:425 fails both note rows (throwaway worktree)
Independence: cross-vendor (writer GPT-6.1 Sol / OpenAI; reviewer Claude Opus 5.5 / Anthropic)
Threats: none — the brief and the diff add no boundary (local git reads only)

## Resolved
| Finding | Sev | Title | Disposition | Resolved |
|---|---|---|---|---|
| C1-1 | P1 | Run gate skips plans whose done Status carries a note | fix now | @ 40f9e4f (cycle 2) |
| C1-2 | P3 | Checkup counts run `scripts/` as code; the Code growth bullet excludes `.workflow` | defer (stays in review.md) | settled (cycle 2) |
| C1-3 | P3 | Checkup leans on check-run internals with no test | defer (stays in review.md) | settled (cycle 2) |
| C1-4 | P3 | B7 line gives tests ÷ code, not the tracked test-line total | defer (stays in review.md) | settled (cycle 2) |

## Cycle 2 findings
- none. C1-1 re-checked at every site of its class: the three `done @ <sha>` readers in check-run.py (`:334`, `:425`, `:724`) all accept text after the sha; `replay.py` uses `startswith`. Red @ 7ac1df2 touches only the test file and fails without the fix; fix @ 40f9e4f touches only check-run.py (1 line). The `todo` and `awaiting-human` rows stay green, so the fix does not loosen what counts as done.

## Pre-existing / environmental
- none

## Cycle 2 verdict
Ship as-is. 0 P0 · 0 P1 · 0 P2 · 3 P3 (deferred, from cycle 1). C1-1 is fixed at every site and its test catches the bug when it is put back.
