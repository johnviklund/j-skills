## Phase 3 — execute (2026-10-08)
- [durable→skill] `unittest -k` matches case-sensitively against module.Class.method: a CamelCase class name does not match a lowercase keyword, so 2 of 4 tests ran silently. Put the Verify keyword in each test method name and check the `Ran N tests` count, not just OK.
- [durable→skill] Verify keywords must not be substrings of other tickets' test names: `-k budget` also matched T2's `test_overrun_net_lines_over_twice_budget_warns`, so T1's Verify went red during T2's red step. Pick keywords unique across the suite.
