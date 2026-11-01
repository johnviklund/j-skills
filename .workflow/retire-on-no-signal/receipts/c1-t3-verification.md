# C1-T3 verification

- Reuse search found no existing six-word summary helper. Two inline expressions serve both normal report branches.
- Red: 711f01a. Focused new case fails because the candidate lines omit change words.
- Green: the focused suite runs 10 tests, OK, exit 0.
- Normal output from this repo now distinguishes both same-date `understand` rows.
- Sweep formatting and verdict wording stay unchanged.
- Mutation checks: omitting row words, removing the ellipsis, and inverting its length guard each fail the new case.
- Existing assertion calls: 18 before, 18 retained; 3 new calls make 21 total.
- Four expected verdict strings gain the required `push guard` prefix. No verdict expectation was weakened or removed.
- No test file changes after the Red commit.
