# C1-T4 verification

- Baseline reused from C1-T3 at 7fa0e3d: workflow 124 tests OK; checkup 19 tests OK. Later commits before this session touched only this run's records.
- Reuse search found rows() and the existing tag matcher. rows() now optionally reads closed rows; one predicate matches both active and historical rows.
- Red: d3d54b6. The kept and archived subcases both fail on unwanted warnings; the missing archive subcase passes.
- Green: trial suite runs 11 tests, OK, exit 0. Active saves, ambiguous tags and sweep row counts remain covered.
- Seven independent mutations fail: filtering closed rows, bypassing the trialing filter, suppressing active ambiguity, warning on closed tags, suppressing unmatched tags, ignoring the archive, and reading a missing archive.
- Full suites: Ran 124 tests in 55.784s, OK; Ran 20 tests in 3.991s, OK; command exit 0.
- Existing test assertions unchanged. Test file untouched after Red commit.
