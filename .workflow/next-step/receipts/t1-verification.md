Command: workflow execute next-step
Created: 2026-10-29
Base: e515c8a
Inputs: .workflow/next-step/plan.md @ 19533a5
Status: complete

## T1 result
- Writer: GPT-6.1 Sol, xhigh. Checkout: primary, main; open and where both returned `.` after refreshing origin.
- Readiness and freshness passed. No AGENTS.md exists. The human confirmed the documented baseline, `python3 -m unittest discover -s scripts/tests` from `.github/skills/workflow`.
- Baseline: 82 tests passed. Final suite: 86 tests passed in 40.574 seconds. No existing assertions changed.
- Verify: `python3 -m unittest discover -s scripts/tests -p test_next_step.py && wc -c ROUTING.md` passed: 4 tests; ROUTING.md 5,453 bytes, below 5,500.
- Fixture CLI checks prove the plan assignment, JSON schema version 1, exact card/stdout equality, `/` prefix, trial selection and primary fallback, and empty stdout with named errors for bad routing.
- The real routing tables parse and all 13 run-state keys resolve. Four additional command keys preserve patch-plan, todo, bootstrap and realign mappings.
- Red: before implementation, 4 tests failed or errored because next-step.py did not exist. Before the table conversion, only the real-routing test failed on the old columns.
- Mutations: 18 of 18 caught. Removed guards for header columns, row width, required cells, duplicate rows, missing header, model width, empty model components, model effort, phase effort, context, approval, unknown seat and missing phase; changed trial selection/marker, fallback splitting, inherited effort and primary trial fallback. Each made the targeted suite fail. All changes restored.
- A surviving required-cell mutation prompted an empty phase-description case. The restored guard rejects it; removing that guard now fails the test.
- Reuse search found the importlib loader in run-worktree.py and check-run.py's Doc/header parser. The new script reuses both. No routing or card helper existed.
- `git diff --check` and Python compilation passed. No build, lint or typecheck command was specified.
- T1 adds 126 code lines and 111 test lines, within its combined 240-line budget. No visible screen changes or unrelated edits.
- Scope: T1 handles brief-only runs. T2 adds plan routing. T1 uses xhigh; T2 uses high, so the execution rule requires the next session.
