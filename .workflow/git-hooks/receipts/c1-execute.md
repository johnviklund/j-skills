Command: workflow execute git-hooks
Created: 2026-11-01 · GPT-6.1 Sol
Base:    a2d308f
Inputs:  .workflow/git-hooks/patch_plan.md @ 6ea2df2
Status:  drafting

## C1-T1
- Baseline: workflow 119 tests OK; checkup 9 tests OK; exit 0.
- Red 860ebb2: PrePush ran 3 tests, spaced-target secret push returned 0; 1 failure.
- Green: PrePush 3 tests OK; workflow 120 tests OK; checkup 9 tests OK; exit 0.
- Invalid outgoing revision probe: refused and local ref named. Removing the revision guard accepts it, so the assertion fails.
- Mutation M14: removing the delete skip makes the existing PrePush delete assertion fail.
- Fix commit leaves the red commit's test file untouched. No existing assertion changed.

## C1-T2
- Reused HookRepo fixture and the existing staged-path test; no helper added.
- Hook suite: 10 tests OK. Full workflow: 122 tests OK; checkup: 9 tests OK; exit 0.
- M7, M10, M11, M22 each produce exactly one assertion failure in a disposable copy.
- Existing assertions: 46 before and 46 retained; 8 assertions added. No existing assertion changed or removed.
