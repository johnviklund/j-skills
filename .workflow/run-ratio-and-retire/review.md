Command: workflow review run-ratio-and-retire
Created: 2026-10-23 · Claude Opus 5.5
Base:    db90b60
Inputs:  .workflow/run-ratio-and-retire/plan.md @ cafdfaa
Status:  complete

## Coverage
- [x] T1 — acceptance 6/6 tested and passing (`test_run_ratio_at_completion`, `test_run_ratio_floor_and_waiver`, `test_committed_test_ratio`; replay receipt re-checked: 26 runs, 1 flagged)
- [x] T2 — acceptance 4/4: the plan's Verify greps re-run (1 · 1 · 1 · 1 · no output · 1); checkup block extracted from `checkup/SKILL.md` and re-run on cx-intelligence `50ef5321^..a5f0f341` → `tests net +3535 · code net +2885 · tracked tests/code 0.09 · ⚠️ …`, same as the receipt
- [x] B1–B8 delivered, B1 except the status form in C1-1 · Outcome observed via `check-run.py` output (this run: 0 errors; `--all` here and on cx-intelligence: no `run: tests net` on any live run) and the checkup line on cx-intelligence · manual, no verify skill (skill repo; check-run is the surface) · out of scope untouched (wrap 5b, Budget overrun: `net` = `code_net + tests` is the old sum)
- [x] .workflow/ dependency check — no hit outside `.workflow/`
- [x] full suite: 49 passed (baseline 51; −2 planned merges, F7)
- [x] assertions in `test_check_run.py`: 76 → 74, matches the planned deviation (7 removed, 5 added; receipts/t1-verification.md)
- [x] escape-hatch scan: no hits
Size: +43 code · +45 tests · ratio 1.05 · net +15 (code +16, tests −1) · over 1,000: none
Reachability: `growth` → `check_overrun`, `check_run_ratio`, `note_net_growth`, checkup §6 block · `check_run_ratio` → `check_plan` · guards shown failing: M1 latest-commit pick, M2 all→any, M3 floor `>=`, M4 HEAD endpoint, M5 code net, M6 ratio `>`, M7 lane filter, M8 waiver read — each fails ≥ 1 `-k ratio` case (throwaway worktree)
Independence: cross-vendor (writer GPT-6.1 Sol / OpenAI; reviewer Claude Opus 5.5 / Anthropic)
Threats: none — the brief and the diff add no boundary (local git reads only)

## Cycle 1 findings
### P1 — C1-1 Run gate skips plans whose done Status carries a note
- Evidence: B1 · `check-run.py:425` uses `re.fullmatch(r"done @ (SHA)")`, while `check_tickets` (`:334`) and the done-run block (`:724`) accept `done @ <sha>` followed by text. Fixture: B1's run (tests +151, code +100) with T2 `Status: done @ <sha> · T2 delegated on 2026-10-02` or `… (proof in receipts/t2.md)` → `0 errors`, no `run: tests net` line; plain `done @ <sha>` → `1 errors`. Real form: 6 cx-intelligence plans write notes after the sha (e.g. `governed-execution-discovery`, `self-service-gaps`). The gate fails open; the tests probe only the bare form.
- Disposition: fix now
- Resolved: —

### P3 — C1-2 Checkup counts run `scripts/` as code; the Code growth bullet excludes `.workflow`
- Evidence: checkup/SKILL.md Test growth block calls `growth()` (receipts excluded, `.workflow/*/scripts/` kept) "over the same range as Code growth", whose dirstat excludes `.workflow`. Accepted for the gate in F4; for the trend it only dampens the ⚠️.
- Disposition: defer (stays in review.md)

### P3 — C1-3 Checkup leans on check-run internals with no test
- Evidence: the block reads `growth`, `git_out`, `RECEIPTS`, `TEST_FILE` through `runpy`; a rename in check-run fails checkup with a `KeyError` that no check-run test catches.
- Disposition: defer (stays in review.md)

### P3 — C1-4 B7 "reports test lines": the line gives tests ÷ code, not the tracked test-line total
- Evidence: printed line `tests net · code net · tracked tests/code · advice`; T2's acceptance asked no more.
- Disposition: defer (stays in review.md)

## Pre-existing / environmental
- none

## Cycle 1 verdict
Fix C1-1, then ship. 1 P1 (fix now) · 3 P3 (deferred). The gate, ticket warning, waiver and checkup line otherwise do what the brief agreed; the tests are strong (8 of 8 mutations killed).
