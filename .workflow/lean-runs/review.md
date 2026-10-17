Command: workflow review lean-runs
Created: 2026-10-17
Base:    4a085e5
Inputs:  .workflow/lean-runs/patch_plan.md @ aafea80
Status:  complete

## Coverage
- [x] T1: acceptance 5/5 tested and passing (`LimitTests`, 2 tests, 8 subtests)
- [x] T2: acceptance 4/4 pass, and the lane gate is now pinned by the C1-T1 case
- [x] T3: acceptance 5/5 by content. The stale-number count is 0 and doc lines net −2 (`receipts/t3-net-lines.txt`)
- [x] C1-T1: acceptance 2/2. The new case passes, and the lane mutation turns it red (`receipts/c1-t1-verification.md`, re-run here)
- [x] B1–B8 delivered · Outcome observed in cycle 1 on check-run output over real cx-intelligence runs, manual (CLI, no user screen); cycle 2 changes no code · out of scope untouched
- [x] .workflow/ dependency check: 0 hits · escape-hatch scan: 0 hits · full suite 38/38 pass · check-run 0 errors
Size: +31 code · +63 tests · ratio 2.03 · net +89 · over 1,000: none (check-run.py 746)
Reachability: no new file, export or function · guards shown failing: M2, M6–M10 below
Independence: cross-vendor (writer GPT-6.1 Sol, OpenAI · reviewer Claude Opus 5.5, Anthropic)

Cycle 2 scope: the fix diff `aafea80..4a085e5` touches one test file, +2 −1, and no checker code.
It adds one tuple to `test_committed_test_ratio` and changes no assertion; the assertion count is the same before and after.

Class check for C1-1, a legacy gate whose test values cannot see it. Every `LEAN_SINCE` site was
mutated at 4a085e5 in a throwaway worktree, never committed:
- M2 `lanes` ungated, `check-run.py:414` → 1 failure (the new contract/151/2026-10-16 case)
- M6 `ratio` ungated, `:413` → 1 failure
- M7 `lean = True`, `:412` → 3 failures
- M8 brief-limit gate dropped, `:213` → 1 failure
- M9 plan-limit gate dropped, `:483` → 1 failure
- M10 Budget-reason gate dropped, `:360` → 6 failures

## Resolved
| Finding | Sev | Title | Disposition | Resolved |
|---|---|---|---|---|
| C1-1 | P1 | The lane gate for old runs survives mutation | fix now | @ e92cdbe (cycle 2) |
| C1-2 | P3 | Two predicates repeat (`check-run.py:214-215`, `:484-485`; regex `:483` repeats `:311`) | defer, stays in review.md | settled (cycle 2) |
| C1-3 | P3 | A list-item `- Split declined by human:` line is not read (`:215`, `:484`) | defer, stays in review.md | settled (cycle 2) |
| C1-4 | P3 | The Budget check reads only `code +N · tests +N` order (`:365`) | defer, stays in review.md | settled (cycle 2) |

## Cycle 2 findings
None. Code is unchanged since cycle 1, so the fix diff can introduce no regression.

## Pre-existing / environmental
- The Codex copy `~/.agents/skills/workflow/scripts/check-run.py` still has 0 `LEAN_SINCE` hits. A Codex executor gets the old checks until `npx skills update -g` runs after push.
- `scripts/tests/__pycache__/` is untracked, as at plan time.

## Cycle 2 verdict
Ship as-is. C1-1 is fixed at e92cdbe: the new case fails when the lane gate is removed, and every
other `LEAN_SINCE` gate also fails under mutation. The three P3s stay deferred here. No P0, P1 or P2 is open.
