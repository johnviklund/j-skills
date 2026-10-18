Command: workflow wrap guard-keys
Created: 2026-10-18
Base:    b98bb26
Inputs:  .workflow/guard-keys/review.md @ b98bb26
Status:  done

## Summary
Writers now add one test case per key a guard matches on, and a reviewer who finds one untested key lists and mutates every key. Execute regained its acceptance-seam and scope wording from before the growth-ratchets trim. The three references grew by a net +5 lines.

## What shipped
- T1 → e478a17: `references/tests.md`, `phase-4-review.md`, `phase-3-execute.md`, and a trial row in `SKILL-IMPACT.md`.

## Review
Ship as-is after 1 cycle (cross-vendor: GPT-6.1 Sol wrote, Opus 5.5 reviewed): 0 P0 to P2, 3 P3 deferred.

## Deferred
- P3-1 Verify greps one phrase per rule → routed to the `MEMORY.md` guard-key entry.
- P3-2 writer rule sits in the deny-list paragraph, P3-3 reviewer rule fires only after a key is found untested → stay in `review.md`; the `SKILL-IMPACT.md` trial judge decides.
- `TODO.md`: growth-ratchets C1-2 moved to `TODO_ARCHIVE.md` (completed by T1).

## Receipts
`receipts/t1-verification.md`. Product docs: none in this repo. Feature map: none. Eval cases: 0.

Retired: none — doc-only run, nothing replaced
