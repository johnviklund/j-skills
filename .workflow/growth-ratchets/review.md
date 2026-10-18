Command: workflow review growth-ratchets
Created: 2026-10-18
Base:    cab6086
Inputs:  .workflow/growth-ratchets/plan.md @ d62b5d0
Status:  complete

## Coverage
- [x] T1: acceptance 6/6 tested and passing (`RatioTests.test_growth_*`, 4 tests, 14 subtests)
- [x] T2: acceptance 5/5 by content. Key counts 1/1, `tests net` 1, stale phrases 0, doc net 0, root `WORKLOG.md` present with `--follow` reaching 5d5eba7, `has no entry` 0
- [x] B1–B8 delivered · Outcome observed on check-run output, manual (CLI, no user screen): `--all` gives 0 errors on every done run · out of scope untouched (no run-level gate, mechanical lane unchanged, skill `MEMORY.md`/`SKILL-IMPACT.md` stay put)
- [x] .workflow/ dependency check: 0 hits · escape-hatch scan: 0 hits · full suite 42/42 pass · existing test assertions unchanged (the diff's only removed test line is the `check()` signature)
Size: +31 code · +48 tests · ratio 1.55 · net +71 · over 1,000: none (check-run.py 770, test_check_run.py 415). Cycle 2 fix diff: +1 test line, no code
Reachability: no new file; `waiver()` has two live callers in `check_overrun` (`check-run.py:422`, `:432`) · guards shown failing: M2, M3
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

## Cycle 2 findings
Scope: fix diff c4ce7f0..cab6086 (one tuple in `test_growth_ratio_waivers`) plus C1-1's class, a waiver keyed on its ticket. Each mutation ran in a throwaway worktree at cab6086, `-k growth`, never committed.
- C1-1 re-checked: M1 (`re.escape(tid)` → `r"T\d+"`, `check-run.py:389`) now fails exactly one case, `Ratio waived: T2 — other ticket`. Both callers, Ratio (`:432`) and Budget (`:422`), share `waiver()`, so the one case pins the ticket key at every site. Stamped.
- Fix diff is test-only: no checker line changed, existing assertions unchanged. Full suite 42/42 pass. `check-run.py --all` 0 errors. `.workflow/` dependency check 0 hits, escape-hatch scan 0 hits.

### P1 — C2-1: no test sees which kind a waiver names
- Evidence: D2 gives two separate keys, `Ratio waived:` and `Budget waived:`. M6 replaces `kind` with `(?:Ratio|Budget)` at `check-run.py:389`, so either line waives both checks, and all 4 growth tests stay green. The code is right today. No growth case puts a `Budget waived: T1` line against a ratio error, or the reverse. Outside cycle 2's scope; cycle 1 missed it. Breaks no B# today and leaves the Outcome true.
- Disposition: fix now (human chose 1a, 2026-10-18) → `patch_plan.md` C2-T1
- Resolved: —

## Pre-existing / environmental
- `slop-guards/plan.md` 127 lines over the ~120 budget: an existing warning, unrelated to this run.

## Cycle 2 verdict
C1-1 is fixed. The new case catches the loose ticket key, and the code is unchanged. One new P1, C2-1, is the same kind of gap on a second key. The human approved a third cycle to fix it: `patch_plan.md` C2-T1, test only.
Cycle 3 approved by human: 2026-10-18 (decision 1a) B1–B8 hold, and the Outcome is visible in check-run output.
