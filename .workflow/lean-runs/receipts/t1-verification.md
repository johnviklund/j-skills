Command: workflow execute lean-runs
Created: 2026-10-17
Base: 151ba27
Inputs: .workflow/lean-runs/plan.md @ b675349
Status: complete

T1: Run size limits
- Baseline: 34 tests pass; check-run reports 0 errors and 0 warnings. Human selected this baseline in chat.
- Reuse: Doc.slop_gated, check/BRIEF/sized fixtures, and the existing approval-line regex shape; no new helper.
- Red: LimitTests fails for 9 behaviours, the old under-5 warning, and 21 acceptance lines.
- Green: LimitTests runs 2 tests with parametrized cases; full suite runs 36 tests, all pass.
- Boundaries: 8 behaviours and 20 acceptance lines pass; 9 and 21 error without a recorded refusal.
- Refusals pass; artifacts created 2026-10-16 retain 0 errors at 9 behaviours and 21 acceptance lines.
- Mutation: each count comparison changed from > to >= independently makes its boundary case fail; restored, 2 tests pass.
- git diff --check passes. No existing test assertions changed. No screen changes.
