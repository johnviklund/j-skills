Command: workflow execute checkup-next-actions
Created: 2026-10-25
Base: bc2a0e2
Inputs: plan.md @ 3480338
Status: complete

T2 runner: agent after approval. Risk: cheap. Approval already recorded in plan Decisions 2a.
1. Secret-scan and push j-skills main; run `npx skills update -g` on this server.
2. Confirm installed report.md equals the repo file with `diff -q`.
3. Refresh the clean work-repo reference clone with its work account; restore the personal account.
4. In `~/work-repo`, run `claude -p --permission-mode plan "checkup"` in a fresh session.
   Save its report as `receipts/t2-work-repo-checkup.md`; keep raw transcripts outside this repo.
5. Run the first agent card's exact prompt in another fresh session in plan mode.
   Save named-path read evidence and context-question result as `receipts/t2-fresh-session.md`.
6. Verify every T2 acceptance clause and compare work-repo git status before and after.
Both sessions only read work-repo; no edits, commits or pushes there. Installation refreshes all global j-skills.
