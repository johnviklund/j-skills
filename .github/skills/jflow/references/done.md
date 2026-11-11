# jflow done

Runs in the builder session after the last check.

1. Confirm no code changed since the newest check receipt's sha, and every row is PROVED or under
   `## Accepted` with no defect open. What the human accepts now gets its `## Accepted` line first.
2. Show the human any **Human checks**, Maybes, `control` verb candidates from `drive.py` per step
   6, and everything left open in `notes.md` or this session: a cost, a risk left in place, a doc
   left out of date. Show the exact `PRODUCT.md` or `DESIGN.md` edit this change calls for, such as
   a reached outcome or a new design decision, or say neither needs one; make it only after their
   yes. Wait for their answer. With none, go on. A `Yes: done` line in `notes.md` answers the Human
   checks and Maybes, so do not wait again for them.
3. Run the repo's own verification commands from `AGENTS.md`.
4. Set `Status: done` in `spec.md`, then record the step as `done`. The script prints the run's
   `jflow:` line; copy it unchanged. When the repo keeps a `WORKLOG.md`, add this entry at its top:

   ```markdown
   ## <date> · <slug> · <what shipped, one line> · <builder model>
   - <what changed and why, one line>
   - Commits: <shas>
   - <the jflow: line the script printed>
   ```

   With no `WORKLOG.md`, add the `jflow:` line to `notes.md`, where `retro` and `memory.compact`
   read it.
5. Keep the repo's lists true, for each of `TODO.md` and `ROADMAP.md` that exists. Search it for the
   slug and for what shipped, and read only the matches and their headings.
   - An item or step this change finished moves to `TODO_ARCHIVE.md` or `ROADMAP_ARCHIVE.md`, word
     for word, plus `— done <date> · <slug>`. The archive sits next to its list at the repo root,
     never in `.jflow/`. Create it with a one-line header if it is missing.
   - A step it finished only part of stays, reworded to what remains.
   - An open item the human kept at step 2 becomes one line in `TODO.md`.

   Ask the human about a match you are unsure of. Done when neither file lists this change as open
   work.
6. Delete `.jflow/<slug>/drive.py` with `git rm` in the done commit: nobody maintains one-off proof
   code. First judge what in it is reusable: only a part a later run would use to drive the same
   user path, never a comparison against `Base` or an attack. Move no code. For each verb the human
   kept at step 2, add one `TODO.md` line naming the verb, the commit that holds the script, and
   `verify.maintain`, which adds the verb to the repo's `control` CLI. To rerun a receipt's quoted
   `drive.py` command later, take the driver from the receipt's own commit, not its header sha,
   which can predate the driver:
   `git show $(git log -1 --format=%H -- <receipt>):.jflow/<slug>/drive.py > <temp folder>/drive.py`.
7. When the human corrected you during this run, invoke `memory.remember` for that correction.
   Nothing else becomes a lesson.
8. Commit. Push the current branch; when the repo has no pre-push secret scan, first run
   `gitleaks git --log-opts="<Base>..HEAD" --redact -v --no-banner` and stop on any finding. `Base`
   stands in for an upstream, which a first push lacks.

Done when the push succeeded. Close with one line: what shipped, whether row 1, the item's
`Solved when`, passed, the proof count, and, on any branch but the default, that the change is not
on the default branch yet.
