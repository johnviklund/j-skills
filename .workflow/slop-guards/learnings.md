## Phase 3 — execute (2026-10-08)
- [durable→skill] `unittest -k` matches case-sensitively against module.Class.method: a CamelCase class name does not match a lowercase keyword, so 2 of 4 tests ran silently. Put the Verify keyword in each test method name and check the `Ran N tests` count, not just OK.
