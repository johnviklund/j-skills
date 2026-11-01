# C2-T2 verification

Writer: GPT-6.1 Sol
Reuse: the existing rows, worklog and subprocess scan helpers cover all three cases.
Change: three regression tests, 16 added lines. Existing assertions are unchanged.

Each mutation ran alone in a temporary copy, with no production edits:
- Remove `after` from `before and after and`: old suite exits 0; new test_trial_without_after_runs fails, exit 1.
- Print the raw Skill cell instead of the first normalized name: old suite exits 0; new test_finished_multiskill_candidate fails, exit 1.
- Change `len(words) > 6` to `>= 6`: old suite exits 0; new test_change_at_six_word_boundary fails, exit 1.

The focused Verify runs 16 tests, OK, exit 0.
Baseline: workflow 124 tests OK; checkup 22 tests OK, exit 0.
Final command: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests && python3 -m unittest discover -s .github/skills/checkup/scripts/tests`
```text
Ran 124 tests in 64.462s
OK
Ran 25 tests in 5.351s
OK
```
Exit 0. No production or screen changes. The one-line test budget overrun is recorded in patch_plan.md.
