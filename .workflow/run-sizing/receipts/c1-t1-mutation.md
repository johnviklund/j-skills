# C1-T1 — mutation receipt

Test: `SizingTests.test_sizing_six_acceptance_lines_are_valid` (six-line ticket → `· 0 errors`).

| Step | Command | Result |
|---|---|---|
| pre | `python3 -m unittest discover -s .github/skills/workflow/scripts/tests -k six_acceptance` | Ran 0 tests, OK |
| mutate | `check-run.py:300` `len(accepts) <= ACCEPT_MAX` → `< ACCEPT_MAX` | Ran 1 test, FAILED (failures=1): `T1: 6 acceptance lines; a ticket has 1-6` · `1 errors` |
| restore | `git diff --stat -- check-run.py` | empty |
| green | same `-k six_acceptance` | Ran 1 test, OK |
| sizing | `-k Sizing` (includes the seven-line rejection) | Ran 4 tests, OK |
| full | `python3 -m unittest discover -s .github/skills/workflow/scripts/tests` | Ran 31 tests, OK |
