# drive-py-at-done
Status: ready
Base: c45e466975b1056b34122816d4e8b7da55e8afa2
Issue: roadmap item 0.4 in https://github.com/johnviklund/hq/blob/main/docs/jflow-standalone-and-hq-roadmap.md

## Problem
Each run's `drive.py` is the checker's throwaway script, and it stays committed in `.jflow/<slug>/`
after the run ends. Nobody maintains it afterwards. Measured 2026-11-08 on the 9 that exist across
personal and work repos: 0.9 to 51 KB each. They hold almost nothing but one-off proof code: running
the `Base` version, patching, comparing and attacking. None adds a verb that the repo's `verify-*`
`control` CLI lacks. `done.md` says nothing about the file, so it stays forever.

## Goals
1. At `done`, the builder deletes `.jflow/<slug>/drive.py` with `git rm`, in the done commit.
2. When part of the script would be a useful `control` verb, `done` adds one `TODO.md` line instead
   of moving code. The line names the verb, the commit that holds the script, and `verify.maintain`
   as the command that adds it.
3. The builder judges what is reusable. The test is "a later run would drive the same user path".
   A comparison against `Base` or an attack never qualifies. The candidate appears at done step 2
   with the other open items, for the human to answer.
4. A receipt's quoted `drive.py` command reruns at that receipt's commit, through
   `git show <sha>:.jflow/<slug>/drive.py`.
5. The run-folder tree in `SKILL.md` says `drive.py` is deleted at `done`.

## Non-goals
- No deleting `drive.py` in past runs, in this repo or any other.
- No change to `jflow.py`.
- No change to how check writes or reuses `drive.py` during a run.
- No rewrite of existing receipts.
- No code moved into a `control` CLI at `done`.

## Constraints
- Must not break: check's "reuse and extend it" rule. Deleting files under `.jflow/` must still
  count as no code change.
- Ask first: nothing.
- Gate: none.

## Proof
| # | Claim | Surface | Check | Pass signal | Kind | Base |
|---|---|---|---|---|---|---|
| 1 | Goal 1 | `references/done.md` | `grep -n "drive.py" references/done.md`, then read the step | A done step deletes `.jflow/<slug>/drive.py` with `git rm` in the done commit | new | red |
| 2 | Goal 2 | `references/done.md` | `grep -n "verify.maintain" references/done.md` | One `TODO.md` line that names the verb, the commit and `verify.maintain`; no code moved at `done` | new | red |
| 3 | Goal 3 | `references/done.md` | Read step 2 and the `drive.py` step | The builder judges reusability by "same user path"; `Base` comparisons and attacks are excluded; the candidate is shown at step 2 | new | red |
| 4 | Goal 4 | `.github/skills/jflow/` | `grep -rn "git show" .github/skills/jflow` | A rule says a receipt's `drive.py` command reruns at its receipt's sha via `git show` | new | red |
| 5 | Goal 5 | `SKILL.md` | `grep -n "drive.py" SKILL.md` | The tree line says it is deleted at `done` | new | red |
| 6 | Check reuse unchanged | `references/check.md` | `grep -n "reuse and extend it" references/check.md` | Still present, unchanged | keep | green |
| 7 | Deletion is not code | `scripts/jflow.py` | In a scratch repo, commit `app.py` and `.jflow/x/drive.py`, then `git rm` the driver and commit; run `jflow.changed(repo, "HEAD~1", "HEAD")` | `False` | keep | green |
| 8 | Text only | git | `git diff --name-only <Base>..HEAD -- . ':(exclude).jflow'` | Only `.md` files under `.github/skills/jflow/` | keep | green |

## Human checks
- On the next run that reaches `done` with a `drive.py`, the file is gone after the done commit, and
  any reusable verb appears as one `TODO.md` line.
