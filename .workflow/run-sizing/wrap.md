Command: workflow wrap run-sizing
Created: 2026-10-10
Base:    38dea5df6e9017b0ef36d863fa457ab53206defd
Inputs:  review.md @ 38dea5df6e9017b0ef36d863fa457ab53206defd
Status:  done

## Outcome
The workflow now sizes work bigger: plans aim for 2–5 right-sized tickets (8 is a ceiling), execute runs up to 3 tickets per session, and review allows two cycles. `check-run.py` warns when the median code Budget is small, accepts 6 acceptance lines, and errors on a third review cycle without the human's approval.

## Shipped (ticket → commit)
T1 1d56b03 · T2 d3ce44c · T3 f3d885e
Patch cycle 1: C1-T1 36b844d (six-line boundary test) · C1-T2 69370a6 (one run-wide session ledger in plan.md)

## Review
Cross-vendor (OpenAI reviewer, Opus 5.5 writer). 2 cycles; C1 found 2 P1s, both fixed; C2 ship as-is, 0 open.

## Deferred / routed
- Learning (1) → `references/tests.md` "Test the boundary"; 1 dropped (already in the rules).
- Human-only, optional: `ROUTING-NOTES.md:11` lists the `Run:` fields without `sessions`; `ROUTING.md` *Modes* still says tickets of different lanes can share a session.
- No TODO.md, PRODUCT.md, DESIGN.md, ROADMAP.md: no changes. No feature map. No eval cases.
- Trial: `SKILL-IMPACT.md` logs run-sizing; judge it on the next runs' ticket counts and cycles.

## Receipts
`receipts/c1-verification.md`, `receipts/c1-t1-mutation.md`, `receipts/c1-t2-verification.md`, `receipts/c2-verification.md`, `notes/proposal.md`.

Final checks: receipt-rule diff `38dea5d..HEAD` empty, so no suite run (31 tests passed at review); shortcut grep clean.
Retired: none — the run only added checks and rules; nothing it replaced
