Command: workflow review growth-ratchets
Created: 2026-10-18
Base:    c4ce7f0
Inputs:  .workflow/growth-ratchets/plan.md @ d62b5d0
Status:  complete

## Coverage
- [x] T1: acceptance 6/6 tested and passing (`RatioTests.test_growth_*`, 4 tests, 14 subtests)
- [x] T2: acceptance 5/5 by content. Key counts 1/1, `tests net` 1, stale phrases 0, doc net 0, root `WORKLOG.md` present with `--follow` reaching 5d5eba7, `has no entry` 0
- [x] B1–B8 delivered · Outcome observed on check-run output, manual (CLI, no user screen): `--all` gives 0 errors on every done run · out of scope untouched (no run-level gate, mechanical lane unchanged, skill `MEMORY.md`/`SKILL-IMPACT.md` stay put)
- [x] .workflow/ dependency check: 0 hits · escape-hatch scan: 0 hits · full suite 42/42 pass · existing test assertions unchanged (the diff's only removed test line is the `check()` signature)
Size: +31 code · +47 tests · ratio 1.52 · net +70 · over 1,000: none (check-run.py 770)
Reachability: no new file; `waiver()` has two live callers in `check_overrun` (`check-run.py:422`, `:432`) · guards shown failing: M2, M3
Independence: cross-vendor (writer GPT-6.1 Sol, OpenAI · reviewer Claude Opus 5.5, Anthropic)

Mutations, each in a throwaway worktree at c4ce7f0, run with `-k growth`, never committed:
- M1 waiver key `re.escape(tid)` → `T\d+`, `check-run.py:389` → **OK, survives** (C1-1)
- M2 tests net back to added-only, `:416` → 4 failures
- M3 any-mention skip kept for new plans, `:351` → 5 failures
- M4 empty reason allowed, `:389` → OK; harmless, `if reason:` (`:424`, `:434`) still rejects an empty reason
- M5 waiver key matched anywhere on the line, `:389` → OK; harmless, the line must still name the key, ticket and a reason

## Cycle 1 findings

### P1 — C1-1: no test sees which ticket a waiver names
- Evidence: D2 and B3 key a waiver to its ticket (`Ratio waived: T# — <reason>`). M1 lets any ticket's waiver silence T1's ratio error, and all 4 growth tests stay green. The code is right today (`check-run.py:389`), but nothing pins it. `test_growth_ratio_waivers` (`test_check_run.py:147-149`) has no case naming another ticket. Same class as lean-runs C1-1.
- Disposition: fix now
- Resolved: —

### P2 — C1-2: the execute doc lost two rules to stay at net zero lines
- Evidence: `phase-3-execute.md:92` drops "Build what its acceptance lines describe, at its seam" and "the ticket continues" after a side note. No other line in the file restates either. D7's net ≤ 0 lines was met by unwrapping: the three edited docs gained 19 words, and lines over 100 chars in `phase-3-execute.md` went from 9 to 13.
- Disposition: defer → `TODO.md` at wrap (restore both rules; measure doc growth in words, not lines)
- Resolved: —

### P3 — C1-3: T2's Verify exits 1 when it passes
- Evidence: its last command is `grep -c 'has no entry'`, which exits 1 on the expected count 0. The writer noted this (`receipts/t2-verification.md`). Use `grep -c … || true` next time.
- Disposition: defer, stays in review.md
- Resolved: —

## Pre-existing / environmental
- `slop-guards/plan.md` 127 lines over the ~120 budget: an existing warning, unrelated to this run.

## Cycle 1 verdict
Fix C1-1 first: one patch ticket, test only (`patch_plan.md` C1-T1). The checker logic is right. B1–B8 hold, and the Outcome is visible in check-run output. C1-2 is deferred to `TODO.md`, and C1-3 stays here.
