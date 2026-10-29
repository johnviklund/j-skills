Command: workflow review next-step
Created: 2026-10-29
Base:    1aa0b47
Inputs:  review.md @ 1aa0b47
Status:  complete

## Phase 4 — review (2026-10-29)
- [durable→memory] Second occurrence of "A new guard needs one test per key it matches on": a new reader of run text was narrower than the corpus and than the check that already parses the same field. next-step's receipt pattern refuses the backticked form a real plan uses (C1-2), and its own copy of check-run's open-fix test reads only the latest review cycle (C1-1). Reuse the existing check's predicate rather than copying it, and test one case per real form found in `.workflow/`. The writer's sweeps reported 54 of 54 caught; tests.md:70 already asks for one mutation per added condition, and the whole-file sweep still found 8 survivors (C1-3).
- [durable→eval] code-review — next-step reads only the latest review cycle, so an unstamped `fix now` finding from cycle 1 routes the run to wrap while check-run counts it open; missed by the writer (GPT-6.1 Sol) and its 23-mutation sweep, caught by the reviewer (Claude Opus 5.5) in cycle 1 (C1-1).
- [durable→eval] code-review — the receipt pattern `receipt:\s*(receipts/…)` refuses ``receipt: `receipts/x.md` ``, a form the repo's own plans use, so an operator ticket stays blocked after its receipt lands; missed by the writer (GPT-6.1 Sol), caught by the reviewer (Claude Opus 5.5) in cycle 1 (C1-2).

## Phase 4 — review cycle 2 (2026-10-29)
- [durable→memory] Third occurrence in this run of a reader narrower than the corpus (after C1-1 and C1-2): next-step now reads every review cycle, but finding ids are positions, and the real fold form in `.workflow/run-worktrees/review.md` at 68cbf30 shifts them (C2-1). When a fix widens what a parser reads, test it on a real artifact in that wider state.
- [durable→memory] A shared predicate proves nothing for a caller with no test. C1-T1 moved check-run's open-finding gate, which wrap reads, onto `open_finding` and cited "test_check_run.py passes unchanged" as proof, but no test asserted that note, so inverting the gate stayed green (C2-2). Mutate each caller of a shared helper, not only the new one.
- [durable→eval] code-review — after the fix that reads every review cycle, the blocker names finding ids by position, so once earlier findings fold into `## Resolved` it asks for a resolved finding (run-worktrees @ 68cbf30: "Resolve C2-1" while C2-2 is open); missed by the writer (GPT-6.1 Sol), caught by the reviewer (Claude Opus 5.5) in cycle 2 (C2-1).
