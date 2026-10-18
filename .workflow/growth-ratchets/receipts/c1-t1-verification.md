Command: workflow execute growth-ratchets
Created: 2026-10-18
Base:    ee191dc
Inputs:  .workflow/growth-ratchets/patch_plan.md @ c4ce7f0
Status:  complete

## C1-T1 proof
- Writer: GPT-6.1 Sol. The live thread configuration confirms medium effort after the routing change for a P1 logic fix.
- Freshness: no ticket files changed between patch Base c4ce7f0 and entry HEAD b862439. The checkout was clean on main.
- Baseline: 42 tests pass; check-run reports zero errors. The prior approval for unittest, check-run and git diff --check still applies.
- Reuse: test_growth_ratio_waivers already checks error counts, waiver warnings and allowed 90 through check(), plan() and lines(). One tuple adds the other-ticket case; no helper is added.
- Red mutation: replace re.escape(tid) with r"T\d+" in check-run.py:389, then run `python3 -B -m unittest discover -s .github/skills/workflow/scripts/tests -k growth`.
- Mutation result: exit 1; four methods run, exactly one failure, the new `Ratio waived: T2 — other ticket` case. It expects `1 errors` but sees `0 errors` and a waiver warning for T1.
- Restore: check-run.py matches its original contents exactly. No checker change is committed.
- Green: the same Verify exits 0; four methods and 15 parameter cases pass. The new case sees one error and zero ratio waiver warnings.
- Full suite: `python3 -B -m unittest discover -s .github/skills/workflow/scripts/tests` exits 0; 42 tests pass.
- `python3 -B .github/skills/workflow/scripts/check-run.py --all` exits 0; every run has zero errors. The existing slop-guards 127-line warning remains.
- `git diff --check` exits 0. No repo lint or typecheck command exists. Existing assertions are unchanged.
- Commit: ee191dc; one test line added, no production changes. No deviations or screen changes.
- Next: cross-vendor review cycle 2 for C1-1. C1-2 and C1-3 retain their recorded deferred dispositions.
