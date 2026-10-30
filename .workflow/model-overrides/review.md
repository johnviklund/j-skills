Command: workflow review model-overrides
Created: 2026-10-30 · Opus 5.5
Base:    a7138d8
Inputs:  .workflow/model-overrides/plan.md @ 43bd7b2 · .workflow/model-overrides/patch_plan.md @ ad0afd9
Status:  complete

Scope, cycle 2: the fix diff 966b7f8..a7138d8, which is C1-T1 red 4b37b24 and fix 5d2d876 and C1-T2 a4135aa, plus the C1-1 and C1-2 classes.

## Coverage
- [x] C1-T1 — acceptance 4/4: both new tests pass (`test_next_step.py:67`, `test_check_run.py:457`); at 4b37b24 both fail, run alone in a throwaway worktree; 4b37b24 changes only the two test files, +13 −0; 5d2d876 changes no test file; `test_override_bad_rows_name_key_without_json` and `test_override_validation` pass unchanged
- [x] C1-1 class: the two `routing.md` readers are `next-step.py:110` and `check-run.py:815`, and both now skip done runs. A parked run still validates its `routing.md`, which is right because a parked run can resume. next-step skips any done brief, while check-run skips only a tracked, clean one, as its docstring (`check-run.py:26-27`) says
- [x] C1-2 class: the vendor lookup (`phase-4-review.md:7`) and the `Writer:` name (`phase-3-execute.md:138`) both read the run's `routing.md` first; the grep returns 1 in each; a4135aa is +1 −1 per file. Other `ROUTING.md` readers need no change: wrap already takes models from the run (`wrap.md:143`), and checkup's per-seat table reads the shared incumbent (`checkup/references/seats.md:20`)
- [x] Mutations in a throwaway worktree on a7138d8: drop the next-step done guard killed (1) · drop the check-run done guard killed (1) · invert the next-step guard killed (12) · invert the check-run guard killed (4) · guard on `parked` instead of `done` killed (1)
- [x] B1–B6 and the Outcome: a scratch run against the real `ROUTING.md` shows `Gemini 4 · xhigh · standard (override)`; a retired key exits 1 naming the row while the run is live, and prints the ✅ Done card once the brief is done · out of scope untouched
- [x] .workflow/ dependency check — the fix diff adds no `.workflow/` literal; the hits are the same four files as cycle 1, all reading run folders by design
- [x] Escape-hatch scan 0 hits · New dependencies none · Suites: workflow 119 OK · checkup 8 OK, exit 0
Size: +54 code · +78 tests · ratio 1.44 · net +116 · over 1,000: none (check-run.py 913); the fix cycle alone is +3 −3 code, +13 tests
Reachability: no new file this cycle · guards shown failing: the next-step done guard, the check-run done guard
Independence: cross-vendor (writer GPT-6.1 Sol, OpenAI · reviewer Opus 5.5, Anthropic; this run has no `routing.md`)
Threats: unchanged from cycle 1 (text in git at 966b7f8); the fix reads the brief's Status earlier and opens no new input

## Resolved
| Finding | Sev | Title | Disposition | Resolved |
|---|---|---|---|---|
| C1-1 | P2 | A done run's routing.md breaks next-step and check-run after a ROUTING.md key change | fix now | @ 5d2d876 (cycle 2) |
| C1-2 | P2 | Review and execute look up a run's models only in ROUTING.md | fix now | @ a4135aa (cycle 2) |
| C1-3 | P3 | An empty routing.md reports `missing None table` | defer — stays in review.md; text in git at `966b7f8` | settled (cycle 2) |
| C1-4 | P3 | check-run's routing.md ERROR repeats the absolute path after the relative one | defer — stays in review.md; text in git at `966b7f8` | settled (cycle 2) |
| C1-5 | P3 | SKILL.md grows further past its ~10 KB budget | defer — stays in review.md; text in git at `966b7f8` | settled (cycle 2) |

Cycle 1's verdict is in git at `966b7f8`.

## Cycle 2 findings
none

## Pre-existing / environmental
- The installed skill copy lags this repo until `npx skills update -g` runs after the push (AGENTS.md); this review ran the repo's scripts.
- check-run still validates a done run's `decisions.md` (`check-run.py:810-814`), though its docstring (`:26-27`) says done runs get only header, sha and layout checks. It predates this run and needs a change to check-run's status words to break anything.

## Cycle 2 verdict
Ship as-is. P0 0 · P1 0 · P2 0 · P3 0 new. Both cycle 1 fixes hold at every site of their class, the reproducing tests failed at the Red commit and pass now, and every new guard fails a test when mutated. Next: wrap.
