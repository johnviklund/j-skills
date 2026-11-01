T2 verification
- Baseline reused from T1 at 3aeab1c; only run records changed afterward.
- Red: 6 tests; new verdict cases failed because normal mode printed nothing.
- Verify: 6 tests OK; both seats documentation grep checks passed.
- Final suites: workflow 124 tests in 55.859s, OK; checkup 15 tests in 3.129s, OK; exit 0.
- Mutations: better comparison, completion boundary, trial unit, save verdict, missing before, after date, before date, skill evidence each went red.
- Existing assertions changed: 0. No UI changes.
- All printed numerical verdicts include before/after means. Sweep preserves its original compact output when no worklog entries exist.
- Read-only preview: 37 rows, 11 keep, 26 candidate, 0 insurance, 0 unmatched tags.
- New impact row is deferred until after T3's fixed 37-row sweep, preserving the approved receipt count.
