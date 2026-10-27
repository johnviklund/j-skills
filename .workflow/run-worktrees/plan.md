Command: workflow plan run-worktrees
Created: 2026-10-27 · Opus 5.5
Base:    743eb2e
Inputs:  .workflow/run-worktrees/brainstorm.md @ c3a29f1
Status:  drafting

Docs read: none in scope (j-skills has no PRODUCT.md, DESIGN.md or AGENTS.md)
Size: code 801 · tests 503 · ratio 0.63 · largest touched check-run.py 801, test_check_run.py 503 · over 1,000: none (new: run-worktree.py, test_run_worktree.py, references/worktrees.md)
Decisions: pending

## Execution state
<filled by execute>

## Findings
| # | What is true | What it changes |
|---|---|---|
| F1 | `SKILL.md` is 212 lines, 12.7 KB: already over its ~180-line, ~10 KB hub budget (`MAINTAINING.md`) | worktree rules go in a new `references/worktrees.md`; `SKILL.md` gets a pointer and edits to the state-table and card lines, net ≤ +3 lines |
| F2 | `check-run.py` has `Doc`, `parse_tickets`, `field` (100–276), `git_out` (669), and primary-branch detection inside `checkout_warnings` (682–685) | `run-worktree.py` loads `check-run.py` by importlib and reuses them; the branch lines move into `primary_branch(repo)` — no second copy |
| F3 | `test_check_run.py`'s `check()` builds temp repos, but `tests.md:20` bars a test importing a test | `test_run_worktree.py` gets its own small repo + bare-remote fixture |
| F4 | `checkout_warnings` (674) has no test today | T3 adds the first and keeps both existing warnings asserted |
| F5 | B1's `.gitignore` edit changes a tracked code file in the repo folder: it breaks B1's "repo folder unchanged", trips D7's own uncommitted-code test and wrap's clean-tree gate | Decision 2 |
| F6 | Land merges into `main`, checked out in the repo folder, where another run may have uncommitted work; git refuses a merge that would overwrite a dirty file and allows one that doesn't | land relays git's refusal with the paths, exits 1, `main` unmoved; no stash |
| F7 | Every wrap appends to `WORKLOG.md` (step 8), often `TODO.md` and memory pages; two worktree runs wrapping in turn conflict there nearly every time | Decision 3 |
| F8 | Wrap 9a marks the run `done`; landing after it would send a done, not-live run to review on a code conflict | land becomes wrap step 9; the archive becomes step 10, run in the repo folder, committing only `.workflow/<slug>/` |
| F9 | `git show --remerge-diff <merge>` shows only how a merge's conflicts were resolved (git 2.36+; here 2.56.0) | the review cycle after a B6 merge reads that output plus the full suite |
| F10 | P1 probe: `grep -r` and `find` see `.worktrees/`; `wrap.md:172` and `phase-4-review.md:135` grep the repo with `grep -rn` | both gain `--exclude-dir=.worktrees` |
| F11 | j-skills has no verify skill; the surface is skill text an agent follows | no `verify.create` prefactor: a scratch-repo dry run (T5) proves the Outcome, as `checkup-next-actions` did |
| F12 | D7 counts a run already in its own worktree as executing, so a third run gets a worktree even when the repo folder is free | Decision 1 |
| F13 | `Doc.status()` splits on whitespace, so `Status:  complete` (two spaces, as this brief has) parses; `SKILL.md:54`'s live-run grep does not (`TODO.md` P2) | `run-worktree.py` uses `Doc.status()`; the grep fix is in TODO impacts |
| F14 | B8 as checkup prose needs a checkup session to observe it | `run-worktree.py doctor` prints both findings and checkup §4 runs it, so B8 is unit-tested |
| F15 | gitleaks is installed; `SKILL.md`'s scan with no upstream already covers `origin/<primary>..HEAD`, so `run/B`'s first push is scanned | no scan change; land pushes `main` only after wrap's scan |
| F16 | `.claude-plugin/plugin.json` holds the only `2.3.0` | wrap bumps it to 2.4.0 (D13); no ticket |
