## Phase 3 — execute (2026-10-31)
- [durable→memory] Mutation results need an unmutated temporary-copy control. Missing sibling configuration made two tests fail and inflated the prototype's caught count.
- [durable→memory] Coverage contexts are not test cases. Eight outer contexts accompanied subtests; counting them twice inflated the Base from 266 to 274.
- [drop] Fail-fast preserves caught/survived outcomes while reducing mutation time; its killer lists contain first failures, so full owner analysis needs fail-fast disabled.
