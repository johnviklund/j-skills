Command: workflow review slop-guards
Created: 2026-10-08
Base:    5c8f68a5e673e5fbc493060d8283fbe5bd2fb868
Inputs:  plan.md @ 85b5b9e
Status:  complete

## Checks
- `python3 -m unittest discover -s .github/skills/workflow/scripts/tests -v`: 16 tests, OK.
- Every ticket's exact Verify command ran. T1–T5 selected 5, 4, 3, 2, 3 tests respectively; all passed.
- T3 document counts: 4, 1. T4: 4, 3. T5: 0 dependency hits, 2 wrap matches.
- T6: 1 Simplicity block, 176 hub lines, 3 template fields, 3 reuse/acceptance matches.
- T7: 7 test rules, 69 lines, 0 old phrases, 2 mutation matches. T8: four counts of 1.
- Read the changed instructions against B11–B15, including operator risk, retire approval and full-suite recheck.
- `git diff --numstat 85b5b9e..5c8f68a -- . ':(exclude).workflow'`: code +89/-3, tests +186/-0, ratio 2.09, net +272.
- No touched file exceeds 1,000 lines. No added escape-hatch matches. No changed pre-existing tests.
- Tracked non-receipt dependency scan found zero literal run-folder paths outside the run folders.
- `python3 .github/skills/workflow/scripts/check-run.py --all`: 0 errors; existing 131-line plan warning; 0 repository warnings.

## Reproduce C1-1 and C1-2
Run from the repository root. These calls reuse the test file's temporary-repository fixtures; they change no tracked file.

```python
import importlib.util
from pathlib import Path
p = Path('.github/skills/workflow/scripts/tests/test_check_run.py')
s = importlib.util.spec_from_file_location('fixtures', p)
m = importlib.util.module_from_spec(s)
s.loader.exec_module(m)
cases = [
    ('C1-1', m.plan(risk='cheap').replace('Risk: cheap', 'Risk:'), None),
    ('C1-2 zero', m.plan(t1_done=True).replace(
        'Budget: code +20 · tests +30', 'Budget: code +0 · tests +0'),
        {'src/app.py': m.lines(101)}),
    ('C1-2 blank', m.plan(t1_done=True).replace(
        'Budget: code +20 · tests +30', 'Budget:'),
        {'src/app.py': m.lines(101)}),
]
for label, plan, ticket in cases:
    print(label, m.check({'brainstorm.md': m.BRIEF, 'plan.md': plan}, ticket))
```

C1-1 prints `IndexError: list index out of range` at check-run.py:347, without a summary.
C1-2 zero and blank each print `0 errors · 0 warnings`.
Additional checks: a stated T1 deviation suppresses the +12/+178 ratio diagnostic; +12/+49 remains below the test floor.
Class checks: empty Risk also crashes in patch_plan.md; an empty contract Budget also reports zero warnings; a zero-budget receipt-only commit stays clean.

## Review artifact validation
`python3 .github/skills/workflow/scripts/check-run.py slop-guards` after writing the review and patch plan reports 0 errors, 1 existing plan-length warning, and 2 open fix-now findings.

## Mutation
Created a local clone and detached worktree under a temporary directory at 5c8f68a. Changed only `check-run.py:370` from `tests > TEST_RATIO * code` to `tests <= TEST_RATIO * code`.
Ran `python3 -m unittest discover -s .github/skills/workflow/scripts/tests -k test_overrun_tests_over_three_times_code_is_an_error` there.
Result: exit 1, `Ran 1 test`, `FAILED (failures=1)` because the expected `ERROR ... tests +178 over 3× code +12` was absent.
The temporary clone and worktree were removed. The primary checkout's code and tests were never edited.
