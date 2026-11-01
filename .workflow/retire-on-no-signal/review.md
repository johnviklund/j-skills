Command: workflow review retire-on-no-signal
Created: 2026-11-01 · Claude Opus 5.5
Base:    0248594
Inputs:  .workflow/retire-on-no-signal/plan.md @ d116760
Status:  complete

## Coverage
- [x] T1 — acceptance 6/6 tested and passing; the 3 doc greps hold
- [x] T2 — acceptance 5/5 tested and passing; both `seats.md` greps hold
- [x] T3 — receipt has 37 label lines and 0 tag lines; `--sweep .` now prints 0 `keep ·` lines; `decisions.md` has 37 answered rows
- [x] B1…B6 delivered · Outcome observed via manual run, no verify skill: `skill-trials.py .` lists 3 finished trials as removal candidates with `workflow improve`, 9 `open` lines · out of scope untouched: `ROADMAP.md` and correction-mining unchanged
- [x] Whole-file mutation sweep of `skill-trials.py` in a throwaway worktree: 43 mutations, 24 killed, 19 survive, see C1-1
- [x] .workflow/ dependency check: one new hit, the fixture path in `test_skill_trials.py`, a skill test reading a target repo's runs by design like `next-step.py` · escape-hatch scan: no hits · new dependencies: none
- [x] Full suites at 0248594: workflow `Ran 124 tests` OK, checkup `Ran 15 tests` OK, exit 0 · existing test files untouched · `check-run.py`: 0 errors, 0 warnings
Size: +102 code · +119 tests · ratio 1.17 · net +221 · over 1,000: none
Reachability: `skill-trials.py` → `checkup/references/seats.md` *Skill trials* · guards shown failing: the trialing filter, `(new)` and ` · ` splits, the date, skill and words keys, casefold, unique match, save count, worklog exists, skill filter, better, unit, finished, insurance, labels, candidate branch · not shown: the 19 in C1-1
Independence: cross-vendor (writer GPT-6.1 Sol / OpenAI · reviewer Claude Opus 5.5 / Anthropic)
Threats: none — the brief and the diff add no boundary; the script reads local files and prints, and writes nothing

## Cycle 1 findings

### P1 — 19 of 43 mutations of the new script survive the tests
- Evidence: whole-file sweep, `skill-trials.py` with `test_skill_trials.py`. Survivors, by name:
  real-form guards: the `| 20` row filter `:11` and `if not tag` `:26`, which both crash on real files because no fixture holds a prose line or a non-tag line; the `date`, `cycles`, `deviations` and `skills` guards `:48`.
  Date window, B2 and B3: the sort `:51`, before `<` to `<=` `:57`, after `>` to `>=` `:58`, before last N to first N, after first N to last N. Fixture values are all equal and no entry shares the row's date.
  Decision 1a, numbers on every line: sweep `detail` never printed `:67`, kept suffix never printed `:73`, `1 saves` `:64`, since tests match a prefix.
  CLI: default repo `.` `:87`, the `seats.md` no-argument path · dedupe `:87` · `is_dir` refusal `:90` · `except` narrowed `:97` · default `--impact` `:84`.
- Disposition: fix now
- Resolved: —

### P1 — A fixture write that the next line overwrites
- Evidence: `test_skill_trials.py:40-41` writes three rows; `:43-44` rewrites the file before anything reads it. Same-run waste.
- Disposition: fix now
- Resolved: —

### P2 — A report line does not say which row it judges
- Evidence: rows sharing date and skill print identical lines; F3 says this is the common case. Today `skill-trials.py .` prints `⚠️ 2026-10-26 understand · open · count explainers with a video by hand` twice. A fixture with two finished `2026-10-30 workflow` rows prints two identical `removal candidate → workflow improve workflow` lines. `skill-trials.py:70,76`
- Disposition: fix now
- Resolved: —

### P2 — A save tag for a closed row warns forever with wrong advice
- Evidence: a tag `2026-10-29 workflow next-step C2`, whose row is now `kept`, prints `⚠️ tag …:1 matches 0 rows; add words of the change`. Run folders are kept forever, and closed rows move to `SKILL-IMPACT_ARCHIVE.md`. So every tag ends up as a permanent false warning. `rows()` keeps only trialing rows, `skill-trials.py:14`
- Disposition: fix now
- Resolved: —

### P2 — Two docs still follow the old trial rules
- Evidence: `learning-worklog.md:86-89` says checkup compares by tree-hash sha and "worse means revert the commit". `seats.md` now says a candidate goes to `workflow improve`, with the human confirming before any removal. Wrap step 4 (`wrap.md:63`) routes every tagged learnings line, and `wrap.md:163` needs all of them routed. But `memory.remember/references/workflow-runs.md:6` lists no `[saved→skill]`, and the tag reads like `[durable→skill]`.
- Disposition: fix now
- Resolved: —

### P3 — Four minor gaps
- Evidence: a Trial cell with no leading count, or a row with a `|` in a cell, stops the whole report with an error that names no row (`skill-trials.py:13,55`). `review cycles` and `deviations` are read from anywhere in an entry, not only its `- Run:` line (`:45-46`). The sweep labels rows with non-run units on run numbers, which the normal report refuses: 7 of T3's 11 keeps, each confirmed by the human. The template's `[words of the change]` uses square brackets for optional words, and a tag copied with the brackets matches 0 rows (`learning-worklog.md:18`).
- Disposition: defer — stays in review.md
- Resolved: —

## Pre-existing / environmental
- The installed `checkup` has no `skill-trials.py` until `npx skills update -g` runs after the push.

## Cycle 1 verdict
Fix before wrap: 2 P1 and 3 small P2 in one patch cycle, `patch_plan.md` C1-T1 to C1-T5. One P3 entry with four minor gaps stays here. Acceptance holds for every ticket, and the Outcome shows on this repo's report.
