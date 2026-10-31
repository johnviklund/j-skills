Command: workflow improve tests - goal: fewer tests, same coverage
Created: 2026-10-31 · claude-opus-5-5
Base:    aefd430
Inputs:  none
Status:  complete
Mode: attended

## Problem
The workflow suite grows faster than the scripts it tests. The five runs since run-ratio-and-retire
added tests +1,166 against code +623, and `test_run_worktree.py` is 597 lines for the 220-line
`run-worktree.py`. Every phase runs the suite at least twice, at 60–61 s each time.

## Outcome
The three files in `.github/skills/workflow/scripts/tests/` hold fewer tests and lines and run faster.
Every line, branch arm, caught mutant and assertion they had at Base is still covered. Surface: the
unittest `Ran N tests` line, `wc -l`, this run's receipts, and ROADMAP.md step 4.
Base @ aefd430: 120 tests, 274 cases, 1,630 lines, 335 assertion calls, 60.1 s and 61.2 s.

Terms: a **test** is one `def test_*`. A **case** is one `subTest`, or a test that has none. A
**mutant** is a copy of a script with one deliberate small bug, and a test **catches** it when it fails.

## Behaviours
- B1 — `test_check_run.py` after F1–F5 → fewer than 54 tests and 566 lines. The date-only cases and
  the F2 duplicate are gone, F3 is a case of the worklog test, and F4 keeps the valid row and one bad row.
- B2 — `test_run_worktree.py` after F6–F7 → fewer than 35 tests and 597 lines, and no reference to
  `check-run.py`. The checkout-warning test now sits in `test_check_run.py`.
- B3 — `test_next_step.py` after F8 → fewer than 31 tests and 467 lines. Its failure tests share one
  helper for the exit code 1, empty stdout, diagnostic and no-Traceback checks.
- B4 — the coverage map, Base vs after → the same line and branch-arm set for each of the three scripts.
- B5 — the mutation run, Base vs after, with message-string and `1.5` mutants added → every mutant
  caught at Base is still caught.
- B6 — each removed or merged test → a row in `receipts/mapping.md` naming the test and case that now
  hold each of its assertions. Assertion counts are given per file, before and after.
- B7 — ROADMAP.md step 4 → `Done 2026-…` with tests, cases, lines and suite time before and after.
  AGENTS.md states the measured suite time.
- B8 — `git diff --stat aefd430..HEAD -- .github/skills/workflow/scripts/*.py` → empty.

## Decisions
- D1 — pursue F1–F8: F1 five date-only cases and two whole tests repeat others, since `Created:`
  dates drive no rule (`check-run.py:226`). F2 `test_budget_plan_with_size_and_budgets_is_clean` repeats
  a trust-boundaries case. F3 `test_wrap_done_with_retired_is_clean` alone reaches the last-entry
  arm at `check-run.py:714`. F4 `overrides()` bad rows are tested from both scripts. F5 single-case
  check-run tests fold into tables. F6 setup, open, where, land and doctor tests fold behind one helper.
  F7 the checkout test moves. F8 next-step's single-assertion routing tests fold — product call
- D2 — same coverage is three checks: B4, B5 and B6. Lines alone miss branch arms such as F3's, and
  P1 alone calls 10 tests redundant that catch a mutant no other test catches (prototype: P1, P2)
- D3 — fold tests that share a setup into table tests. Drop a case only when D2 still holds without it.
  No target number: stop when no candidate passes — product call
- D4 — the scripts stay unchanged, so mutant ids match between Base and after (prototype: P2)
- D5 — the coverage-map and mutation tools move from `prototypes/` into this run's `scripts/`, not
  into the skill. They have one caller (code: SKILL.md Simplicity rule)
- D6 — the suite gets faster only by dropping cases: script runs take 81 % of its time and fixture git
  calls 17.5 % (prototype: P3). Time is the median of three runs with nothing else running
- D7 — ROADMAP step 4 closes with no standing rule: the simplify pass is `workflow improve tests`
  when checkup flags test growth, which checkup already prints (code: checkup/references/seats.md:42).
  Wrap moves the goal to `ROADMAP_ARCHIVE.md`
- D8 — F1, F2, F4 and F7 come from a Sonnet 5.5 brainstorm of the same prompt. Its F3 "delete" became
  "fold", because P1 shows the test's unique branch arm — product call

## Test seams
- `python3 -m unittest discover -s .github/skills/workflow/scripts/tests` — observes B1–B3 (existing)
- this run's `scripts/` coverage map and mutation run, compared with their Base receipts — observe
  B4, B5 (new, from P1 and P2)
- `receipts/mapping.md`, `wc -l`, `grep`, `git diff --stat` — observe B6–B8 (existing)

## Trust boundaries
- Mutated script copies → git writes and `bash` setup commands; they run only in temp copies against
  temp repos, never the real checkout.

## Out of scope
- TODO "Worktree setup as a script" — it changes what every AGENTS.md must hold, which is a behaviour change
- Tests for the 76 surviving mutants and the 70 on unreached lines — that adds tests, against this goal
- Cutting to the 133-case greedy minimum — it drops cases that only check a message or the 1.5× edge
- In-process calls instead of CLI subprocesses, and faster fixtures — they change the seam, or save 17 % at most
- A standing simplify-before-review or retire-at-wrap rule — D7
- The checkup suite — 8 tests in 0.5 s, not the target

Docs read: none in scope; ROADMAP.md §Goal: keep the code base and test suites from growing unchecked, TODO.md §Simplify
