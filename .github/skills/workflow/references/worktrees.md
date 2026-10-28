# Run worktrees

Read before opening run artifacts in any phase, including `status` and `next`.
A worktree is a separate checkout sharing the repo's git history. The human starts in the repo
folder and types the same workflow commands; the agent resolves the checkout from the slug.
Use an absolute `<skill>` path for the workflow skill before changing directories.

## Find the run

1. Find the primary checkout: the first `worktree` path in `git worktree list --porcelain`.
   Call it `<repo>`. All paths the script prints are relative to it.
2. Run `python3 <skill>/scripts/run-worktree.py where <slug> --repo <repo>` before reading the
   run. It prints `.` or `.worktrees/<slug>`. Work from that directory for artifact reads,
   git commands, checks, edits and commits. A nonzero exit stops the phase; report the error.
3. The lookup fetches `origin/run/*`, rebuilds a missing checkout from `origin/run/<slug>`, and
   fast-forwards a checkout behind that branch. A failed fetch warns and uses local refs;
   a second clone may then read a stale copy. Dirty or diverged checkouts that prevent updates
   need resolving before the phase continues. Local commits ahead of the remote stay local.

For `status` or an omitted slug, collect slugs from the primary checkout's `.workflow/`, local
`.worktrees/` directories and local or remote `run/*` refs. Refresh remote refs first with
`git fetch --quiet --prune origin '+refs/heads/run/*:refs/remotes/origin/run/*'` when origin exists.
Resolve each candidate with step 2, then read only its own `.workflow/<slug>/` artifacts.
Deduplicate by slug; use the resolved copy instead of the primary checkout's older copy.
Apply the hub's state table there, so a completed worktree plan reports `review`.
An omitted slug still asks when several runs are live; `status` also lists parked runs.

## Slug and status

**Slug:** the command names one, or exactly one run is live — otherwise list the live runs,
lettered, and ask. Live runs in each resolved checkout: `grep -l 'Status: *\(drafting\|complete\)' .workflow/*/brainstorm.md`.
`workflow status` prints one line per non-done run — `slug · phase · blocker or none · next command`
(an `awaiting-human` ticket is the blocker, with its action). A command that doesn't fit the run's
state gets named and asked about.

## Start execution

Before the first ticket, run `python3 <skill>/scripts/run-worktree.py open <slug> --repo <repo>`.
Use its returned directory and repeat execute's readiness, freshness and baseline checks there.
It reuses an existing run checkout. A run with a started ticket stays in its original checkout.
Otherwise it creates `.worktrees/<slug>` on `run/<slug>` from the primary branch
when the primary checkout has uncommitted files or another live run
there has a started ticket. A run already isolated in its own worktree does not occupy the
primary checkout. A free primary checkout keeps the lone run there.

The script adds `.worktrees/` once to the clone's `.git/info/exclude`, preserving tracked files.
Setup comes only from the committed primary branch's `AGENTS.md` `## Worktree setup` block.
Only `sh`, `bash`, `shell` and untagged fences supply commands; text outside a shell fence never runs.
A block without one of these fences stops `open` before a checkout exists.
Commands are printed and run in the new checkout. A missing block produces a note;
a failed setup stops execution. Resume only after checking and completing setup there.

## Commit and hand off

Commit code and run artifacts together on the resolved branch. A run checkout stays on
`run/<slug>` through review and wrap. Before every closing card, run the hub's gitleaks scan,
then push that branch with `git push -u origin run/<slug>`; a primary-checkout run pushes the
primary branch as before. The first run-branch scan uses `origin/<primary>..HEAD` when no
upstream exists. Scan or push failure stops the handoff. The card command stays
`workflow <phase> <slug>`; the next phase resolves its checkout again.

## Land at wrap

Wrap step 9 runs `python3 <skill>/scripts/run-worktree.py land <slug> --repo <repo>` from the
primary checkout, after committing the run checkout and scanning its outgoing commits.
The script expects the primary checkout on its primary branch and the run checkout clean.
It checks conflicts before changing the primary checkout and never stashes another run's files.

- Exit 0: fast-forward when possible, otherwise merge without rebasing. Ticket shas remain
  ancestors of the primary branch. The primary branch is pushed, the remote and local
  `run/<slug>` branches are deleted, and the run worktree is removed. Continue wrap step 10
  in the primary checkout, archiving and committing only `.workflow/<slug>/`.
- Exit 1: report the named error or dirty paths. The command can fail after a successful local
  merge or push; inspect refs and worktrees before resuming. Preserve other runs' edits.
  If the primary branch moved on origin, merge it into the primary checkout with `git merge --no-edit origin/<primary>`, then land again. A pull can rebase another run's unpushed commits.
  For unpushed primary commits, run `gitleaks git --log-opts="origin/<primary>..<primary>" --redact -v --no-banner`.
  After a clean scan, push the primary branch, then land again.
- Exit 3: the primary branch stays unmoved; its changes are merged into the run checkout with
  conflicts left there. Resolve the code conflicts, commit the merge, run the full suite and
  route to `workflow review <slug>` for the merge-resolution diff. Keep the run live until that
  review passes, then resume wrap and land again.
- Exit 4: only Markdown or text files conflict. Resolve in the run checkout keeping both sides,
  commit and scan, then land again. This needs no extra code review.

A primary-checkout run skips landing and proceeds to the same archive step.

## Workspace health

`python3 <skill>/scripts/run-worktree.py doctor --repo <repo>` prints a line for a missing
committed `## Worktree setup` block when worktree directories exist, and one per directory
without a live matching run. Checkup reports those lines; cleanup remains a human decision.
