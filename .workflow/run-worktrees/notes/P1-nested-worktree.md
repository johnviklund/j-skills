P1 — Does a run's worktree in an ignored `.worktrees/` stay invisible to the primary checkout and its tools?
Variant: one, `prototypes/P1-nested-worktree/probe.sh <repo>` run on a scratch clone of j-skills; plus a node --test probe.
- `git status --porcelain` in primary: empty. `git grep`, `rg --files`: do not see worktree files.
- `grep -r` and `find`: do see them (they ignore .gitignore). pytest skips dot dirs by default; `node --test` (v26.8.1) ran 1 test, skipped the copy.
- Run branch merged after main moved: the ticket's sha is still an ancestor of main (merge keeps shas).
- check-run.py inside the worktree warns twice ("linked worktree", "on branch run/demo"): it must learn a run's own worktree.
- `git worktree remove` + `git branch -d` after merge: clean, no leftovers.
Result: `.worktrees/<slug>` works; plain grep/find need `--exclude-dir=.worktrees`; check-run's warning needs changing.
