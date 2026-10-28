Command: workflow review run-worktrees · patch cycle 4
Created: 2026-10-28 · claude-opus-5-5
Base:    dda6fd2
Inputs:  .workflow/run-worktrees/review.md @ dda6fd2
Status:  complete

## Execution state
Current: C4-T1 todo · writer: — · baseline failures: none

## Tickets

### C4-T1 — Tests fail when any setup-parser condition breaks
Delivers: B1 · Blocked by: none · Lane: logic
Fixes: C4-1 (P1)
Budget: code +0 · tests +3 · why: three rows in the existing `cases` tuple
Seam: `test_Open_setup_reads_shell_fences_line_by_line` (`test_run_worktree.py:174`), which runs `run-worktree.py open` as a subprocess on temp repos
Change: add three rows to `cases`, each expecting exit 0 and `.worktrees/B/ready`: ```` ```sh ```` `touch ready` ```` ``` ```` then `Then run the app.`; an untagged fence holding `touch ready`; `1. Install:` then a three-space-indented `sh` fence holding `touch ready`. No code change, so no red commit: the proof is the three mutations below, each run on a temporary copy and never committed. Class sites, searched at planning time: the parser's conditions are `run-worktree.py:33-40`; M21–M24 and M26 already fail the suite (`review.md` Coverage).
Accept:
- [ ] `elif fenced and shell` → `elif shell` (M25) fails the suite on the `Then run the app.` row (C4-1, B1)
- [ ] `line.lstrip().startswith` → `line.startswith` (M27) fails the suite on the indented row (C4-1, B1)
- [ ] `shell = not tag or` → `shell = False or` (M28) fails the suite on the untagged row (C4-1, B1)
- [ ] the commit changes only `test_run_worktree.py`, adds no test method, and the full suite passes (B1)
Verify: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests` (pre: 72 pass; M25, M27, M28 each leave it green)
Skills: none
Status: todo
