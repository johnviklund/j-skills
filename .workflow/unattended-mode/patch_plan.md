Command: workflow review unattended-mode · patch cycle 2
Created: 2026-10-30 · Claude Opus 5.5
Base:    a4d6991
Inputs:  .workflow/unattended-mode/review.md @ a4d6991
Status:  complete

Cycle 3 approved by human (1a). C2-T1 fixes a behaviour: a red test committed alone, then the
fix with every test file untouched.

## Execution state
Current: C2-T1 next · writer: — · baseline: workflow 111, checkup 8 passed

## Tickets

### C2-T1 — A run stopped at its first ticket resumes where its pending code is
Delivers: B2 · Blocked by: none · Lane: logic
Fixes: C1-1 (P2)
Budget: code +3 · tests +14
Seam: `run-worktree.py open <slug>` stdout and `git worktree list`, through `test_run_worktree.py` OpenTests
Change: `started()` (`run-worktree.py:98-101`) also returns true when `run_dir / "decisions.md"` exists and holds a row whose Phase is `execute`; parse it with `checks.decisions(checks.Doc(...))`, as `next-step.py:174` does. Every unattended stop writes its row before it ends (`unattended.md:13-14`), so an execute row means execution began in this checkout. Sites, from `grep -n 'porcelain\|started(' .github/skills/*/scripts/*.py`: `run-worktree.py:108`, the own run (the bug); `:116`, another live run, already busy from its dirty code at `:110` and covered by the same change; `:137`, land, after every ticket is done (outside the class); `check-run.py:779`, the brief's own changes (outside the class). Then `worktrees.md:44` reads exactly: `It reuses an existing run checkout. A run with a started ticket or an execute decision stays in its original checkout.`
Accept:
- [ ] run B, every plan.md ticket `todo`, `src.py` uncommitted, `decisions.md` holding `| D1 | execute | Approve T1? | commit | answered | commit |` → `open` prints `.`, `git worktree list` is unchanged and `src.py` keeps its text (B2)
- [ ] the same run with that row's Phase `plan` → `open` prints `.worktrees/B` (B2)
- [ ] the red commit holds only the new test, run and seen failing on the first case; the fix commit changes no test file (B2)
- [ ] `grep -c 'started ticket or an execute decision' .github/skills/workflow/references/worktrees.md` returns 1 (B2)
- [ ] existing `test_run_worktree.py` cases pass with no assertion edited (B2)
Verify: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests && python3 -m unittest discover -s .github/skills/checkup/scripts/tests` (pre: 111 OK · 8 OK; the new test fails its first case before the fix; the grep returns 0)
Skills: .github/skills/agent-docs/SKILL.md
Status: todo
