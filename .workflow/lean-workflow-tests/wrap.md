Command: workflow wrap lean-workflow-tests
Created: 2026-11-01
Base:    3de9155
Inputs:  review.md @ 3de9155
Status:  done

## Outcome
The workflow test suites got smaller with nothing lost. Tests went from 120 to 112, cases from 266 to 257, test lines from 1,630 to 1,565, and median suite time from 52.3 to 50.9 s (inside run-to-run spread). The run's own coverage-map and mutation tool (`scripts/covmap`, `scripts/compare.py`) shows `lost 0` for every script and kind, and four hand mutants agree. No script changed.

## Shipped
- T1 baseline receipts, coverage map and mutation run with message-string and `1.5` mutants @ 6bdf81d
- T2 run-worktree tests fold behind shared helpers; checkout test moves to check-run @ e86f78a
- T3 check-run cases consolidated @ d508b3a
- T4 next-step failure checks share `fails()`; routing cases folded @ 6c4b4ca
- T5 full-suite compare, ROADMAP row 4 done, AGENTS.md suite time @ a13c5a2
- C1-T1 dead test parameters and bindings removed @ 961deed

## Review
Ship as-is after 2 cycles. C1-1 (P2, dead parameters) fixed @ 961deed. C1-2 (P3, suite-time gain inside spread) stays in `review.md`, settled.

## Deferred
Nothing went to `TODO.md`. The 5 deviations (Base case count 274 → 266, assertion shifts, corrected mutation baseline) are in `plan.md`.

## Docs and routing
- Learning routed to `.github/skills/workflow/MEMORY.md` ("A baseline for coverage or mutation counts needs a control and a case count"); one line dropped.
- ROADMAP steps 1 and 4 moved to `ROADMAP_ARCHIVE.md`; `AGENTS.md` already carries the measured time. No PRODUCT.md or DESIGN.md. No verify skill, so no feature map.
- Worklog entry added; the two oldest entries rolled off.

## Receipts
`receipts/` (coverage maps, mutation results, timings, mapping, per-ticket verification), `notes/` (P1–P3), `scripts/` (compare.py, covmap), `prototypes/P3-time-split`.

Retired: none — tests-only run; it replaced no product code path, flag or shim, and the run tools stay in the run folder as history.
