Command: workflow review retire-on-no-signal
Created: 2026-11-01 · Claude Opus 5.5
Base:    8bca6d7
Inputs:  .workflow/retire-on-no-signal/plan.md @ d116760 · patch_plan.md @ 0248594
Status:  complete

## Coverage
- [x] T1 — acceptance 6/6 tested and passing; the 3 doc greps hold
- [x] T2 — acceptance 5/5 tested and passing; both `seats.md` greps hold
- [x] T3 — receipt has 37 label lines and 0 tag lines; `decisions.md` has 37 answered rows; `--sweep` over a copy of `SKILL-IMPACT.md` with no archive beside it prints 27 `candidate` lines and 0 `keep`. On the real folder it exits 2, see C2-1
- [x] C1-T1 — the 19 named mutations each fail the suite in a throwaway worktree
- [x] C1-T2 — that test calls `self.rows(` once and passes
- [x] C1-T3 — both acceptance lines tested; on the real rows, archive excluded, 12 report lines and 0 duplicates. `> 6` as `>= 6` survives, see C2-2
- [x] C1-T4 — 3 subtests pass; on the real folder the archive read crashes, see C2-1
- [x] C1-T5 — greps give 0 · present · 1 as accepted; `workflow/README.md:214-215` still says revert, C1-5 reopened
- [x] Red commits 711f01a, d3d54b6 touch tests only; fix commits 7fa0e3d, fb6e29b touch no test file
- [x] B1…B6 delivered on fixtures · Outcome false: `skill-trials.py .` exits 2 on this repo, see C2-1 · out of scope untouched: `ROADMAP.md` and correction-mining unchanged
- [x] Whole-file mutation sweep at 8bca6d7: 61 mutations, 57 fail the suite; the 4 survivors are in C2-1 and C2-2
- [x] .workflow/ dependency check: no new hits · escape-hatch scan: no hits · new dependencies: none
- [x] Full suites at 8bca6d7: workflow `Ran 124 tests` OK, checkup `Ran 20 tests` OK, exit 0
Size: +109 code · +186 tests · ratio 1.71 · net +295 · over 1,000: none
Reachability: `skill-trials.py` → `checkup/references/seats.md` *Skill trials* · guards shown failing: the 19 from C1-1, the C1-T3 words and ellipsis, the 7 C1-T4 conditions · not shown: the 4 in C2-1 and C2-2
Independence: cross-vendor (writer GPT-6.1 Sol / OpenAI · reviewer Claude Opus 5.5 / Anthropic)
Threats: none — the brief and the diff add no boundary; the script reads local files, now also the archive beside `--impact`, and writes nothing

## Resolved
| Finding | Sev | Title | Disposition | Resolved |
|---|---|---|---|---|
| C1-1 | P1 | 19 of 43 mutations of the new script survive the tests | fix now | @ 953e4ac (cycle 2) |
| C1-2 | P1 | A fixture write that the next line overwrites | fix now | @ 59bd7be (cycle 2) |
| C1-3 | P2 | A report line does not say which row it judges | fix now | @ 7fa0e3d (cycle 2) |
| C1-4 | P2 | A save tag for a closed row warns forever with wrong advice | fix now | @ fb6e29b (cycle 2); its archive read crashes the report, C2-1 |
| C1-6 | P3 | Four minor gaps | defer — stays here | settled (cycle 2); the `\|`-in-a-cell gap is now C2-1 |

## Cycle 1 findings

### P2 — Two docs still follow the old trial rules
- Evidence: `learning-worklog.md:86-89` says checkup compares by tree-hash sha and "worse means revert the commit". `seats.md` now says a candidate goes to `workflow improve`, with the human confirming before any removal. Wrap step 4 (`wrap.md:63`) routes every tagged learnings line, and `wrap.md:163` needs all of them routed. But `memory.remember/references/workflow-runs.md:6` lists no `[saved→skill]`, and the tag reads like `[durable→skill]`.
- Disposition: fix now — cycle 3 approved
- Resolved: —
- Reopened in cycle 2: C1-T5 fixed both named sites, but `workflow/README.md:214-215` still says "If the runs got worse, revert the commit and log why." The patch plan's site search missed it.
- Remedy: replace that sentence with the `seats.md` rule. A finished trial with no save and no better numbers becomes a removal candidate for `workflow improve`, and nothing is removed until the human confirms.

## Pre-existing / environmental
- The installed `checkup` has no `skill-trials.py` until `npx skills update -g` runs after the push.

## Cycle 1 verdict
Fix before wrap: 2 P1 and 3 small P2 in one patch cycle, `patch_plan.md` C1-T1 to C1-T5. One P3 entry with four minor gaps stays here. Acceptance holds for every ticket, and the Outcome shows on this repo's report.

## Cycle 2 findings

### P0 — The closed-row fix crashes the report on this repo's real archive (C2-1)
- Evidence: Outcome false on its surface. `skill-trials.py .` and `--sweep .` both exit 2 with `too many values to unpack (expected 6)`, so `checkup seats` prints no trial line. C1-T4 now parses every row of `SKILL-IMPACT_ARCHIVE.md` (`skill-trials.py:96-99`), and archive rows 17, 18, 22 and 23 hold `\|` inside a cell. `rows()` splits on every `|` (`:13`). The fixture archive holds one clean row (`test_skill_trials.py:180`), so all 20 tests pass. This also makes cycle 1's deferred P3 (a `|` in a cell stops the report) a crash on real data. Third time a fixture held only lines the parser handles. The sweep also shows the `ValueError` arm of `except` `:104` untested: narrowing it to `OSError` keeps all 20 tests green.
- Remedy: split cells on unescaped pipes, `re.split(r"(?<!\\)\|", line.strip())[1:-1]`. A row that still has the wrong cell count exits 2 naming `<file>:<line>`. The archive fixture copies a real row with `\|` in a cell, and the acceptance runs `skill-trials.py .` and `--sweep .` on this repo, each exit 0.
- Disposition: fix now — cycle 3 approved
- Resolved: —

### P1 — Three more mutations survive, outside cycle 1's sweep (C2-2)
- Evidence: whole-file sweep at 8bca6d7. First, `better = bool(before and after and …)` `:61` without `after` divides by zero for a row with worklog entries before it and none after, a trial that just started. No fixture has one; today's 2026-11-01 rows do, and the mutant exits 1 on them. Second, `workflow improve {row['names'][0]}` `:78` printing the whole Skill cell survives. No fixture has a finished multi-skill candidate, and the real report has one, `2026-10-26 memory.remember · memory.compact · workflow`. Third, C1-T3's `len(words) > 6` `:68` as `>= 6` survives, since no fixture Change has exactly 6 words. Cycle 1's sweep never tried the first two, so they are a reviewer miss.
- Remedy: three cases in `test_skill_trials.py`. A `3 runs` row with 3 entries before and none after: `--sweep` prints `numbers unavailable (before 4.0 → after n/a)`. A finished `design (new) · workflow` candidate: the line ends `workflow improve design`. A 6-word Change: its words with no `…`.
- Disposition: fix now — cycle 3 approved
- Resolved: —

## Cycle 2 verdict
Cycle 1's C1-1 to C1-4 are fixed and C1-5 is reopened for one README sentence. Cycle 2 found 1 P0 and 1 P1. C2-1 makes the Outcome false: the report exits 2 on this repo. The two-cycle limit is reached, so C2-1, C2-2 and C1-5 wait for the human: a third cycle or a deferral.
Cycle 3 approved by human: 2026-11-01, answer "1a" to the cycle-bound question. `patch_plan.md` holds C2-T1 to C2-T3.
