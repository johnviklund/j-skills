# T1 case-count mismatch

The old prototype map and regenerated Base map each contain 120 methods and 274 context entries.
Eight outer method entries coexist with subtest entries. Counting those methods only by their
subtests yields 266 cases under the brief's definition.

The eight methods are:
- NextStepTests.test_brief_drafting_parked_and_done
- NextStepTests.test_brief_plan_card_and_json
- NextStepTests.test_open_finding_needs_patch_or_recheck
- NextStepTests.test_override_model_keeps_route_policy
- NextStepTests.test_p0_fix_keeps_lane_approval
- NextStepTests.test_patch_ticket_routes_by_severity_and_lane
- WhereTests.test_Where_checks_slugs_and_primary_fallback
- WhereTests.test_Where_skips_a_run_landed_from_another_clone

Line/branch-arm totals match T1: check-run 630/673, next-step 204/229, run-worktree 188/170.
The new coverage receipt reports 266 cases. Production scripts and tests remain unchanged.
The comparator catches a removed coverage item and a removed caught-mutant item in temporary fixtures.
The full mutation run was stopped when this mismatch was identified; no mutation receipt is complete.
Baseline: workflow 120 tests in 52.675s OK; checkup 8 tests in 0.428s OK; command exit 0.
Timed runs: 52.078s, 52.312s, 52.383s; median 52.312s; 120 tests OK each.

Human approved option 1a: use 266 cases and retain the brief definition.
