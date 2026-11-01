# C2-T1 verification

Writer: GPT-6.1 Sol
Red: 81bd914. Tests only, 13 added lines. The two new cases fail on the old parser.
Fix: a8b72da. Parser only, 5 added lines and 2 removed. Test files untouched.

Reuse search confirmed `rows()` is the only impact-table parser. The other split calls read run artifacts.
Fixtures cover escaped pipes in backticks, multiple escaped pipes, and a five-cell archive row at line 3.
Existing test assertions are unchanged.

The ticket's exact Verify command exits 0. The focused suite runs 13 tests, OK.
Both real-repo report commands exit 0. The sweep prints 27 labels for 27 trialing rows and zero tag warnings.

Each mutation alone makes the focused suite exit 1:
- Split every pipe instead of only unescaped pipes.
- Disable the six-cell guard.
- Narrow `except (OSError, ValueError)` to `except OSError`.
- Start line numbers at zero.

All mutations were restored before the final checkup suite.

Baseline:
```text
Ran 124 tests in 56.277s
OK
Ran 20 tests in 3.916s
OK
```

Final command: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests && python3 -m unittest discover -s .github/skills/checkup/scripts/tests`
```text
Ran 124 tests in 56.252s
OK
Ran 22 tests in 4.093s
OK
```
Exit 0. No pre-existing failures. No screen changes or deviations.
