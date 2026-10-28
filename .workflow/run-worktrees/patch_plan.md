Command: workflow review run-worktrees · patch cycle 6
Created: 2026-10-28 · claude-opus-5-5
Base:    7740521
Inputs:  .workflow/run-worktrees/review.md @ 7740521
Status:  complete

## Execution state
Current: C6-T1 done; next review · writer: GPT-6.1 Sol · baseline failures: none
C6-T1 @ f61de07
Red: be47a91

## Tickets

### C6-T1 — A refused land names a merge, never a pull
Delivers: B5 · Blocked by: none · Lane: mechanical
Fixes: C6-1 (P2, the human chose to fix it, 1a)
Budget: code +0 · tests +1 · why: one assertion in an existing test; the message line changes in place
Seam: `test_Land_refuses_a_primary_branch_advanced_on_origin` (`test_run_worktree.py:438`), which already pushes `main` from a second clone and runs `land B`
Change: first a red commit, the test file alone: add `self.assertIn("git merge --no-edit origin/main", result.stderr)` after the test's `origin/main` assertion, run it and see it fail. Then the fix, which leaves test files untouched:
- `run-worktree.py:114`: `f"origin/{primary} moved; merge it into the primary checkout with git merge --no-edit origin/{primary}, then land again:\n{behind}"`
- `worktrees.md:67`: `If the primary branch moved on origin, merge it into the primary checkout with \`git merge --no-edit origin/<primary>\`, then land again. A pull can rebase another run's unpushed commits.`
- `SKILL-IMPACT.md`, the 2026-10-28 row from C5-2: after "when origin has advanced", add "and names `git merge --no-edit`, never a pull, so another run's unpushed commits keep their shas"

The merge needs no fetch: `land` fetched `origin <primary>` at `run-worktree.py:111` just before it refused.
Accept:
- [x] The red commit fails at its parent on the new assertion alone; every other assertion of that test still passes (C6-1)
- [x] After the fix, `test_Land_refuses_a_primary_branch_advanced_on_origin` passes and the full suite passes, 81 tests (C6-1, B5)
- [x] `grep -c 'pull' .github/skills/workflow/references/worktrees.md` → 1, the rebase warning; `grep -c 'pull' .github/skills/workflow/scripts/run-worktree.py` → 0; `grep -c 'moved on origin' .github/skills/workflow/references/worktrees.md` → 1 (C6-1)
- [x] The fix commit leaves test files untouched; `SKILL-IMPACT.md` has `git merge --no-edit` on exactly 1 line (C6-1)
Verify: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests -k test_Land_refuses_a_primary_branch_advanced_on_origin` (pre: passes; after the red commit: fails on the new assertion)
Skills: none
Status: done @ f61de07
Writer: GPT-6.1 Sol
