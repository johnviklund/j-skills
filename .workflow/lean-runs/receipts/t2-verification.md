Command: workflow execute lean-runs
Created: 2026-10-17
Base: f8fdbd3
Inputs: .workflow/lean-runs/plan.md @ b675349
Status: complete

T2: Test ratios and Budget reasons
- Reuse: check_overrun, check_sizing, Doc.slop_gated, field, and existing check/plan/lines fixtures; no new helper.
- Red: RatioTests fails for tests +76 / code +50 in both new lanes, then for a Budget without a reason.
- Green: RatioTests runs 2 tests with parametrized cases; full suite runs 38 tests, all pass.
- Both new lanes error at tests +76 / code +50 and pass at +75 / +50. A 2026-10-16 contract ticket stays at 0 errors.
- Budget tests +120 / code +60 warns without a same-line reason and is quiet with one. Older plans stay quiet.
- Same-line check: a reason on another line fails red before the line-number check, then passes green with the warning required.
- Mutations: > to >= at the ratio boundary, removing contract, forcing the new ratio onto old logic, and inverting the Budget comparison each fail. Restored, RatioTests passes.
- Existing assertions unchanged; git diff --check passes. No screen changes.
