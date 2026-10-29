Command: workflow review next-step
Created: 2026-10-29
Base:    1aa0b47
Inputs:  review.md @ 1aa0b47
Status:  complete

## Phase 4 — review (2026-10-29)
- [durable→memory] Second occurrence of "A new guard needs one test per key it matches on": a new reader of run text was narrower than the corpus and than the check that already parses the same field. next-step's receipt pattern refuses the backticked form a real plan uses (C1-2), and its own copy of check-run's open-fix test reads only the latest review cycle (C1-1). Reuse the existing check's predicate rather than copying it, and test one case per real form found in `.workflow/`. The writer's sweeps reported 54 of 54 caught; tests.md:70 already asks for one mutation per added condition, and the whole-file sweep still found 8 survivors (C1-3).
- [durable→eval] code-review — next-step reads only the latest review cycle, so an unstamped `fix now` finding from cycle 1 routes the run to wrap while check-run counts it open; missed by the writer (GPT-6.1 Sol) and its 23-mutation sweep, caught by the reviewer (Claude Opus 5.5) in cycle 1 (C1-1).
- [durable→eval] code-review — the receipt pattern `receipt:\s*(receipts/…)` refuses ``receipt: `receipts/x.md` ``, a form the repo's own plans use, so an operator ticket stays blocked after its receipt lands; missed by the writer (GPT-6.1 Sol), caught by the reviewer (Claude Opus 5.5) in cycle 1 (C1-2).
