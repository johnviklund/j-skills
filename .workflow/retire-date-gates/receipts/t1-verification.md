Command: workflow execute retire-date-gates
Created: 2026-10-21 · GPT-6.1 Sol
Base: 984abb3
Inputs: .workflow/retire-date-gates/plan.md @ 6a2dec0
Status: complete

T1 implements B1–B6. Reuse search confirmed `Report.done` and `git_out`; no helper added.
The `skills/workflow` path is a symlink; tracked edits live in `.github/skills/workflow`.
Freshness against 6a2dec0: no changes in the tracked ticket files before execution.
No AGENTS.md or root MEMORY.md exists. Read skills/workflow/MEMORY.md; no additional pages apply.
Baseline uses the plan's command; this repo declares no separate build, lint or typecheck.

- Baseline: `python3 -m unittest discover -s skills/workflow/scripts/tests`, 44 tests passed.
- Red: updated date and done-state cases produced 16 expected failures across 47 tests.
- Green: the same command passed all 47 tests, exit 0.
- Repository: `python3 skills/workflow/scripts/check-run.py --all`, exit 0, zero errors and warnings.
- Whitespace: `git diff --check`, exit 0.
- Growth: checker +35/-59, tests +63/-33; net code -24, tests +30.

Six mutations failed their targeted tests: dropping the clean-brief condition; dropping the tracked-brief
condition; treating complete briefs as done; running rules on committed done briefs; skipping the parked
limit; skipping the old plan's Budget warning. Each change was restored.
The done-state fixture also checks an unrelated dirty receipt does not reopen a finished run.

Existing assertions changed for the approved new rules: older plans now warn or error; the ratio is
1.5× with net test lines; bare deviations no longer hide overruns; old reviews require cycle approval.
Assertions: 61 before, 66 after. No clean-case assertion was weakened. Fixture budgets now include a
reason for larger test budgets; the empty-Budget fixture strips that reason before making its Budget empty.
The old plan-limit fixture no longer adds nine behaviours, so it isolates the acceptance-line limit.
