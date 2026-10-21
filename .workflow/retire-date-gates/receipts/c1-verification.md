Command: workflow execute retire-date-gates
Created: 2026-10-21 · GPT-6.1 Sol
Base:    2aac08b
Inputs:  .workflow/retire-date-gates/patch_plan.md @ 188f48a
Status:  complete

## Scope and baseline
- Patch cycle 1 fixes C1-1 and C1-2. C1-3 remains deferred.
- The patch plan is complete and check-run passes before execution.
- No ticket files changed between its Base 188f48a and entry HEAD 12cd159.
- Baseline command: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests`.
- Baseline result: exit 0, 47 tests passed. No AGENTS.md or separate build, lint or typecheck command exists in this checkout.
- The live model catalog includes GPT-6.1 Sol and the next review's Opus 5.5 and Sonnet 5.5.
- Reuse search found parse_tickets, field, git_has, Report.missing_sha, Doc, check, plan and review. No helper added.

## C1-T1
- Red commit: 380c292. Two new tests each fail on two dangling-pointer cases.
- Ticket cases cover plan.md and patch_plan.md. Review cases isolate finding resolutions and the Resolved table.
- Each pointer kind also has a valid-commit case, which remains clean.
- Fix commit: fbb1fdc. Finished runs inspect pointers without invoking ticket or review rule checks.
- Verify: full suite exits 0, 49 tests pass. Missing Size stays unreported for finished reviews.
- Mutation: invert the ticket SHA existence check in a temporary copy. The test fails on all four subcases.
- Mutation: invert the review SHA existence check in a temporary copy. The test fails on all four subcases.
- Actual change across red and fix commits: code +15, tests +23.

## C1-T2
- Red commit: c88dc8e. The parked draft's missing Outcome produces an error instead of the expected warning.
- Fix commit: 2aac08b. Required sections use complete/done strictness; the behaviour limit applies to every status except drafting.
- Verify: full suite exits 0, 50 tests pass, including the existing nine-behaviour parked case.
- Mutation: restore parked section strictness in a temporary copy. The missing-section test fails.
- Mutation: restore the behaviour limit's strict gate in a temporary copy. The nine-behaviour parked test fails.
- Actual change across red and fix commits: code +2/-2, tests +6.

## Final checks
- `python3 skills/workflow/scripts/check-run.py --all`: exit 0; all six runs have 0 errors and 0 warnings; repo has 0 warnings.
- `git diff --check`: exit 0.
- Existing assertions remain unchanged. Unittest assertion calls increase from 66 to 75.
- No user-visible screen changes, new helper, or scope deviation.
- Review cycle 1 findings remain unchanged for the next reviewer to resolve against these commits.
