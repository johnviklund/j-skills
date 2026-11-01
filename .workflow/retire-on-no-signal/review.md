Command: workflow review retire-on-no-signal
Created: 2026-11-01 · Claude Opus 5.5
Base:    b21156a
Inputs:  .workflow/retire-on-no-signal/plan.md @ d116760 · patch_plan.md @ 1fba169
Status:  complete

## Coverage
- [x] T1, T2, T3, C1-T1 to C1-T5 — covered in cycles 1 and 2; nothing in cycle 3 touches them
- [x] C2-T1 — acceptance 5/5 tested and passing; Red 81bd914 touches tests only, fix a8b72da touches no test file. The `!= 6` guard is tested on one side only, see C3-1
- [x] C2-T2 — acceptance 4/4; tests only; each of the three named mutations fails the suite
- [x] C2-T3 — the site search gives 0 hits; `README.md:214-216` names `workflow improve`
- [x] B1…B6 delivered · Outcome observed on this repo: `skill-trials.py .` exits 0 with 12 lines; `--sweep .` exits 0 with 27 label lines for 27 `trialing` rows and no other line · out of scope untouched
- [x] Mutation sweep of the cycle 3 diff at b21156a: 10 mutations, 9 fail the suite (lookbehind, `[1:-1]`, `> 6`, path in message, line start 0, `except OSError`, and the three C2-2 mutations); `!= 6` as `< 6` survives, see C3-1. `line.strip()` as `line` is equivalent: `[1:-1]` drops the trailing cell either way
- [x] .workflow/ dependency check: no new hits · escape-hatch scan: no hits · new dependencies: none
- [x] Full suites at b21156a: workflow `Ran 124 tests` OK, checkup `Ran 25 tests` OK, exit 0 · check-run: 0 errors, 0 warnings
Size: +112 code · +215 tests · ratio 1.92 · net +327 · over 1,000: none
Reachability: `skill-trials.py` → `checkup/references/seats.md` *Skill trials* · guards shown failing: all earlier ones, plus the cell-count guard for 5 cells · not shown: the cell-count guard for 7 cells, C3-1
Independence: cross-vendor (writer GPT-6.1 Sol / OpenAI · reviewer Claude Opus 5.5 / Anthropic)
Threats: none — the brief and the diff add no boundary; the script reads local files and writes nothing

## Resolved
| Finding | Sev | Title | Disposition | Resolved |
|---|---|---|---|---|
| C1-1 | P1 | 19 of 43 mutations of the new script survive the tests | fix now | @ 953e4ac (cycle 2) |
| C1-2 | P1 | A fixture write that the next line overwrites | fix now | @ 59bd7be (cycle 2) |
| C1-3 | P2 | A report line does not say which row it judges | fix now | @ 7fa0e3d (cycle 2) |
| C1-4 | P2 | A save tag for a closed row warns forever with wrong advice | fix now | @ fb6e29b (cycle 2); its archive read crashes the report, C2-1 |
| C1-6 | P3 | Four minor gaps | defer — stays here | settled (cycle 2); the `\|`-in-a-cell gap is now C2-1 |
| C1-5 | P2 | Two docs still follow the old trial rules | fix now | @ c76edeb (cycle 3) |
| C2-1 | P0 | The closed-row fix crashes the report on this repo's real archive | fix now | @ a8b72da (cycle 3); the 7-cell side of its guard is untested, C3-1 |
| C2-2 | P1 | Three more mutations survive, outside cycle 1's sweep | fix now | @ 25a4739 (cycle 3) |

## Pre-existing / environmental
- The installed `checkup` has no `skill-trials.py` until `npx skills update -g` runs after the push.

## Cycle 2 verdict
Cycle 1's C1-1 to C1-4 are fixed and C1-5 is reopened for one README sentence. Cycle 2 found 1 P0 and 1 P1. C2-1 makes the Outcome false: the report exits 2 on this repo. The two-cycle limit is reached, so C2-1, C2-2 and C1-5 wait for the human: a third cycle or a deferral.
Cycle 3 approved by human: 2026-11-01, answer "1a" to the cycle-bound question. `patch_plan.md` holds C2-T1 to C2-T3.

## Cycle 3 findings

### P1 — A row with too many cells is not tested for its location message (C3-1)
- Evidence: surviving mutation. `skill-trials.py:14` `len(cells) != 6` as `len(cells) < 6` keeps all 25 checkup tests green, because the only bad-row fixture has 5 cells (`test_skill_trials.py:212`). Under that mutant a 7-cell row, which is what an unescaped `|` in a cell makes, exits 2 with `too many values to unpack (expected 6)`: the exact C2-1 message the fix was meant to replace. Unmutated it prints `<file>:3: expected 6 cells, got 7`. Behaviour is correct today; nothing guards it. The cycle 2 patch plan named only the 5-cell case, so this is a reviewer miss.
- Remedy: one more case in `test_bad_archive_row_names_location`: an archive row at line 3 with an extra unescaped `|` exits 2, and stderr holds `SKILL-IMPACT_ARCHIVE.md:3` and `got 7`. Tests only, about 4 lines.
- Disposition: fix now — cycle 4 approved
- Resolved: —

## Cycle 3 verdict
C1-5, C2-1 and C2-2 are fixed and stamped. The Outcome holds on this repo: both report commands exit 0 and the sweep labels all 27 trialing rows. One new P1: a test gap in C2-1's own guard. It breaks no B# and not the Outcome. Cycle 3 was already the approved extra cycle, so C3-1 goes to the human: a fourth cycle with one test, or a deferral.
Cycle 4 approved by human: 2026-11-01, answer "1a" to the cycle-bound question. `patch_plan.md` holds C3-T1.
