Command: workflow execute lean-runs
Created: 2026-10-17
Base:    e92cdbe
Inputs:  .workflow/lean-runs/patch_plan.md @ aafea80
Status:  complete

## C1-T1
- Writer: GPT-6.1 Sol, from the harness runtime record and live model catalog.
- Baseline: full suite 38/38 passes; check-run has 0 errors and 0 warnings.
- Reuse search found `RatioTests.test_committed_test_ratio`, `plan()`, `check()` and `lines()` in the existing test file. Added one tuple; no new helper or assertion changes.
- Added case: contract lane, plan created 2026-10-16, code +50, tests +151. The existing assertion requires `0 errors` in the check-run CLI output.
- Verify: `python3 -B -m unittest discover -s .github/skills/workflow/scripts/tests -k RatioTests` exits 0, 2 tests pass.
- Mutation: replace `lanes = ("logic", "contract") if lean else ("logic",)` with `lanes = ("logic", "contract")` in check-run.py.
- Mutation result: exit 1, 2 tests run, 1 failure in the new contract/151/2026-10-16 case. Output reports `tests +151 over 3× code +50` instead of `0 errors`.
- Restored the checker in a `finally` block. The final diff contains no checker changes.
- Restored full suite: `python3 -B -m unittest discover -s .github/skills/workflow/scripts/tests` exits 0, 38 tests pass.
- Checks: `python3 -B .github/skills/workflow/scripts/check-run.py lean-runs` exits 0, 0 errors and 0 warnings; `git diff --check` exits 0.
- Commit: e92cdbe changes only the added case, tests +2/-1, code +0.
- Try it: none; no screen changes. The CLI fixture and mutation prove the legacy lane rule.
- Noticed: none. The pre-existing untracked test __pycache__/ remains untouched. Deferred C1-2 through C1-4 remain in review.md.
