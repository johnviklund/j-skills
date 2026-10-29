Command: workflow brainstorm lean-runs
Created: 2026-10-17
Base:    5ff0790
Inputs:  none
Status:  complete

# Evidence from work-repo (read-only clone, HEAD 4c2567bc)

Runs since slop-guards and run-sizing (created 2026-10-09 or later, 11 runs):
- Tickets per run: 7, 4, 8, 5, 8, 8, 4, 8, 7, 6, 5. Median 7. Four of 11 meet run-sizing's "≤ 5" judge.
- Five runs sampled: behaviours 12–15 (cap 15), acceptance lines 29–44 per run.
- `live-run-guardrails`: one run, six separate deliverables (git hooks, retry, probe, rehearsal, waiter, deploy tool).

Ticket commits (51 tickets, `done @` sha, `.md`/`.txt`/`.workflow/` excluded):
- code +5,001 · tests +3,921 (0.78×). Logic lane: code +1,440 · tests +1,644 (1.14×).
- 26 of 51 tickets add more test lines than code lines. About 4 test functions per ticket.
- Logic and contract tickets with tests ≥ 50 lines (39 tickets): over 1× → 18 · over 1.5× → 13 ·
  over 2× → 9 · over 3× → 3. Today only the 3× check exists, and only for the logic lane.

Plans: in the last four plans, 16 of 30 tickets budget more test lines than code lines
(e.g. `Budget: code +60 · tests +120`). check-run checks the commit against the Budget, never the Budget itself.

j-skills rules that drive the count:
- `phase-2-plan.md:57` "Each acceptance line is one test" contradicts `tests.md:12`
  "one end-to-end test per behaviour, not per acceptance line".
- `check-run.py` `check_overrun`: the TEST_RATIO error fires for `logic` only; `contract` is exempt.
