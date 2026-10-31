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


T3 static assertion calls: test_check_run.py Base 89 → T2 92 → T3 87.
The old cycle diagnostic check moves into the surviving approval test. The missing-budget check
is strengthened from `T2: no Budget:` to `T2: no Budget: line`, retaining both earlier checks.
The only removed cases differ solely by dates or repeat override validation already reached through next-step.

| Before | After | Assertions retained |
|---|---|---|
| LimitTests.test_plan_limits, 21 lines, no approval, old date | same method, 21 lines/no approval | 21-line error regex |
| RatioTests.test_committed_test_ratio, contract/76/old date | same method, contract/76 | warning count 1 and 0 errors |
| RatioTests.test_budget_ratio_reason, empty reason/old date | same method, empty reason | warning regex with tests +120/code +60 |
| BudgetTests.test_budget_old_plan_without_budget_warns | BudgetTests.test_budget_rules_warn, missing-budget case | exact `T2: no Budget: line` |
| CycleTests.test_cycle_three_old_review_still_needs_approval | CycleTests.test_cycle_three_without_approval_is_an_error | exact old `cycle 3 needs` error regex, alongside existing approval regex |
| BudgetTests.test_budget_plan_with_size_and_budgets_is_clean | SeatTests.test_brief_trust_boundaries_are_optional, empty-section case | exact 0 errors/0 warnings on the same plan() |
| WrapTests.test_wrap_done_with_retired_is_clean | WrapTests.test_wrap_worklog_entry_with_seats_is_clean, args x/one-entry worklog | 0 errors, same one-entry header, seats, skills, retired text and CLI selection |
| WrapTests.test_wrap_worklog_entry_with_seats_is_clean | same method, args --all/two-entry worklog | original 0 errors assertion and fixture |
| SeatTests.test_override_validation, missing-model and max-effort bad rows | NextStepTests.test_override_bad_rows_name_key_without_json, identical rows; kept check-run unknown-key case | next-step checks exit 1 and review diagnostic; kept invalid row checks check-run exit 1, ERROR format and key |
| BudgetTests.test_budget_missing_on_logic_ticket_warns | BudgetTests.test_budget_rules_warn, missing-budget case | stronger full diagnostic contains original prefix |
| BudgetTests.test_budget_acceptance_line_over_40_words_warns | BudgetTests.test_budget_rules_warn, 41-word case | original 41-word diagnostic |
| OperatorTests.test_operator_cheap_ticket_with_a_script_test_warns | OperatorTests.test_operator_script_test_respects_risk, cheap case | original cheap-script diagnostic |
| OperatorTests.test_operator_costly_ticket_may_test_its_script | OperatorTests.test_operator_script_test_respects_risk, costly case | original 0 errors/0 warnings |

ReviewTests single-result checks retain their original assertions, with the check() result passed directly.
Reuse search: existing check(), plan(), self.DONE and worklog() cover the fixtures; no new helper.
T3 also moves unittest.main() below the relocated CheckoutTests, so direct-file execution includes those cases.
