Command: workflow review growth-ratchets
Created: 2026-10-18
Base:    c4ce7f0
Inputs:  .workflow/growth-ratchets/review.md @ c4ce7f0
Status:  complete

## Phase 4 — review (2026-10-18)
- [durable→memory] A new checker condition shipped with no test value that can see it, and the cycle-1 mutation caught it. The cases here: the waiver's ticket key (growth-ratchets C1-1) and the legacy lane gate (lean-runs C1-1). When a guard keys on an ID, a date or a lane, add one case where only that key differs.
- [durable→skill] A size cap counted in lines can be met by unwrapping text, so measure doc growth in words (growth-ratchets C1-2: 19 words added, two execute rules dropped).
