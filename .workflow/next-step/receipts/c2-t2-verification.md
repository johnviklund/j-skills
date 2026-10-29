Command: workflow execute next-step · C2-T2
Created: 2026-10-29 · GPT-6.1 Sol
Base: 5c5e306
Inputs: .workflow/next-step/patch_plan.md @ 688e443
Status: complete

Reused the existing check() and review() fixtures. No helper or production change.

- Baseline: workflow 107 tests, `OK`; checkup 8 tests, `OK`; exit 0. Freshness diff from patch Base to entry HEAD was empty for ticket files.
- Before the new test, isolated inverted and never-true `if open_finding(f):` mutations both pass all 50 checker tests.
- Verify: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests -p test_check_run.py`. Runs 51 tests, `OK`, exit 0.
- The new parametrized test checks the positive note with an unresolved finding and with a valid resolution commit. The closed case also excludes the open-note form.
- After the new test, the same two isolated mutations fail test_check_run.py, each exit 1, at the new test. Both mutations are caught, 2 of 2. Production check-run.py remains unchanged.
- Full: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests && python3 -m unittest discover -s .github/skills/checkup/scripts/tests`. Workflow 108 tests, `OK`; checkup 8 tests, `OK`; exit 0.
- Existing assertions remain unchanged. Checker assertion lines increase from 77 to 79. Code net +0; tests net +10, within the +12 test budget. No deviation.
