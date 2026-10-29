Command: workflow execute next-step · C1-T1
Created: 2026-10-29 · GPT-6.1 Sol
Base: e6a8e5d
Inputs: .workflow/next-step/patch_plan.md @ 1aa0b47
Status: complete

Reused `review_findings`; the existing checker and card duplicated the open-finding test. Both now call `open_finding`.

- Red: 29100c5. The unresolved cycle-1 case fails because the card selects wrap after an empty cycle 2. One test runs; its resolved variant passes.
- Green: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests && python3 -m unittest discover -s .github/skills/checkup/scripts/tests`. Workflow runs 100 tests, `OK`; checkup runs 8 tests, `OK`; exit 0.
- Content: `grep -c Disposition .github/skills/workflow/scripts/next-step.py` prints 0. Its expected no-match exit is 1.
- Mutations in throwaway copies: latest-cycle-only selection, ignoring disposition, and ignoring resolution each fail the CLI tests. Three of three killed.
- The fix commit changes no tests. `test_check_run.py` stays unchanged.
- Deviation: the red commit removes the wrong earlier-cycle wrap subcase named by the review. It adds a parametrized unresolved/resolved test; existing assertion lines stay unchanged.
