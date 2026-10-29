Command: workflow execute checkup-next-actions
Created: 2026-10-25
Base: bfa6d38
Inputs: plan.md @ e192505
Status: complete

T2 runner: agent after approval. Risk: costly. User approved replan 2 options 2a and 3a on 2026-10-25, including these two fixture sessions with USD 1 cap each. No further approval needed for this scope.

1. Secret-scan the unpushed commits, push main, run `npx skills update -g`, and compare installed report.md to the tracked file.
2. Dry run passed: rebuild the synthetic /tmp/checkup-fixture twice; clean tree, one commit, TODO.md 19,161 bytes, required fixture files present, no .claude directory. No work-repo file read or copied.
3. Run in the fixture: `claude -p --permission-mode default --allowedTools "Read Grep Glob Bash Skill" --disallowedTools "Write Edit NotebookEdit" --max-budget-usd 1 --verbose --output-format stream-json "checkup"`.
4. Keep the raw stream outside the repo in /tmp; extract the final result to receipts/t2-fixture-checkup.md and verify every report clause. A failed clause stops T2.
5. Only if all report clauses pass, run its exact workflow todo prompt in a fresh session with the same flags and USD 1 cap. Save the result and initial tool-read evidence to receipts/t2-fresh-session.md.
6. Compare fixture HEAD and git status before/after each session. No work-repo commands or edits. Save verification in receipts/t2-fixture-verification.md. No additional paid retries.
