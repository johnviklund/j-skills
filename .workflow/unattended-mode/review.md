Command: workflow review unattended-mode
Created: 2026-10-30 · Claude Opus 5.5
Base:    1db6f47
Inputs:  .workflow/unattended-mode/plan.md @ b02cf59 · .workflow/unattended-mode/patch_plan.md @ f719a10
Status: complete

Scope, cycle 2: the fix diff f719a10..1db6f47, which is C1-T1 23f4ec6 and C1-T2 2e8ad60, plus each finding's class.
Cycle 3 approved by human: 2026-10-30 — option 1a, one more cycle fixing C1-1.

## Coverage
- [x] C1-T1 — acceptance 3/3 re-run: 1 · 1 · 5; `## Always stop` is still only in `unattended.md`. Doc-only; no test or script touched
- [x] C1-T2 — acceptance 2/2: the suite passes with the new assertion (`test_next_step.py:103`); deleting `next-step.py:177` in a throwaway worktree fails 2 tests (killed); `next-step.py` unchanged since f719a10; assertions in `test_next_step.py` 75 → 76
- [x] C1-1 class, every site where a resumed session meets the UI ticket's uncommitted code: `unattended.md:36-38` (fixed) · `SKILL.md:151-153` (overridden for unattended runs through `SKILL.md:24`) · `phase-3-execute.md:27` baseline reuse (reruns the suite; harmless) · `phase-3-execute.md:128` Execution state names the uncommitted files · `run-worktree.py:104-117` `open` (not covered; C1-1 reopened)
- [x] C1-2 class: `next-step.py:177` is the only place that adds `decisions.md` to Reads
- [x] B1–B8 and the Outcome: no script changed since cycle 1, so its observation on the real card stands · out of scope untouched
- [x] .workflow/ dependency check — the same hits as cycle 1 (`next-step.py`, `run-worktree.py`, test fixtures); the fix diff adds none
- [x] Escape-hatch scan 0 hits · New dependencies none · Ratio waived none · Suites: workflow 111 OK · checkup 8 OK, exit 0
Size: +53 code · +46 tests · ratio 0.87 · net +68 · over 1,000: none (check-run.py 882); the fix cycle alone is +0 code, +1 test
Reachability: no new file this cycle · guards shown failing: the Reads append (`next-step.py:177`), deleted → 2 failures
Independence: cross-vendor (writer GPT-6.1 Sol, OpenAI · reviewer Claude Opus 5.5, Anthropic)
Threats: unchanged from cycle 1 (text in git at 880e471); the fix diff adds one doc rule and one test assertion, and no input, write or command

## Resolved
| Finding | Sev | Title | Disposition | Resolved |
|---|---|---|---|---|
| C1-2 | P2 | The `decisions.md` entry in the card's Reads has no test | fix now | @ 2e8ad60 (cycle 2) |
| C1-3 | P3 | An `answered` or `assumed` row with an empty Answer passes | defer — stays in review.md; text in git at `880e471` | settled (cycle 2) |
| C1-4 | P3 | A done run hides a waiting row | defer — stays in review.md; text in git at `880e471` | settled (cycle 2) |
| C1-5 | P3 | An answer does not say who gave it | defer — stays in review.md; text in git at `880e471` | settled (cycle 2) |
| C1-6 | P3 | The hub's state table has no waiting-decision row | defer — stays in review.md; text in git at `880e471` | settled (cycle 2) |

Cycle 1 also counted 1 more P3 without an ID; text in git at `880e471`.

## Cycle 1 findings
### P2 — An unattended UI stop has no rule for the uncommitted ticket
- Evidence (cycle 1): `unattended.md:21-22` commits and pushes at every Always-stop case, but the UI stop comes before the ticket's commit, and a resumed session treats dirty paths no run commit touched as the human's (`SKILL.md:151-153`).
- Evidence (cycle 2): C1-T1 fixes the rule (`unattended.md:36-38`) but not its code site. `run-worktree.py open` calls a run unstarted while every ticket is `todo` (`started()`, `:98-101`) and the primary checkout busy when `git status --porcelain` shows anything (`:110`), so it opens a new `.worktrees/<slug>` from the primary branch. Failing input, reproduced in a temp repo: a primary-checkout unattended run stops at its first ticket, a UI ticket, with `src.py` edited; D1 `execute` is answered; the fresh session's `open A` prints `.worktrees/A`, whose `src.py` reads `base`. The pending code stays in the primary checkout, outside the session's checkout.
- Remedy: `started()` also returns true when the run's `decisions.md` has an `execute` row, which every stop writes first (`unattended.md:13-14`); one test beside `test_Open_keeps_dirty_checkout_busy_with_an_unstarted_run` (`test_run_worktree.py:135`). About 3 code and 8 test lines.
- Disposition: fix now (small) — reopened in cycle 2; past the two-cycle bound, so the human decides between a third cycle and deferral
- Resolved: — (reopened, cycle 2)

## Cycle 2 findings
No new finding. C1-1 is reopened above; C1-2 is stamped.

## Pre-existing / environmental
none

## Cycle 2 verdict
Human decision · C1-1 is still open after two cycles. P0 0 · P1 0 · P2 1 (C1-1, reopened) · P3 0 new. C1-2 is fixed and its mutation is killed. The UI-stop rule now says the right thing, but `run-worktree.py open` still sends a resume after a first-ticket UI stop to a new, empty worktree. That breaks no B# and not the Outcome. Recommended: a third cycle with one fix ticket (decision 1a).

Cycle 3 approved by human (1a). Patch cycle 2 (`patch_plan.md`): C2-T1 fixes C1-1.
