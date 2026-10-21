Command: workflow review retire-date-gates
Created: 2026-10-21 · Claude Opus 5.5
Base:    188f48a
Inputs:  .workflow/retire-date-gates/plan.md @ 6a2dec0
Status:  complete

## Coverage
- [x] T1 — acceptance 6/6 tested and passing (47 tests, OK); B5's sha clause tested for the header Base only → C1-1
- [x] T2 — acceptance 4/4 by grep receipt (receipts/t2-verification.md); re-run here, 0 forbidden matches
- [x] B1–B4, B7 delivered · B5 partial (C1-1) · B6 over-delivered (C1-2) · Outcome observed via `check-run.py --all` on this repo (0 errors; slop-guards' budget warn gone as a done run) and on three parked cx-intelligence runs (read-only) · no verify skill · out of scope untouched (thresholds 8/20/1.5× unchanged; no finished run edited)
- [x] .workflow/ dependency check — 0 hits outside run folders
Size: +42 code · +63 tests · ratio 1.50 · net -24 code, +30 tests · over 1,000: none
Reachability: none new (deviated(), slop_gated(), 4 `*_SINCE`, LEGACY_TEST_RATIO, BEHAVIOURS_MIN/MAX removed) · guards shown failing: done-gate ls-files, done-gate status, parked strict, cycle ≥ 3, contract-lane ratio — all 5 mutations went red in a throwaway worktree
Escape hatches: none added
Independence: cross-vendor (writer GPT-6.1 Sol, OpenAI · reviewer Claude Opus 5.5, Anthropic)

## Cycle 1 findings
### P1 — A done run no longer reports dangling ticket or Resolved shas
- Evidence: B5 "a dangling sha … still reports"; the docstring and MAINTAINING.md say done runs keep "header, sha and layout checks". `check_run` skips `check_tickets` and `check_review` when `rep.done` (check-run.py:694), and those hold the only `done @` and `Resolved @` sha checks (check-run.py:336-337, 538-539, 550-552). Probe: done brief + plan with `T1 … done @ deadbee`, `--all` → new code `0 errors · 0 warnings`; at 6a2dec0 → `warn … T1: done @ deadbee is not a commit`. The T1 test checks only the header Base (test_check_run.py `test_done_brief_keeps_header_sha_and_layout_checks`).
- Remedy: for a done run, still walk the `@ <sha>` pointers in plan.md, patch_plan.md and review.md through `git_has` → `rep.missing_sha` (a warning, since done); no rule checks.
- Disposition: fix now
- Resolved: —

### P1 — A brief parked mid-brainstorm now fails check-run
- Evidence: B6 says parked is checked like a live run "(no special case)"; T1 made `parked` strict like `complete` (check-run.py:197), so a parked brief that was still drafting gets a missing-section ERROR per absent section, where a live drafting brief gets warnings. `workflow park` is allowed mid-brainstorm (phase-0-brainstorm.md:207-213) and its commit is chained on check-run, so that park can no longer commit. Real input: cx-intelligence `topic-catalog-quality` (parked, sections missing) → 6 ERRORs now, 0 errors at 6a2dec0.
- Remedy: keep `strict = status in ("complete", "done")`; apply the 8-behaviour limit when `status != "drafting"`, so B6's parked case still errors.
- Disposition: fix now
- Resolved: —

### P3 — agent-docs sentence reads as a condition
- Evidence: agent-docs/SKILL.md:151 "Finished runs get header, sha and layout checks only when included with `--all` or named explicitly" can read as "only get checks when --all". Fold into C1-1's doc touch if it edits that line; otherwise leave.
- Disposition: defer
- Resolved: —

## Pre-existing / environmental
- D2 as intended: cx-intelligence parked runs `decision-model-evaluation` (4 errors) and `gpt6-classifier-cutover` (2 errors) now fail on behaviour and acceptance-line limits; unparking either means a split or a `Split declined by human:` line. Not edited (out of scope).
- Copilot registration check unverified (DNS), per T2 deviation; no trigger text changed.

## Cycle 1 verdict
Fix two P1s (C1-1, C1-2), both small and in check-run.py; P3 deferred. Patch cycle 1 · fix C1-1, C1-2.
