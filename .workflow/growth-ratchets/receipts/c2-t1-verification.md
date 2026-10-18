Command: workflow execute growth-ratchets
Created: 2026-10-18
Base:    cfa48ca
Inputs:  .workflow/growth-ratchets/patch_plan.md @ c8f2e48
Status:  complete

## C2-T1 proof
- Writer: GPT-6.1 Sol. The live thread configuration confirms medium effort for this P1 logic fix.
- Freshness: no ticket files changed between patch Base c8f2e48 and entry HEAD 528ca7b. The checkout was clean on main.
- Baseline: 42 tests pass; check-run reports zero errors. The prior approval for unittest, check-run and git diff --check still applies. No repo AGENTS.md, lint or typecheck command exists.
- Reuse: test_growth_ratio_waivers and test_growth_budget_waivers already loop over Deviations lines and assert error counts, ratio waiver warnings and budget warnings. One tuple per loop adds both cases; no fixture, helper or assertion changes.
- Red mutation: replace `+ kind +` with `+ r"(?:Ratio|Budget)" +` in check-run.py:389, then run `python3 -B -m unittest discover -s .github/skills/workflow/scripts/tests -k growth`.
- Mutation result: exit 1; four methods run, exactly two failures. `Budget waived: T1 — wrong kind` incorrectly removes the ratio error and emits a ratio waiver warning. `Ratio waived: T1 — wrong kind` incorrectly replaces the budget warning with a note.
- Restore: check-run.py matches its original bytes exactly; `git diff --exit-code -- .github/skills/workflow/scripts/check-run.py` exits 0. No checker change is committed.
- Green: the same Verify exits 0; four methods and 17 parameter cases pass. The wrong-kind budget waiver leaves one ratio error and no ratio waiver warning. The wrong-kind ratio waiver leaves zero errors and one budget warning.
- Full suite: `python3 -B -m unittest discover -s .github/skills/workflow/scripts/tests` exits 0; 42 tests pass.
- `python3 -B .github/skills/workflow/scripts/check-run.py --all` exits 0; every run has zero errors. The existing slop-guards 127-line warning remains.
- `git diff --check` exits 0. Existing assertions are unchanged.
- Commit: cfa48ca; two cases, three test lines added and one replaced, net +2. No production changes, deviations or screen changes.
- Next: cross-vendor review cycle 3 for C2-1, approved in review.md. C1-2 and C1-3 retain their recorded deferred dispositions.
