### 4. Workspace cleanliness

Run `python3 <workflow skill folder>/scripts/run-worktree.py doctor --repo <repo>` when that
script exists; `<repo>` is the primary checkout from `git worktree list --porcelain`.
Report each missing setup block or orphan directory as one warning. Resolve each run through
the workflow skill's `references/worktrees.md` before its status and run-shape checks below.

```sh
for d in .workflow/*/; do printf '%s ' "$d"; grep -m1 '^Status:' "$d/brainstorm.md" 2>/dev/null; done   # runs + status
ls .workflow/*.md 2>/dev/null                                             # v1 flat scratch (needs migration)
git check-ignore -q .workflow && echo 'IGNORED'                           # runs must be tracked
git status --porcelain 2>/dev/null                                        # uncommitted work
git log @{u}.. --oneline 2>/dev/null                                      # unpushed commits
git ls-files | grep -Ei '(^|/)\.DS_Store$|(^|/)\.env$|/node_modules/|/\.venv|\.pyc$' 2>/dev/null
```

- **Run shape.** In a repo with `.workflow/`, run the workflow skill's checker over every run:
  `python3 <workflow skill folder>/scripts/check-run.py --all`. Each ERROR on a live run is 🔴;
  ERRORs and warnings on done runs are ⚠️, counted per run, not listed.
- **Runs.** List every `.workflow/<slug>/` with its status. A `drafting`/`complete` run with no
  commit touching it in ~14 days is ⚠️ "stalled -- park it or finish it". A `parked` run older
  than ~90 days is ⚠️ "still wanted?". `done` runs are ✅, counted not listed. A run folder
  missing `brainstorm.md`, or a `done` run still holding `patch_plan.md`/an
  `## Execution state` block, is ⚠️ (wrap didn't archive properly). A ticket `awaiting-human`
  for more than ~7 days is ⚠️ "operator step pending — run it or park the run". A `proto/*`
  branch (`git branch --list 'proto/*'`) is ⚠️ "prototype branch left behind -- its evidence is in
  the run folder; delete it".
- **Review deferrals.** `TODO.md`'s `## Review deferrals` lines older than ~90 days are ⚠️ "still
  wanted? fold into a run or archive"; more than ~20 open is ⚠️ "triage before the next brainstorm".
- **v1 leftovers.** Flat `.workflow/*.md` files are ⚠️ "migrate into `.workflow/<slug>/`" (see the
  workflow README); a gitignored `.workflow/` is 🔴 -- runs are the repo's history.
- **One home per idea.** A `TODO.md` item naming the same thing as a parked run is ⚠️ -- archive
  the TODO line with a pointer to the run.
- **Context weight.** `TODO.md` over ~15 KB or `ROADMAP.md` over ~12 KB, a finished run's `wrap.md`
  over ~60 lines or its `review.md` over ~150, `SKILL.md` over ~10 KB or `ROUTING.md` over ~5.5 KB
  (`wc -c`) is ⚠️ -- grounding cost repeats every phase; propose what to archive or move, never delete.
- **Tracked junk / secrets.** A committed `.DS_Store`, `.env`, virtualenv, build output, or `.pyc`
  is 🔴 (secrets) or ⚠️ (junk). A tracked `.env` is always 🔴 -- flag loudly.
- **Uncommitted or unpushed work.** If the repo treats push as its archive/safety net, unpushed
  commits or a dirty tree are ⚠️ worth surfacing.
