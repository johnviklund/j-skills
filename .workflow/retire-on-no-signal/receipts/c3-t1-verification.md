# C3-T1 verification

Writer: GPT-6.1 Sol
Reuse: the existing rows, row and subprocess helpers cover both malformed archive cases.
Change: tests only, four net lines within the five-line budget.
Existing assertions: two before, three after; exit 2 and the archive location stay unchanged.
The added assertion checks the reported cell count for both five and seven cells.

Before the change, `len(cells) != 6` as `< 6` passes all 16 focused tests.
After the change, each mutation runs alone in a temporary copy:
- `< 6` fails on the seven-cell case because stderr lacks the archive location, exit 1.
- `> 6` fails on the five-cell case because stderr lacks the archive location, exit 1.
Production code stays unchanged. No red commit is required by this test-only ticket.

Focused Verify: 16 tests, OK, exit 0.
Baseline: workflow 124 tests OK; checkup 25 tests OK, exit 0.
Final command: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests && python3 -m unittest discover -s .github/skills/checkup/scripts/tests`
```text
Ran 124 tests in 63.259s
OK
Ran 25 tests in 4.473s
OK
```
Exit 0. `git diff --check` passes. No screen changes.
