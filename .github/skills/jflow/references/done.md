# jflow done

Runs in the builder session after the last proof.

1. Confirm no code changed since the newest prove receipt's sha and every row is PROVED, or the
   human accepted the rest; when review was required, the same holds for the newest review, with no
   defects left or the human accepting them.
2. Show the human any **Human checks**, Maybes and costs you flagged in `notes.md`, and wait for
   their answer. With none, go on.
3. Run the repo's own verification commands from `AGENTS.md`.
4. Set `Status: done` in `spec.md`. When the repo keeps a `WORKLOG.md`, add this entry at its top:

   ```markdown
   ## <date> · <slug> · <what shipped, one line> · <builder model>
   - <what changed and why, one line>
   - Commits: <shas>
   - jflow: <sessions> sessions · <fix rounds> fix rounds · <rows> rows · review <clean | skipped | n defects, m missed by prove> · net code <±n> · tests <±n>
   ```

5. When the human corrected you during this run, invoke `memory.remember` for that correction.
   Nothing else becomes a lesson.
6. Commit. Push the current branch; when the repo has no pre-push secret scan, first run
   `gitleaks git --log-opts="@{u}..HEAD" --redact -v --no-banner` and stop on any finding.

Done when the push succeeded. Close with one line: what shipped, and the proof count.
