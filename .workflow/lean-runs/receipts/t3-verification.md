Command: workflow execute lean-runs
Created: 2026-10-17
Base: 2b6835a
Inputs: .workflow/lean-runs/plan.md @ b675349
Status: complete

T3: Docs state the new limits and one test per behaviour
- Baseline selected in chat: full unittest suite and check-run, with no separate build or lint. This session starts with 38 tests passing and check-run at 0 errors / 0 warnings.
- Reuse: existing Budgets, Testable, Inherited semantics and Test budget sections; no new helper or document section.
- Verify command output: 0 old per-acceptance-test instructions; 0 stale limit occurrences after joining lines across workflow docs and root README, excluding SKILL-IMPACT and WORKLOG.
- Positive checks: phase-2-plan contains one test per behaviour and parametrized cases; its Inherited semantics bullet contains at risk. SKILL.md contains 8 behaviours and 20 acceptance lines; tests.md contains 1.5×.
- Net lines: receipts/t3-net-lines.txt records the committed b675349..HEAD diff, net -2 lines.
- Docs also state same-line Budget reasons. Both READMEs stay unchanged, as decision 2a requires.
- Consistency correction: execute's Red step and tests.md's Red/green paragraph now use behaviour tests with acceptance cases, replacing the old one-test-per-line instructions.
- Mechanical ticket: content verification; no new tests, mutations or screenshots. Trigger description and routing are unchanged; no trigger suite is supplied for workflow.
- git diff --check passes. No product or UI files exist in scope.
