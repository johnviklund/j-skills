Command: workflow plan lean-workflow-tests
Created: 2026-10-31 · claude-opus-5-5
Base:    9a77cd3
Inputs:  .workflow/lean-workflow-tests/brainstorm.md @ aefd430
Status:  complete

Docs read: none in scope; no PRODUCT.md or DESIGN.md. ROADMAP.md §Goal: keep the code base and test suites from growing unchecked
Size: code 0 skill lines touched (scripts 1,355 measured, unchanged) + 426 run-tool lines moved from prototypes/ · tests 1,630 · largest touched test_run_worktree.py 597 · over 1,000: none
Decisions: 1a approve T1-T5 as listed · 2a message-string mutants cover only strings inside diagnostic calls (F4), 149 complete strings

## Execution state
Current: T3 ready; T2 complete.
T1 @ 6bdf81d
T2 @ e86f78a
writer: GPT-6.1 Sol
Baseline: workflow 120 tests in 52.675s OK; checkup 8 tests in 0.428s OK.
Pending decision: none.
Session 1: T1 incomplete; case-count and mutation-fixture findings.
Session 2: T1, T2
## Findings
| # | What is true | What it changes |
|---|---|---|
| F1 | Baseline @ 9a77cd3: workflow suite 120 tests OK in 52.3 s, checkup 8 OK. Tests 54 · 31 · 35, assertion calls 89 · 91 · 155, lines 566 · 467 · 597 match the brief. `git diff --stat aefd430..HEAD -- .github/skills/workflow/scripts` is empty | The tree is still Base, so T1 measures Base at HEAD. The brief's 60.1 s and 61.2 s came from another machine state, so T1 measures Base time again as a median of three |
| F2 | The Base coverage map and mutation results exist only in `/tmp` (`covmap-before/`, `mut-before-*.json`) and have no message-string or `1.5` mutants | T1 regenerates Base into `receipts/` before any test changes |
| F3 | `check-run.py:66` counts only `*.md` and `*.txt` as receipts; P2's raw JSON is 3.8 MB | Raw tool output stays in `/tmp`; receipts are sorted `.txt` item lists, one item per line |
| F4 | The scripts hold 1,249 non-docstring fragments; 149 whole strings sit inside diagnostic calls: `rep.error/warn/note/missing_sha`, `print`, `sys.exit`, `raise ValueError/RuntimeError`. The one float is `TEST_RATIO = 1.5` at `check-run.py:63` | A message-string mutant wraps one string in a diagnostic call as `"XX" + s + "XX"`; the float mutants are `1.4` and `1.6`. All 1,249 strings would add about an hour per run |
| F5 | Mutant ids collide once: `check-run.py:380:15:LtE->Lt`, a chained comparison | T1 makes ids unique, so compare loses no mutant |
| F6 | P2 at Base took 8,725 CPU-s for 665 mutants, about 36 min on 4 workers; this machine has 8 cores | Runs use `--workers 6`. A full run takes about 50 min; T2 to T4 run `--only` their own script |
| F7 | `next-step.py:112` calls check-run's `overrides()`, so next-step tests reach check-run lines | A loss across files shows only in a full-suite run, which T5 does |
| F8 | Quoted, `git diff -- '.github/skills/workflow/scripts/*.py'` matches `tests/` too, because git's `*` crosses `/` | B8's check names the three scripts |
| F9 | Reuse: `check()` at `test_check_run.py:66` builds a fixture repo; `run_command`, `started`, `run_branch` at `test_run_worktree.py:46,50,403`; `result()` at `test_next_step.py:59` covers only success. Next-step has 5 `Traceback` and 6 `(1, "")` checks and no failure helper | The moved checkout test reuses `check()` with a checkout argument; it needs no origin. T4 adds one `fails()` helper |
| F10 | `Created:` dates drive only the model warning at `check-run.py:226`. The date-only cases are the 4th of `test_plan_limits`, 5th of `test_committed_test_ratio`, 4th of `test_budget_ratio_reason`, plus `test_budget_old_plan_without_budget_warns:303` and `test_cycle_three_old_review_still_needs_approval:448`. Only `test_wrap_done_with_retired_is_clean:518` has a one-entry WORKLOG, the arm at `check-run.py:714` | Brief F1 and F3 hold as written |
| F11 | `checkup/references/seats.md:42` prints the `workflow improve tests` advice | D7 needs no new rule |
| F12 | T2 to T4 change only tests, so their code Budget is 0 and check-run warns that the median code Budget is under 40 | The warning is expected here and is no merge signal |
## Deviations
- Human approved 1a: correct Base to 266 cases; 274 counted eight outer contexts twice.
  Evidence: receipts/t1-case-count.md. F4 counts whole diagnostic strings, including f-strings.
