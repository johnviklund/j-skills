# jflow done

Runs in the builder session after the last check.

1. Confirm no code changed since the newest check receipt's sha, and every row is PROVED or under
   `## Accepted` with no defect open. What the human accepts now gets its `## Accepted` line first,
   per the hub, so an unproved row stays visible in the record.
2. Show the human any **Human checks**, Maybes, and everything left open in `notes.md` or this
   session: a cost, a risk left in place, a doc left out of date. Show also any `control` verb
   candidate from `drive.py`, per step 6. Wait for their answer. With none, go on.
3. Run the repo's own verification commands from `AGENTS.md`.
4. Set `Status: done` in `spec.md`, then record the step as `done`. The script prints the run's
   `jflow:` line; copy it unchanged. When the repo keeps a `WORKLOG.md`, add this entry at its top:

   ```markdown
   ## <date> · <slug> · <what shipped, one line> · <builder model>
   - <what changed and why, one line>
   - Commits: <shas>
   - <the jflow: line the script printed>
   ```

   With no `WORKLOG.md`, add the `jflow:` line to `notes.md`, because `retro` and `memory.compact`
   read a run's numbers from one or the other.
5. Keep the repo's lists true, for each of `TODO.md` and `ROADMAP.md` that exists. Search it for the
   slug and for what shipped, and read only the matches and their headings.
   - An item or step this change finished moves to `TODO_ARCHIVE.md` or `ROADMAP_ARCHIVE.md`, word
     for word, plus `— done <date> · <slug>`. The archive sits next to its list at the repo root,
     never in `.jflow/`. Create it with a one-line header if it is missing.
   - A step it finished only part of stays, reworded to what remains.
   - An open item the human kept at step 2 becomes one line in `TODO.md`.

   Ask the human about a match you are unsure of. Done when neither file lists this change as open
   work.
6. Delete `.jflow/<slug>/drive.py` with `git rm`, so the done commit removes it. It is one-off
   proof code that nobody maintains after the run. Before that, judge what in it is reusable. A part
   qualifies only when a later run would drive the same user path; a comparison against `Base` or
   an attack never does. Move no code. For each verb the human kept at step 2, add one `TODO.md`
   line that names the verb, the commit that holds the script, and `verify.maintain` as the command
   that adds it to the repo's `control` CLI. After the deletion, a receipt's quoted `drive.py`
   command reruns at that receipt's sha:
   `git show <sha>:.jflow/<slug>/drive.py > <temp folder>/drive.py`, then the quoted command on
   that copy.
7. When the human corrected you during this run, invoke `memory.remember` for that correction.
   Nothing else becomes a lesson.
8. Commit. Push the current branch; when the repo has no pre-push secret scan, first run
   `gitleaks git --log-opts="<Base>..HEAD" --redact -v --no-banner` and stop on any finding. It uses
   `Base` because this is usually the branch's first push, so it has no upstream.

Done when the push succeeded. Close with one line: what shipped, the proof count, and, on any branch
but the default, that the change is not on the default branch yet.
