Command: workflow review run-sizing
Created: 2026-10-10
Base:    e1bc18b8792c33efbb8c8930b3914c8c012e4f28
Inputs:  .workflow/run-sizing/plan.md @ 1dfb679
Status:  complete

## Coverage
- [x] T1: acceptance 4/4 passes; B1–B4 work in direct probes. B4 lacks a six-line regression assertion, C1-1.
- [x] T2: acceptance 4/4 passes; B5–B7 and B10 verified in tests and full reference text.
- [x] T3: literal acceptance 4/4 passes; B8–B12 traced through plan, execute, review, wrap, and worklog instructions. C1-2 breaks patch-session counting.
- [x] Outcome observed in checker output and skill references, manual, no verify skill. Future throughput remains a trial measure.
- [x] Full suite: 30 tests pass; all 28 assertions in 24 pre-existing tests remain unchanged.
- [x] Out of scope untouched; no added escape hatches; no `.workflow/` dependency hits outside receipts.
- [x] Mutation checks: cycle approval inversion fails 2/3 tests; six-line boundary mutation survives all 30 tests, C1-1.
Size: +27 code · +47 tests · ratio 1.74 · net +67 · over 1,000: none
Reachability: no new production files; CLI → check_plan → check_tickets → check_sizing; CLI → check_review. Median, cycle, and acceptance guards shown failing.
Independence: cross-vendor; writer Opus 5.5; reviewer configured as GPT-6 Astra in `~/.codex/config.toml`. Runtime model and picker unavailable.
Evidence: `receipts/c1-verification.md`. All changed skill files belong to T1–T3; input artifacts are fresh.

## Cycle 1 findings

### P1 — C1-1: Six acceptance lines have no regression assertion
- Evidence: B4 requires six lines to pass. `scripts/tests/test_check_run.py:130` tests only seven lines failing.
- Mutation: changing `len(accepts) <= ACCEPT_MAX` to `< ACCEPT_MAX` at `scripts/check-run.py:300` rejects six lines, but all 30 tests pass.
- Remedy: add the six-line success case at the subprocess seam and prove it fails under this mutation.
- Disposition: fix now
- Resolved: —

### P1 — C1-2: Wrap omits patch sessions from the run total
- Evidence: B9/B11 and D4 require a session record and run count. `references/phase-3-execute.md:10` selects `patch_plan.md`; line 67 records sessions there.
- `references/wrap.md:140` counts only `plan.md`, then line 147 deletes `patch_plan.md`. One initial session plus one patch session reports 1 instead of 2.
- Remedy: keep one run-wide session ledger in `plan.md` for both normal and patch execution, preserving earlier entries across patch cycles.
- Disposition: fix now
- Resolved: —

## Pre-existing / environmental
The installed workflow skill predates this run. Review checks the canonical files in `.github/skills/`.
Finding paths above are relative to `.github/skills/workflow/`. Memory and reviewer exam cases contain no matching prior occurrence.
The full plan read exposed the writer's Deviations before independent findings were drafted; blind-first isolation was incomplete.

## Cycle 1 verdict
Fix C1-1 and C1-2 before wrap. P0: 0 · P1: 2 · P2: 0 · P3: 0.
`patch_plan.md` contains two tickets. Production code passes the stated examples; the remaining work covers a missing assertion and session accounting.
Consider `verify.create` for repeatable checks of the workflow's user-facing instructions.
