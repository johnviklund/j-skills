### 4. Workspace cleanliness

```sh
for d in .jflow/*/; do printf '%s ' "$d"; grep -m1 '^Status:' "$d/spec.md" 2>/dev/null; done   # runs + status
git check-ignore -q .jflow && echo 'IGNORED'                              # runs must be tracked
git status --porcelain 2>/dev/null                                        # uncommitted work
git log @{u}.. --oneline 2>/dev/null                                      # unpushed commits
git ls-files | grep -Ei '(^|/)\.DS_Store$|(^|/)\.env$|/node_modules/|/\.venv|\.pyc$' 2>/dev/null
```

- **Push hook.** Run `python3 <jflow skill folder>/scripts/hooks.py install --check`. Anything but
  `installed` is a warning: a missing or old stub, or a refused foreign hook or `core.hooksPath`.
  Offer installation as an opt-in fix, one at a time.
- **Runs.** List every `.jflow/<slug>/` with its status from `spec.md`, and what
  `python3 <jflow skill folder>/scripts/jflow.py next <slug> --json` says is next. A run that is
  not `done` with no commit touching it in ~14 days is ⚠️ "stalled -- finish it or drop it".
  `done` runs are ✅, counted not listed. A `done` run still holding `drive.py` is ⚠️ (done
  did not clean up). A run folder missing `spec.md` is ⚠️. A gitignored `.jflow/` is 🔴 -- runs
  are the repo's history.
- **One home per idea.** A `TODO.md` item naming the same thing as an open run is ⚠️ -- archive
  the TODO line with a pointer to the run.
- **Context weight.** `TODO.md` over ~15 KB or `ROADMAP.md` over ~12 KB, a run's `notes.md` over
  ~150 lines, or `SKILL.md` over ~10 KB (`wc -c`) is ⚠️ -- grounding cost repeats every step;
  propose what to archive or move, never delete.
- **Tracked junk / secrets.** A committed `.DS_Store`, `.env`, virtualenv, build output, or `.pyc`
  is 🔴 (secrets) or ⚠️ (junk). A tracked `.env` is always 🔴 -- flag loudly.
- **Uncommitted or unpushed work.** If the repo treats push as its archive/safety net, unpushed
  commits or a dirty tree are ⚠️ worth surfacing.
