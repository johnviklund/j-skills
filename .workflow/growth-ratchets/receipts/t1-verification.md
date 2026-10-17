Command: workflow execute growth-ratchets
Created: 2026-10-18
Base:    1a65a10
Inputs:  .workflow/growth-ratchets/plan.md @ d62b5d0
Status:  complete

## T1 proof
- Writer: GPT-6.1 Sol, high effort, recorded by the harness and live model catalog.
- Approval: human chose 1a for the baseline checks. No root AGENTS.md or MEMORY.md exists.
- Reuse: Doc.section and Doc.slop_gated already exist in check-run.py; check() already creates fixture repos. No waiver parser existed. The new parser serves ratio and budget checks.
- Red: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests -k growth`, exit 1, four methods and 14 parameter cases, ten expected failures before implementation.
- Green: the same Verify, exit 0, four methods and 14 parameter cases pass. Tests cover both rewrite shapes, exact ratio and floor boundaries, keyed and empty waivers, budget notes, and old-plan compatibility.
- Full suite: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests`, exit 0, 42 tests pass. Baseline was 38 passing tests.
- Mutation: replace `tests += int(added) - (int(deleted) if growth else 0)` with `tests += int(added)`. Verify exits 1 with four failures. Restore the line; Verify exits 0.
- `python3 .github/skills/workflow/scripts/check-run.py growth-ratchets`, exit 0, zero errors and warnings.
- `git diff --check`, exit 0. No lint or typecheck command exists in repo configuration.
- Commit: 1a65a10. Code +31/-7; tests +47/-1. Existing test assertions stay unchanged.
- No screen changes. Try it through the Verify command above.
- No deviations. The existing two WORKLOG errors and slop-guards size warning remain for T2 and history respectively.
- T2 requires medium effort; stop here under the execute ticket-loop handoff rule.
