# T1 mutation fixture correction

The prototype copies scripts/ but not its sibling ROUTING.md. Two existing tests read that file:
- test_check_run.SeatTests.test_override_validation
- test_next_step.NextStepTests.test_real_routing_resolves_all_thirteen_run_keys

An unmutated prototype copy fails those two methods with four assertion failures and one error.
The error names missing ROUTING.md; the override checks receive empty stdout.

Of the prototype's 392 caught check-run mutants, 32 fail only those two methods.
The exact 392 baseline therefore cannot establish preservation of real mutation catches.
The next-step and run-worktree prototype results have zero catches relying only on those methods.

The corrected fixture copies ROUTING.md alongside scripts/. Tests and production scripts stay intact.
The full mutation run was stopped rather than recording incomplete or invalid results.

Corrected unmutated temporary copy: 120 tests in 52.004s, OK, exit 0.

Confirmation: check-run.py:55:19:40->41, reported caught by the prototype, survives
with the corrected fixture and all mapped tests. No tests fail.

Human approved regenerating and using the corrected baseline; later changes must lose no valid catch.

Mutation runs use --failfast: a failed mapped test proves a catch; survivors run all mapped tests.
Killer lists then name first failures only. Full owner-list tools require omitting --failfast.

Final repo-suite check during mutation workload: workflow 120 tests in 84.730s OK;
checkup 8 tests in 0.833s OK; combined command exit 0.