- T2 relocates assertions: run-worktree 155 → 126, check-run 89 → 92; values unchanged.
- The mutation copy omitted ROUTING.md: two tests fail unmutated, and 32 P2 catches depend only
  on those tests. The fixture now copies that dependency. Human approved regenerating and using corrected counts.
## Tickets
### T1 — Base receipts: coverage map and mutation run with message-string and 1.5 mutants
Delivers: B4, B5 (Base half), prefactor for T2-T5 · Blocked by: none · Lane: logic
Budget: code +120 · tests +0
Seam: `scripts/covmap/`, `scripts/mutation/`, `scripts/compare.py <base> <label>` in the run folder; P1 and P2 move there with `git mv`, P3 stays
Accept:
- [x] `receipts/covmap-base.txt` totals → check-run.py 630 lines · 673 arms, next-step.py 204 · 229, run-worktree.py 188 · 170; 120 tests · 266 cases (B4)
- [x] `receipts/mutants-base.txt` → corrected P2 caught counts recorded per script, ids unique, and `TEST_RATIO` `1.4` and `1.6` mutants both caught (B5)
- [x] the same receipt → message-string mutants listed per script with caught and survived counts, check-run.py caught > 0 (B5)
- [x] `compare.py base base` → `lost 0` per script and kind, exit 0; with one Base item deleted from a copy → exit 1 naming that item
- [x] `receipts/time-base.txt` → three workflow-suite times with nothing else running, and their median
Verify: `cd .workflow/lean-workflow-tests && python3 scripts/compare.py base base` (pre: new file)
Skills: none
Status: done @ 6bdf81d
Writer: GPT-6.1 Sol
### T2 — run-worktree tests fold behind shared helpers; the checkout test moves to check-run
Delivers: B2, B4, B5, B6 · Blocked by: T1 · Lane: logic
Budget: code +0 · tests +0
Seam: `test_run_worktree.py` and `check()` in `test_check_run.py`
Accept:
- [x] `test_run_worktree.py` → under 35 tests and 597 lines, `grep -c check-run` 0; its five checkout cases pass in `test_check_run.py` (B2)
- [x] `compare.py base t2` → `lost 0` for covmap on all three scripts and for run-worktree.py mutants (B4, B5)
- [x] `receipts/mapping.md` → a row per removed test naming the test and case holding each assertion; run-worktree assertions 155 → N (B6)
Verify: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests -p 'test_[cr]*.py' && (cd .workflow/lean-workflow-tests && python3 scripts/compare.py base t2)` (pre: 89 tests OK, then compare.py new file)
Skills: none
Status: done @ e86f78a
Writer: GPT-6.1 Sol
### T3 — check-run tests: date-only cases and duplicates gone, single cases in tables
Delivers: B1, B4, B5, B6 · Blocked by: T2 · Lane: logic
Budget: code +0 · tests +0
Seam: `test_check_run.py`
Accept:
- [ ] `test_check_run.py` → under 54 tests and 566 lines; the five F10 cases and two tests gone, `test_budget_plan_with_size_and_budgets_is_clean` gone (B1)
- [ ] the same file → the one-entry WORKLOG is a case of the worklog test, and `test_override_validation` keeps one valid row and one bad row (B1)
- [ ] `compare.py base t3` → `lost 0` for covmap on all three scripts and for check-run.py mutants (B4, B5)
- [ ] `receipts/mapping.md` → a row per removed test and per merged test of check-run; assertions 89 → N (B6)
Verify: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests -p test_check_run.py && (cd .workflow/lean-workflow-tests && python3 scripts/compare.py base t3)` (pre: 54 tests OK, then compare.py new file)
Skills: none
Status: todo
### T4 — next-step tests: routing tests folded, failure checks share one helper
Delivers: B3, B4, B5, B6 · Blocked by: T3 · Lane: logic
Budget: code +0 · tests +0
Seam: `test_next_step.py`
Accept:
- [ ] `test_next_step.py` → under 31 tests and 467 lines; `grep -c Traceback` 1, inside the shared failure helper (B3)
- [ ] `compare.py base t4` → `lost 0` for covmap on all three scripts and for next-step.py mutants (B4, B5)
- [ ] `receipts/mapping.md` → a row per removed test and per merged test of next-step; assertions 91 → N (B6)
Verify: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests -p test_next_step.py && (cd .workflow/lean-workflow-tests && python3 scripts/compare.py base t4)` (pre: 31 tests OK, then compare.py new file)
Skills: none
Status: todo
### T5 — Close: full comparison, suite time, ROADMAP step 4 and AGENTS.md
Delivers: B4, B5, B7, B8 · Blocked by: T4 · Lane: mechanical
Budget: code +0 · tests +0
Seam: `compare.py base final`, ROADMAP.md, AGENTS.md
Accept:
- [ ] `compare.py base final` on a full run of all three scripts → `lost 0` for every script and kind (B4, B5)
- [ ] ROADMAP.md step 4 → `Done 2026-…` with tests, cases, lines and median suite time, Base and after (B7)
- [ ] AGENTS.md → `The workflow suite takes about N s`, N from `receipts/time-final.txt` (B7)
- [ ] `git diff --stat aefd430..HEAD -- ` the three scripts → empty (B8)
Verify: `git diff --quiet aefd430..HEAD -- .github/skills/workflow/scripts/check-run.py .github/skills/workflow/scripts/next-step.py .github/skills/workflow/scripts/run-worktree.py && grep -q '^| 4 |.*Done 2026-' ROADMAP.md && grep -qE 'workflow suite takes about [0-9]+ s' AGENTS.md && (cd .workflow/lean-workflow-tests && python3 scripts/compare.py base final)` (pre: diff quiet, then ROADMAP grep fails)
Skills: none
Status: todo
## Coverage
- Outcome → T5: the full-suite compare, the ROADMAP row and the timing receipts
- B1 → T3 · B2 → T2 · B3 → T4 · B4 → T1, T2, T3, T4, T5 · B5 → T1, T2, T3, T4, T5 · B6 → T2, T3, T4 · B7 → T5 · B8 → T5
- Out of scope: Worktree setup as a script, new tests for surviving or unreached mutants, the 133-case greedy minimum, in-process calls and faster fixtures, a standing simplify rule, the checkup suite → untouched
## Risks
- T3 is the riskiest: check-run has the most cases, and its mutation run takes about 40 min.
- T4's helper adds a `Traceback` check to tests that lacked one; a script that prints one is a finding, never a test edit.
- Option not taken: check only line coverage per ticket. P1 calls 10 tests redundant that each catch a mutant no other test catches.

## TODO impacts
none

## Product doc impacts
- ROADMAP.md: step 4 "Open: no brainstorm until the numbers show growth is still a problem" becomes `Done` with the numbers (T5). Wrap moves the goal to `ROADMAP_ARCHIVE.md` (D7).
- AGENTS.md: "about a minute" becomes the measured time (T5).
- No PRODUCT.md or DESIGN.md.
