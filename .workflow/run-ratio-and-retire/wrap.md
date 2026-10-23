Command: workflow wrap run-ratio-and-retire
Created: 2026-10-23
Base:    d1f9b5f
Inputs:  .workflow/run-ratio-and-retire/review.md @ d1f9b5f
Status:  done

# run-ratio-and-retire — summary

**Outcome.** `check-run.py` now judges test growth once per run, when the last ticket is done: tests net above 1.5× code added is an error unless `## Deviations` holds `Ratio waived: run — <reason>`. The per-ticket ratio is a warning. `checkup` prints each repo's test growth beside code growth and points at `workflow improve` when tests outgrow code.

**Shipped.**
- T1 run-level test gate, `growth()` helper shared by three callers → 577a33a
- T2 docs state the run rule; checkup test-growth line → b8c24ce
- C1-T1 gate counts done statuses that carry a note after the sha (C1-1) → 40f9e4f (red test 7ac1df2)

**Review.** Ship as-is after 2 cycles; cycle 1 had one P1 (fixed). 49 tests pass. Net code +16, tests +1. Replay over 26 runs flags 1 (`live-run-guardrails`).

**Deferred.** C1-2, C1-3, C1-4 (P3) stay in `review.md`. Nothing went to `TODO.md`.

**Product docs.** No PRODUCT.md or DESIGN.md. ROADMAP step 3 moved to `ROADMAP_ARCHIVE.md`.

**Learnings.** Matcher-forms lesson added to the workflow `MEMORY.md` guard-keys entry. Eval case not deposited: exam set is full (10) and the miss is the same class as two cases in it.

**Feature map.** No verify skill. **Evals.** No cases deposited.

**Receipts.** `receipts/` (t1 and c1-t1 verification and replay, t2 checkup on cx-intelligence), `scripts/replay.py`, `notes/P1-run-gate.md`, `prototypes/P1-run-gate/`.

Retired: none — the run changed one gate in place and merged its own tests; no other product file became obsolete.
