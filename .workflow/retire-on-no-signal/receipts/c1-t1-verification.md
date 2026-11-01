# C1-T1 verification

- Reuse search found the existing subprocess helpers `rows`, `tag`, `scan` and `worklog`; all remain in use.
- Added three parametrized tests, 45 lines. Production code and existing assertions stay unchanged.
- Focused Verify: 9 tests, OK, exit 0.
- Mutation run copied production code outside the repo and pointed the real CLI suite at each copy.
- Every mutation below was applied alone. All 19 failed the suite; the original passed.

| Mutation | Result |
|---|---|
| Remove impact row filter | red |
| Remove non-tag guard | red |
| Remove date guard | red |
| Remove review cycles guard | red |
| Remove deviations guard | red |
| Remove skills guard | red |
| Return unsorted worklog entries | red |
| Include the row date in the before window | red |
| Include the row date in the after window | red |
| Use first N before entries | red |
| Use last N after entries | red |
| Omit sweep numbers | red |
| Omit kept verdict numbers | red |
| Print 1 saves | red |
| Remove default current-directory repo | red |
| Remove repo deduplication | red |
| Remove repo directory check | red |
| Stop catching filesystem errors | red |
| Resolve installed impact from wrong parent | red |
