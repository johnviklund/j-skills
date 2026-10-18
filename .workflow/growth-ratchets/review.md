Command: workflow review growth-ratchets
Created: 2026-10-18
Base:    30a648b
Inputs:  .workflow/growth-ratchets/plan.md @ d62b5d0
Status:  complete

## Coverage
- [x] T1: acceptance 6/6 tested and passing (`RatioTests.test_growth_*`, 4 tests, 14 subtests)
- [x] T2: acceptance 5/5 by content. Key counts 1/1, `tests net` 1, stale phrases 0, doc net 0, root `WORKLOG.md` present with `--follow` reaching 5d5eba7, `has no entry` 0
- [x] B1–B8 delivered · Outcome observed on check-run output, manual (CLI, no user screen): `--all` gives 0 errors on every done run · out of scope untouched (no run-level gate, mechanical lane unchanged, skill `MEMORY.md`/`SKILL-IMPACT.md` stay put)
- [x] .workflow/ dependency check: 0 hits · escape-hatch scan: 0 hits · full suite 42/42 pass · existing test assertions unchanged (the diff's only removed test line is the `check()` signature)
Size: +31 code · +50 tests · ratio 1.61 · net +73 · over 1,000: none (check-run.py 770, test_check_run.py 417). Cycle 3 fix diff: +3 −1 test lines, no code
Reachability: no new file; `waiver()` has two live callers in `check_overrun` (`check-run.py:422`, `:432`) · guards shown failing: M2, M3, M6, M7
Independence: cross-vendor (writer GPT-6.1 Sol, OpenAI · reviewer Claude Opus 5.5, Anthropic)

Mutations, each in a throwaway worktree at c4ce7f0, run with `-k growth`, never committed:
- M1 waiver key `re.escape(tid)` → `T\d+`, `check-run.py:389` → **OK, survives** (C1-1)
- M2 tests net back to added-only, `:416` → 4 failures
- M3 any-mention skip kept for new plans, `:351` → 5 failures
- M4 empty reason allowed, `:389` → OK; harmless, `if reason:` (`:424`, `:434`) still rejects an empty reason
- M5 waiver key matched anywhere on the line, `:389` → OK; harmless, the line must still name the key, ticket and a reason

## Resolved
| Finding | Sev | Title | Disposition | Resolved |
|---|---|---|---|---|
| C1-1 | P1 | no test sees which ticket a waiver names | fix now | @ ee191dc (cycle 2) |
| C1-2 | P2 | the execute doc lost two rules to stay at net zero lines | defer → `TODO.md` at wrap | settled (cycle 2) |
| C1-3 | P3 | T2's Verify exits 1 when it passes | defer, stays here | settled (cycle 2) |
| C2-1 | P1 | no test sees which kind a waiver names | fix now | @ cfa48ca (cycle 3) |

## Cycle 3 findings
Scope: fix diff cab6086..30a648b, which adds two tuples to `test_check_run.py`, plus C2-1's class, a waiver keyed on its kind. Each mutation ran in a throwaway worktree at 30a648b with `-k growth` and was never committed.
- C2-1 re-checked. M6 replaces `kind` with `(?:Ratio|Budget)` at `check-run.py:389`. It now fails exactly the two new cases, `Budget waived: T1 — wrong kind` and `Ratio waived: T1 — wrong kind`. Stamped.
- Class check. `waiver()` has two callers, Budget at `:422` and Ratio at `:432`. M7 passes `"Ratio"` at the Budget caller and fails 2 budget cases, so each caller's kind is pinned.
- The fix diff is test only. No checker line changed, and the existing assertions are unchanged. The full suite passes 42/42 and `check-run.py --all` exits 0 with 0 errors. The `.workflow/` dependency check and the escape-hatch scan each find 0 hits.
- No new findings.

## Pre-existing / environmental
- `slop-guards/plan.md` 127 lines over the ~120 budget: an existing warning, unrelated to this run.

Cycle 3 approved by human: 2026-10-18 (decision 1a)

## Cycle 3 verdict
Ship as-is. C2-1 is fixed: each wrong-kind waiver now has a case that fails when the kind check breaks. No finding is open. B1–B8 hold, and the Outcome shows in check-run output. C1-2 goes to `TODO.md` at wrap, and C1-3 stays here.
