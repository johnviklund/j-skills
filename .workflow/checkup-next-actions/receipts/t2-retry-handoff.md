Command: workflow execute checkup-next-actions
Created: 2026-10-25
Base: 364d378
Inputs: plan.md @ 37f7b44
Status: complete

T2 runner: agent after approval. Risk: cheap. Installation and clone refresh already passed.
Approval received 2026-10-25: user selected 1a, allowing Claude Code to read private ~/cx-intelligence files and send their contents to Anthropic for two paid read-only sessions.
1. Run in ~/cx-intelligence: `claude -p --permission-mode plan --verbose --output-format stream-json 'checkup'`.
2. Keep raw transcripts in /tmp; save the report as receipts/t2-cx-checkup-2.md in this run.
3. Verify every T2 report acceptance clause. A failed clause stops the ticket; no further paid retry is authorized.
4. If the report passes, run its first agent card's exact prompt in a fresh Claude plan-mode session in the same clone.
5. Save named-path read evidence and whether it asks for checkup context in receipts/t2-fresh-session.md.
6. Compare cx HEAD and git status before/after; no edits, commits or pushes there. Verify all acceptance clauses and persist the result here.
Automatic approval review initially rejected step 1 for missing private-data authorization. The user's explicit 1a approval now authorizes the scope above.
