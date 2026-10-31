# Assertion mapping

T2 static assertion calls: test_run_worktree.py 155 → 126; test_check_run.py 89 → 92.
Three checkout assertions move intact. Fourteen pairs of command assertions move to two shared
assertions in RepoTests.run_command; the same expected values and checks still execute at each call.

| Before | After | Assertions retained |
|---|---|---|
| test_run_worktree.CheckoutTests.test_Checkout_warnings_exempt_only_the_matching_run_checkout | test_check_run.CheckoutTests.test_Checkout_warnings_exempt_only_the_matching_run_checkout, five unchanged path/branch cases | warning-flag tuple, exit 0, `== x` banner |
| test_Open_keeps_primary_free_for_an_unstarted_run | same method → RepoTests.run_command(expected=…) | exit 0 and the original stripped-stdout value |
| test_Open_excludes_multiple_isolated_runs_once | same method → RepoTests.run_command(expected=…) | exit 0 and the original stripped-stdout value |
| test_Open_keeps_started_run_with_its_uncommitted_work | same method → RepoTests.run_command(expected=…) | exit 0 and the original stripped-stdout value |
| test_Open_isolates_a_second_run | same method → RepoTests.run_command(expected=…) | exit 0 and the original stripped-stdout value |
| test_Open_keeps_a_free_primary_checkout | same method → RepoTests.run_command(expected=…) | exit 0 and the original stripped-stdout value |
| test_Open_preserves_dirty_files_and_excludes_once | same method → RepoTests.run_command(expected=…) | exit 0 and the original stripped-stdout value |
| test_Open_keeps_dirty_checkout_busy_with_an_unstarted_run | same method → RepoTests.run_command(expected=…) | exit 0 and the original stripped-stdout value |
| test_Open_resumes_first_ticket_with_an_execute_decision | same method → RepoTests.run_command(expected=…) | exit 0 and the original stripped-stdout value |
| test_Where_uses_local_refs_when_origin_is_unreachable | same method → RepoTests.run_command(expected=…) | exit 0 and the original stripped-stdout value |
| test_Where_recovers_an_unpushed_local_branch | same method → RepoTests.run_command(expected=…) | exit 0 and the original stripped-stdout value |
| test_Where_without_origin_uses_the_primary_checkout | same method → RepoTests.run_command(expected=…) | exit 0 and the original stripped-stdout value |
| test_Where_finds_an_existing_worktree | same method → RepoTests.run_command(expected=…) | exit 0 and the original stripped-stdout value |
| test_Where_recovers_and_fast_forwards_another_clone | same method → RepoTests.run_command(expected=…) | exit 0 and the original stripped-stdout value |
| test_Where_skips_a_run_landed_from_another_clone | same method → RepoTests.run_command(expected=…) | exit 0 and the original stripped-stdout value |

Reuse search: existing RepoTests.run_command and check() cover both fixture needs; no new helper.
No assertion expectation changed or was removed. Static call count falls because repeated calls share one definition.
