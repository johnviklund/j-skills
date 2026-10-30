Command: workflow wrap model-overrides
Created: 2026-10-30 · Sonnet 5.5
Base:    a7138d8
Inputs:  .workflow/model-overrides/review.md @ a7138d8
Status:  done

# model-overrides — wrap

Outcome: a human can drop a headerless `routing.md` in a run folder to set that run's model and
effort per ROUTING.md key. The card and JSON show `(override)` / `override: true`, and a run
whose writer and reviewer share a vendor gets a warning. Both scripts validate the rows; a done
run's `routing.md` is no longer checked, so a later key rename cannot break history.

## Shipped
- T1 → d9a0f8f (override in next-step and check-run) · T2 → 4db8014 (SKILL, MAINTAINING, README)
- C1-T1 → 5d2d876 (red 4b37b24) done runs skip routing.md · C1-T2 → a4135aa review and execute read the run's routing.md first
- Wrap: 4d53dcb routes two lessons to plan Risks and MAINTAINING; SKILL-IMPACT line added (trial 3 runs)

## Review
Two cycles. Cycle 1: 2 P2 fixed, 3 P3 deferred (C1-3 to C1-5, text in `review.md` and git at 966b7f8). Cycle 2: none, ship as-is @ 7689d09. Cross-vendor (GPT-6.1 Sol writer, Opus 5.5 reviewer).

## Deferred
P3s C1-3, C1-4, C1-5 stay in `review.md`; none go to `TODO.md` (P3 only).

## Receipts
`receipts/t1-verification.md`, `t2-verification.md`, `c1-verification.md`. Final checks: workflow 119 OK, checkup 8 OK.

Product docs: none exist. ROADMAP.md: no change (step 3 conductor reads the JSON; override changes only that run's `model`). TODO.md: no change.
Retired: none — the run replaced no code path, flag or test.
