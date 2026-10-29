Command: workflow execute next-step · C1-T3
Created: 2026-10-29 · GPT-6.1 Sol
Base: 0762b64
Inputs: .workflow/next-step/patch_plan.md @ 1aa0b47
Status: complete

Reused the CLI fixture helpers and extended existing card and handoff cases. No new helper or next-step.py change.

- Verify: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests -p test_next_step.py`. Runs 22 tests, `OK`, exit 0.
- Full: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests && python3 -m unittest discover -s .github/skills/checkup/scripts/tests`. Workflow runs 105 tests, `OK`; checkup runs 8 tests, `OK`; exit 0.
- Each mutation runs alone in a throwaway copy. Before the added cases all eight exit 0. Afterwards all eight exit 1 with assertion failures:
  - wrap card always says reset yes;
  - blocker selects the first unfinished ticket;
  - no-ready error is removed;
  - handoff glob drops the ticket id;
  - ticket Why text becomes a constant;
  - patch cycle comes from the finding id;
  - slug validation is removed;
  - non-git-repository error is removed.
- Both awaiting-human and ready Why values are asserted. Handoff checks retain the selected ticket's path and exclude the other ticket's path.
- Tests add 31 lines against budget 45. Assertion lines increase from 53 to 65; no existing assertion changes. No deviations.
