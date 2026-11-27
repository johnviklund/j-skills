# jflow done

Runs in the builder session after the last check.

1. Confirm no code changed since the newest check receipt's sha, and every row is PROVED or under
   `## Accepted` with no defect open. What the human accepts now gets its `## Accepted` line first.
   With every check used, an `## Accepted` line committed after the newest receipt also accepts the
   code changed since it: list those files for the human in step 2.
2. Show the human any **Human checks**, Maybes, `control` verb candidates from `drive.py` per step
   6, and everything left open in `notes.md` or this session: a cost, a risk left in place, a doc
   left out of date. Show the exact `PRODUCT.md` or `DESIGN.md` edit this change calls for, such as
   a reached outcome or a new design decision, or say neither needs one; make it only after their
   yes. Wait for their answer. With none, go on. A `Yes: done` line in `notes.md` answers the Human
   checks and Maybes, so do not wait again for them.

   **Unattended,** with no human in the session, as under `conductor`: write each `PRODUCT.md`,
   `DESIGN.md` or `TODO.md` edit and each `drive.py` verb you would ask about as one `- ` line
   under `## Proposed edits` in `notes.md`. Commit only `notes.md` and end with the closing card:
   steps 3 to 8 wait, since `next` waits for `Yes: edits`. A changed proposal goes in a new
   `## Proposed edits`; the newest one counts. With a `Yes: edits` line after it, make the proposed edits as written, with any change the human gave, and do not ask
   again. In a session with a human, ask in chat as above.
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

   Add one `Impact check` line to `notes.md`: did the change move what the card's `Moves` or
   `Impact` named? Write one of:
   - `Impact check: observed · <the number>`
   - `Impact check: not yet measurable · <how and when to check>`
   - `Impact check: missed · <what happened>`
5. Keep the repo's lists true, for each of `TODO.md` and `ROADMAP.md` that exists. Search it for the
   slug and for what shipped, and read only the matches and their headings.
   - A `ROADMAP.md` with `## Next up` follows the `roadmap` skill's done-item rules and `check`.
   - Any other finished item moves word for word to `TODO_ARCHIVE.md` or `ROADMAP_ARCHIVE.md`
     beside its list, plus `— done <date> · <slug>`; create it if missing.
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
on the default branch yet. Then, when `ROADMAP.md` has a `## Next up` item, run `jflow.py next
<first item's slug>` and print its card as the closing card, under `Next up in ROADMAP.md: <slug>`.

## Issue and pull request mode

The pull request is the review gate, so done waits for no one: `next` sends a run here without
stopping for `[edge]`-only defects, Human checks, Maybes or proposed edits.

- Step 1: unfixed `[edge]` defects may stay open. Each one becomes a caveat in the pull request
  description; it needs no `## Accepted` line.
- Step 2: ask nothing and wait for no one. Make each `PRODUCT.md`, `DESIGN.md` or `TODO.md` edit
  directly in the pull request diff and commit it, so the reviewer sees it there. Human checks and
  Maybes go under **What you need to do**.
- Step 4: leave the spec comment as it is; `record done` marks the run done. Post the `Impact
  check` line with `jflow.py note`, and repeat it in the pull request description.
- Step 6: delete `drive.py` from `.git/jflow/<issue>/`.
- Step 8: push the branch. Invoke the `plain` skill, then write the pull request description with
  these three headings and update it with `gh pr edit <number> --body-file F`:
  - **What changed**: two or three sentences.
  - **What was proved**: the proof count, any row accepted unproved, and the `Impact check` line.
  - **What you need to do**: each Human check, Maybe and `[edge]` caveat as a step only a person
    can do, or `Nothing for you to test.` when there is none.

  End it with `Closes #<issue>`, then run `gh pr ready <number>`. Never merge. If the repo opts
  into `confirm_public_writes`, ask before public GitHub writes and pass `--confirmed`.

Done when the pull request is ready for review.
