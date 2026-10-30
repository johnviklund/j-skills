Command: workflow wrap next-step
Created: 2026-10-30
Base:    8bfbbf0
Inputs:  review.md @ 91a5e68
Status:  done

# next-step — wrap

**Outcome.** `next-step.py` now decides every phase's next step from the run's files and ROUTING.md. The closing card, `workflow next` and `workflow status` print its output, and `--json` (schema 1) serves an outside conductor. ROUTING.md has keyed tables, patch tickets carry `Fixes: C<n>-<m> (P#)`, and checkup copies its model lines from `--key`. Roadmap step 1 of the v3 goal is done.

**Shipped.**
- T1 ROUTING parses, plan card · 904f083
- T2 ticket lanes and operator handoffs · 70fefa2
- T3 fix tickets by severity and lane · 17c8020
- T4 review, wrap, parked, done · 53d959c
- T5 phases print the script's card; checkup `--key` · a354025
- Patch cycles 1–3: C1-T1..T5 (e6a8e5d, f2bba2b, 0762b64, 6e87503, 08048cb), C2-T1/T2 (eac69f8, 5c5e306), C3-T1 (3b72722)

**Review.** Ship as-is at cycle 4, cross-vendor (writer GPT-6.1 Sol, reviewer Opus 5.5). 8 findings fixed (C1-1..5, C2-1, C2-2, C3-1); 0 overturned. Open P3s (C1-6, C2-3, C3-2, C4-1) stay in `review.md`.

**Deferred.** The P3 items above, in `review.md`. TODO "checkup guardrail" (C1-1) was completed by T5 and archived.

**Learnings.** Five times a fixture was narrower than the real files. Routed to the workflow skill's `tests.md` (*Fixtures copy the real form*, SKILL-IMPACT trial). Four missed P1s deposited in the private strict-reviewer exam set (cap 10; four oldest dropped).

**Receipts.** `receipts/` holds a verification record per ticket (t1–t5, c1-t1..t5, c2-t1/t2, c3-t1).

Product docs: no PRODUCT.md or DESIGN.md; ROADMAP.md step 1 moved to ROADMAP_ARCHIVE.md.
Retired: none — the run replaced no code path; it added new files.
