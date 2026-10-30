# C2-T1 verification

Writer: GPT-6.1 Sol · high
Reuse: started() calls the existing checks.decisions(checks.Doc(...)) parser.
The existing OpenTests repository fixture drives the real open command.
No new helper or dependency. Docs read: no PRODUCT.md or DESIGN.md in scope.

Red commit: 056a042 contains only the new parametrized test, 19 added lines.
The execute case expects '.', an unchanged worktree list and preserved pending code.
The plan case expects '.worktrees/B' and preserved pending code.
Targeted red: 1 test, 1 failure, exit 1; execute returned '.worktrees/B' instead of '.'.
Required suite at red: 112 workflow tests, 1 failure, exit 1; checkup skipped by &&.

Green targeted command:
```text
python3 -m unittest discover -s .github/skills/workflow/scripts/tests -p test_run_worktree.py -k test_Open_resumes_first_ticket_with_an_execute_decision
Ran 1 test in 0.477s
OK
exit 0
```
Content check:
```text
grep -c 'started ticket or an execute decision' .github/skills/workflow/references/worktrees.md
1
exit 0
```

Three independent mutations run in temporary copies; production files stay unchanged.

- Ignore the execute decision: 1 test, 1 failure, exit 1.
- Invert the execute phase comparison: 1 test, 2 failing cases, exit 1.
- Remove the missing-file guard: existing free-primary test fails, exit 1.

Final required command and result:
```text
python3 -m unittest discover -s .github/skills/workflow/scripts/tests && python3 -m unittest discover -s .github/skills/checkup/scripts/tests
Ran 112 tests in 46.925s
OK
Ran 8 tests in 0.412s
OK
exit 0
```
Existing assertion changes: 0. Assertion calls in test_run_worktree.py: 148 to 152.
The fix changes no test file relative to the red commit.
Ticket growth across red and fix: code +3, tests +19; combined +22 against budget +17.
The extra five test lines keep both acceptance cases and preservation checks readable.
The skill-impact row records the checkout fix alongside the existing unattended-mode change.
