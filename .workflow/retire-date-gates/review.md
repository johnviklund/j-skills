Command: workflow review retire-date-gates
Created: 2026-10-21 · Claude Opus 5.5
Base:    98b87f9
Inputs:  .workflow/retire-date-gates/plan.md @ 6a2dec0
Status:  complete

## Coverage
- [x] T1 — acceptance 6/6 tested and passing; B5's ticket and Resolved shas now tested (C1-1)
- [x] C1-T1 — acceptance 3/3 tested (plan, patch_plan, review findings and table); C1-T2 — 2/2 tested; 50 tests OK
- [x] T2 — acceptance 4/4 by grep receipt (receipts/t2-verification.md); re-run here, 0 forbidden matches
- [x] B1–B4, B7 delivered · B5, B6 delivered · Outcome observed via `check-run.py --all` on this repo (0 errors; slop-guards' budget warn gone as a done run) and on three parked cx-intelligence runs (read-only) · no verify skill · out of scope untouched (thresholds 8/20/1.5× unchanged; no finished run edited)
- [x] .workflow/ dependency check — 0 hits outside run folders
Size: +56 code · +92 tests · ratio 1.64 · net -9 code, +59 tests · over 1,000: none
Reachability: none new (deviated(), slop_gated(), 4 `*_SINCE`, LEGACY_TEST_RATIO, BEHAVIOURS_MIN/MAX removed) · guards shown failing: done-gate ls-files, done-gate status, parked strict, cycle ≥ 3, contract-lane ratio (cycle 1); done-run patch_plan.md walk, done-run review.md walk, parked behaviour limit (cycle 2) — all red in a throwaway worktree
Escape hatches: none added
Independence: cross-vendor (writer GPT-6.1 Sol, OpenAI · reviewer Claude Opus 5.5, Anthropic)

## Resolved
| Finding | Sev | Title | Disposition | Resolved |
|---|---|---|---|---|
| C1-1 | P1 | A done run no longer reports dangling ticket or Resolved shas | fix now | @ fbb1fdc (cycle 2) |
| C1-2 | P1 | A brief parked mid-brainstorm now fails check-run | fix now | @ 2aac08b (cycle 2) |
| C1-3 | P3 | agent-docs sentence reads as a condition | defer | stays in review.md |

## Cycle 2 findings
Scope: fix diff 188f48a..98b87f9 plus each finding's class. Red commits 380c292 (4 failures) and c88dc8e (1 failure) fail at their sha; fix commits fbb1fdc and 2aac08b leave the test files untouched (`git diff <red>..<fix> -- '*tests*'` empty).
- C1-1 class: every sha pointer outside the header is walked for a done run: ticket `done @` in plan.md and patch_plan.md (check-run.py:696-710), finding `Resolved:` lines and the `## Resolved` table in review.md. Rule checks stay off (test asserts no `Size:`).
- C1-2 class: section strictness is `complete`/`done` (check-run.py:197); the behaviour limit runs for any status except `drafting` (209). cx-intelligence `topic-catalog-quality` (parked draft) → 0 errors, 6 missing-section warnings; the 9-behaviour parked test still errors.

### P3 — The done-run sha walk repeats the live-run sha checks
- Evidence: check-run.py:696-710 re-implements the `done @` and `Resolved @` lookups of 336-337 and 534-552. The review.md walk matches every `@ <sha>` in the body, wider than the live check, and labels each one `Resolved @`. This repo's `--all` gives 0 warnings, so no real run hits the wider match.
- Disposition: defer
- Resolved: —

## Pre-existing / environmental
- D2 as intended: cx-intelligence parked runs `decision-model-evaluation` (4 errors) and `gpt6-classifier-cutover` (2 errors) now fail on behaviour and acceptance-line limits; unparking either means a split or a `Split declined by human:` line. Not edited (out of scope).
- Copilot registration check unverified (DNS), per T2 deviation; no trigger text changed.

## Cycle 2 verdict
Ship as-is. C1-1 and C1-2 are fixed at every site of their class, with red tests and no test edits in the fix commits. 0 P0, 0 P1, 0 P2, 2 P3 deferred (C1-3, C2-1). Next: wrap.
