Command: workflow review run-worktrees · patch cycle 2
Created: 2026-10-27 · claude-opus-5-5
Base:    bc15275
Inputs:  .workflow/run-worktrees/review.md @ bc15275
Status:  complete

## Execution state
Current: C2-T2 next · writer: GPT-6.1 Sol · baseline failures: none
C2-T1 @ b0b55af

## Tickets

### C2-T1 — Setup stops at the next `# ` heading
Delivers: B1 · Blocked by: none · Lane: logic
Fixes: C2-1 (P1)
Budget: code +2 · tests +10 · why: one temp repo with a two-section `AGENTS.md`
Seam: `run-worktree.py open` as a subprocess on temp repos; `Doc.__init__` (`check-run.py:103-117`)
Change: `Doc` ends the current `## ` section at a `# ` heading outside a fence, as markdown does. Red commit first: the new Open test, run and seen failing, committed alone; the fix commit changes no test file. Class sites, searched at planning time: every `Doc.section` caller in `check-run.py` reads run artifacts, and their `# ` lines outside fences sit before the first `## ` (line 1 of two `learnings.md`, line 7 of three `wrap.md`), so no existing section changes.
Accept:
- [x] `## Worktree setup` with a `sh` fence `touch ready`, then `# Appendix` with a `sh` fence `touch appendix_ran` → `open B` exits 0, `.worktrees/B/ready` exists, `.worktrees/B/appendix_ran` does not, stderr lacks `appendix_ran` (B1)
- [x] The fix commit changes no test file; `test_check_run.py` and the other Open tests pass (B1)
- [x] `check-run.py` prints the same output for every run under `.workflow/` at the red commit and at the fix commit (B1)
Verify: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests && for r in .workflow/*/; do python3 .github/skills/workflow/scripts/check-run.py "$(basename "$r")"; done > /tmp/c2-t1-after.txt 2>&1; diff /tmp/c2-t1-before.txt /tmp/c2-t1-after.txt` (pre: 69 pass; the new test does not exist yet; capture `/tmp/c2-t1-before.txt` with the same loop at the red commit)
Skills: none
Status: done @ b0b55af
Writer: GPT-6.1 Sol

### C2-T2 — A setup block with no shell fence stops `open`
Delivers: B1 · Blocked by: C2-T1 · Lane: logic
Fixes: C2-2 (P2, the human chose fix now)
Budget: code +4 · tests +15 · why: two fence shapes, each a temp repo
Seam: `run-worktree.py open` as a subprocess on temp repos; `add_worktree` (`run-worktree.py:28-47`); `references/worktrees.md` §Start execution
Change: read the setup commands before `git worktree add`. The fence regex (`:44`) also accepts spaces after the tag. When the block has a fence but none is `sh`, `bash`, `shell` or untagged, raise naming `## Worktree setup` and those tags, so `open` exits 1 and creates nothing. Red commit first; the fix commit changes no test file.
Accept:
- [ ] Setup fence tagged `zsh` → `open B` exits 1, stderr names `## Worktree setup` and `sh`, and neither `.worktrees/B` nor a `run/B` branch exists (B1)
- [ ] Setup fence tagged `sh` followed by a space → `open B` exits 0 and `.worktrees/B/ready` exists (B1)
- [ ] `worktrees.md` §Start execution: setup runs only `sh`, `bash`, `shell` and untagged fences; any other tag stops `open` before a checkout exists (B1)
Verify: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests -p 'test_run_worktree.py' -k Open && grep -c 'untagged' .github/skills/workflow/references/worktrees.md` (pre: 8 Open tests pass; grep 0)
Skills: .github/skills/agent-docs/SKILL.md
Status: todo

### C2-T3 — One started-ticket test in `open_run`
Delivers: B1, B2 · Blocked by: none · Lane: logic
Fixes: C2-3 (P2)
Budget: code +0 · tests +0
Seam: `open_run` (`run-worktree.py:71-90`); the existing Open tests, which pin both callers (cycle 2 mutations M3, M4, M9)
Change: one helper, `started(run_dir)`: true when the run's `plan.md` or `patch_plan.md` has a ticket whose Status is not `todo`. The own-run check and the busy loop both call it. A refactor: no test file changes.
Accept:
- [ ] `run-worktree.py` holds `not in (None, "todo")` once (B1, B2)
- [ ] The fix commit's net lines in `run-worktree.py` are at most 0, it changes no test file, and the full suite passes (B1, B2)
Verify: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests && grep -c 'not in (None, "todo")' .github/skills/workflow/scripts/run-worktree.py` (pre: 69 pass; grep 2)
Skills: none
Status: todo

## Deviations
- none
