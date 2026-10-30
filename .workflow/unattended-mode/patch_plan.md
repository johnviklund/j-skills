Command: workflow review unattended-mode · patch cycle 1
Created: 2026-10-30 · Claude Opus 5.5
Base:    f719a10
Inputs:  .workflow/unattended-mode/review.md @ f719a10
Status:  complete

Both tickets are small and run in one session at the same model and effort. C1-T2 is test-only:
one commit, no red commit, and next-step.py stays unchanged.

## Tickets

### C1-T1 — An unattended UI stop leaves the ticket's code uncommitted
Delivers: B2 · Blocked by: none · Lane: mechanical
Fixes: C1-1 (P2)
Budget: code +0 · tests +0
Seam: `grep` of `.github/skills/workflow/references/unattended.md`
Change: replace the UI bullet at `unattended.md:36` with exactly these lines, so the section keeps five bullets:
```markdown
- UI approval before the ticket commit stays with the human; see `phase-3-execute.md`. Commit and
  push only run artifacts and `screens/`; the ticket's code stays uncommitted, and on resume it is
  that ticket's pending work, not the human's edits.
```
Accept:
- [ ] `grep -c "the ticket's code stays uncommitted" unattended.md` returns 1 (B2)
- [ ] `grep -c "not the human's edits" unattended.md` returns 1 (B2)
- [ ] the `## Always stop` section still has exactly 5 lines starting `- ` (B2)
Verify: `U=.github/skills/workflow/references/unattended.md; grep -c "the ticket's code stays uncommitted" $U; grep -c "not the human's edits" $U; awk '/^## Always stop/{f=1;next} /^## /{f=0} f&&/^- /' $U | wc -l` (pre: 0 · 0 · 5)
Skills: .github/skills/agent-docs/SKILL.md
Status: todo

### C1-T2 — The card's Reads names decisions.md under test
Delivers: B4 · Blocked by: none · Lane: logic
Fixes: C1-2 (P2)
Budget: code +0 · tests +1
Seam: `test_next_step.py` `test_unattended_decision_states` (`:84-105`) through `next-step.py --json`
Change: in the waiting branch, after `test_next_step.py:102`, add `self.assertIn(".workflow/x/decisions.md", result["reads"])`. The assumed and answered branches already compare the whole result to the no-file baseline, so they prove the entry is absent there.
Accept:
- [ ] `test_next_step.py` passes with the new assertion (B4)
- [ ] `step["reads"].append(...)` deleted from `next-step.py:177` in a throwaway copy → `test_unattended_decision_states` fails; the commit changes no line of next-step.py (B4)
Verify: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests && python3 -m unittest discover -s .github/skills/checkup/scripts/tests` (pre: 111 OK · 8 OK; deleting `:177` also stays green)
Skills: none
Status: todo
