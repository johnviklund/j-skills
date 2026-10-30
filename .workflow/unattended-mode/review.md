Command: workflow review unattended-mode
Created: 2026-10-30 · Claude Opus 5.5
Base:    fe33dbf
Inputs:  .workflow/unattended-mode/plan.md @ b02cf59 · .workflow/unattended-mode/patch_plan.md @ a4d6991
Status: done

Scope, cycle 3: the fix diff a4d6991..fe33dbf, which is C2-T1 red 056a042 and fix f268f88, plus the C1-1 class.
Cycle 3 approved by human: 2026-10-30 — option 1a, one more cycle fixing C1-1.

## Coverage
- [x] C2-T1 — acceptance 5/5: the new test passes (`test_run_worktree.py:144`); 056a042 run alone fails its execute case (`'.worktrees/B' != '.'`); f268f88 changes no test file; the grep returns 1; no existing assertion edited
- [x] C1-1 class, both `started()` callers: `run-worktree.py:111` own run · `:119` another live run. Reproduced in a temp repo with a plan row then an execute row: own run A with dirty `src.py` → `.`; run B on a clean tree while A holds the execute row → `.worktrees/B`
- [x] Mutations in a throwaway worktree on f268f88: `==`→`!=` killed (2 failures) · drop `exists()` killed (52) · early `return True`→`False` killed (1) · `any`→`all` survived (C3-1)
- [x] Helper boundary: `checks.decisions` raises `ValueError` on a bad row; `run-worktree.py:213` catches only `RuntimeError, OSError, CalledProcessError` (C3-2)
- [x] B1–B8 and the Outcome: `next-step.py` and `check-run.py` unchanged since cycle 1, so its observation on the real card stands · out of scope untouched
- [x] .workflow/ dependency check — the fix diff adds no `.workflow/` literal; the same files as cycle 1
- [x] Escape-hatch scan 0 hits · New dependencies none · Ratio waived none · Suites: workflow 112 OK · checkup 8 OK, exit 0
Size: +56 code · +65 tests · ratio 1.16 · net +90 · over 1,000: none (check-run.py 882); the fix cycle alone is +3 code, +19 tests
Reachability: no new file this cycle · guards shown failing: the execute-decision check in `started()`, removed → 1 failure
Independence: cross-vendor (writer GPT-6.1 Sol, OpenAI · reviewer Claude Opus 5.5, Anthropic)
Threats: unchanged from cycle 1 (text in git at 880e471); `open` now reads `decisions.md` cells as data and compares one column to a literal

## Resolved
| Finding | Sev | Title | Disposition | Resolved |
|---|---|---|---|---|
| C1-1 | P2 | An unattended UI stop has no rule for the uncommitted ticket | fix now | @ f268f88 (cycle 3) |
| C1-2 | P2 | The `decisions.md` entry in the card's Reads has no test | fix now | @ 2e8ad60 (cycle 2) |
| C1-3 | P3 | An `answered` or `assumed` row with an empty Answer passes | defer — stays in review.md; text in git at `880e471` | settled (cycle 2) |
| C1-4 | P3 | A done run hides a waiting row | defer — stays in review.md; text in git at `880e471` | settled (cycle 2) |
| C1-5 | P3 | An answer does not say who gave it | defer — stays in review.md; text in git at `880e471` | settled (cycle 2) |
| C1-6 | P3 | The hub's state table has no waiting-decision row | defer — stays in review.md; text in git at `880e471` | settled (cycle 2) |

Cycle 1 also counted 1 more P3 without an ID; text in git at `880e471`. Cycle 2 had no new finding; its verdict is in git at `a4d6991`.

## Cycle 3 findings
### P1 — The new test's one-row fixture lets `any`→`all` survive
- Evidence: mutating `any(row["Phase"] == "execute"` to `all(` at `run-worktree.py:100` leaves `test_run_worktree` green. The fixture (`test_run_worktree.py:149-152`) holds one row, where `any` and `all` agree. A real unattended run writes plan rows before execute rows (`unattended.md:13-14`, example row `D1 | plan`), and under `all` such a file brings C1-1 back. Same class as `tests.md`'s rule that a fixture copies every real form.
- Remedy: put a `| D1 | plan | … | assumed | … |` row before the execute row in the fixture, renumbering it D2. One test line; no code change.
- Disposition: defer → `TODO.md` at wrap — Approved by human: 2026-10-30, option 1b
- Resolved: —

### P2 — A bad `decisions.md` in any live run makes `open` crash with a traceback
- Evidence: a temp repo where run A's `decisions.md` has status `approved` and run B is unstarted → `run-worktree.py open B` prints a Python traceback ending `ValueError: …/A/decisions.md: D1: unknown decision status approved`, exit 1. Before f268f88, `open B` ignored A's file. `next-step.py:207` catches `ValueError`; `run-worktree.py:213` does not.
- Remedy: add `ValueError` to the except tuple at `run-worktree.py:213`, plus one `OpenTests` case asserting exit 1 and the file name on stderr with no `Traceback`. About 1 code and 8 test lines. Failing closed is right: `open` cannot tell whether A occupies the primary checkout.
- Disposition: defer → `TODO.md` at wrap — human chose option 1b, 2026-10-30
- Resolved: —

### P3 — `worktrees.md:46` still says another run occupies the primary checkout only with a started ticket
- Evidence: line 44 gained "or an execute decision" for the run itself; line 46 did not, though `started()` now also counts an execute decision for other runs (`run-worktree.py:119`).
- Disposition: defer — stays in review.md
- Resolved: —

## Pre-existing / environmental
none

## Cycle 3 verdict
Human decision · C1-1 is fixed at both call sites and stamped. P0 0 · P1 1 (C3-1) · P2 1 (C3-2) · P3 1 (C3-3). The code is right; C3-1 is a test gap and C3-2 an unhandled error in a path the fix added. Neither breaks a B# or the Outcome. Past the two-cycle bound, so the human chose between a fourth cycle and deferral.

Deferral approved by human (1b), 2026-10-30: C3-1 and C3-2 become `TODO.md` lines at wrap; C3-3 stays here. Next: wrap.
