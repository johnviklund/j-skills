Command: workflow execute run-ratio-and-retire
Created: 2026-10-23 · GPT-6.1 Sol
Base: 35dbff6
Inputs: .workflow/run-ratio-and-retire/plan.md @ cafdfaa
Status: complete

T1 uses `growth()` for ticket budgets, the run gate and wrap net growth. The existing `waiver()` parser handles the run waiver.

- Baseline: 51 tests passed; check-run reported 0 errors, 0 warnings. No additional build/lint commands, confirmed by the user.
- Red: revised ratio cases on the old checker failed, 18 failing subcases across 5 methods.
- Green: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests` passed 49 tests.
- Replay: `python3 .workflow/run-ratio-and-retire/scripts/replay.py ~/work-repo ~/agent-cv ~/j-skills` reported 26 runs, 1 flagged. See t1-replay.txt: live-run-guardrails tests +679, code added +442.
- Mutations, each restored afterward: floor `>=` to `>` failed 1 subcase; ratio `>` to `>=` failed 3; completion `all` to `any` failed 16; latest commit `max` to `min` failed 1; admitting mechanical tickets failed 1. Each command was the ticket's unittest `-k ratio`, exit 1.

Planned assertion changes: the six F7 methods had 12 assertion sites. The two retained methods have 5; the two new run methods add 5. File total: 76 to 74, methods 51 to 49. Ticket ERROR expectations become warnings. Old-date and bare-deviation cases merge into the lane table; duplicate overrun cases merge there too. Ticket-waiver cases move to the run waiver table, preserving wrong-kind, wrong-key and empty-reason rejection. The old `allowed 90` assertion duplicates the retained net-growth cases. The receipt-pointer case is covered by the empty/nonmatching waiver cases. No budget assertions changed.

The completion fixture lands T1 after T2, deletes old code, and adds code after the last ticket. This checks code-added measurement and the endpoint without HEAD contamination. The waiver table also rejects a waiver outside Deviations.
