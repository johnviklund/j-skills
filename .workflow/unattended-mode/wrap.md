Command: workflow wrap unattended-mode
Created: 2026-10-30
Base:    fe33dbf
Inputs:  review.md @ fe33dbf
Status:  done

# unattended-mode — wrap

**Outcome.** A run whose brief says `Mode: unattended` never waits in chat after brainstorm. `references/unattended.md` holds the defaults and the always-stop list once. `decisions.md` rows are checked by `check-run.py`, and a `waiting` row becomes a `blocker` in `next-step.py --json`. A run with no `Mode` line behaves as before. Workflow is 3.0.0. Roadmap step 2 of the v3 goal is done.

**Shipped.**
- T1 mode and decisions checks, waiting blocker · 39fe912
- T2 unattended rules, hub pointer, version 3.0.0 · b5b8642
- C1-T1 UI code preserved at approval stops · 23f4ec6
- C1-T2 waiting decisions asserted in card reads · 2e8ad60
- C2-T1 execute decisions keep a run in its checkout · 056a042 (red) · f268f88 (fix)

**Review.** 3 cycles, verdict ship with 2 deferrals approved by the human (1b), 2026-10-30. Net code +27, tests +63.

**Deferred.** C3-1 (P1, one-row fixture lets `any`→`all` survive) and C3-2 (P2, unhandled `ValueError` in `open`) are in `TODO.md` under `## Review deferrals`. P3s C1-3 to C1-6 and C3-3 stay in `review.md`.

**Learnings.** 4 routed to skill edits in `bd2e938`: `tests.md`, `phase-4-review.md`, `agent-docs`; logged in `SKILL-IMPACT.md`.

**Product docs.** No `PRODUCT.md` or `DESIGN.md`. `ROADMAP.md` step 2 moved to `ROADMAP_ARCHIVE.md`.

**Receipts.** `receipts/` holds the T1, T2, C1-T1, C1-T2 and C2-T1 verification files. Final suite: 112 workflow tests OK, 8 checkup tests OK.

Retired: none — the run replaced no code path, flag or harness.
