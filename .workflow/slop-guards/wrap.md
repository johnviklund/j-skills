Command: workflow wrap slop-guards
Created: 2026-10-08
Base:    752ad6be9407e21c684b5345dbcfc0121c7e1e36
Inputs:  review.md @ 752ad6b
Status:  done

## Outcome
The workflow now pushes back on run size. Plans carry a `Size:` block and a `Budget:` per ticket; `check-run.py` warns on overruns and errors on test bloat, missing review `Size:` and missing wrap `Retired:`. The docs teach smallest diff, search-before-writing, proportional tests, and retiring obsolete code.

## Shipped (ticket → commit)
T1 d5289bd · T2 b9381ca · T3 fbe43c1 · T4 d6280d0 · T5 6484bb8 · T6 5a92358 · T7 0c1e7ac · T8 fb10679
Patch cycle: C1-T1 6e8efc9/bc114fc (empty `Risk:` crash) · C1-T3 dd167fe/0e888de (zero `Budget`).

## Review
Cross-vendor (OpenAI reviewer, Opus 5.5 writer). 2 cycles; C1 found 2 P1s, both fixed; C2 ship as-is, 0 open.

## Deferred / routed
- Learnings (2, `unittest -k` keyword rules) → `references/tests.md` "Verify keywords".
- No TODO.md, PRODUCT.md, DESIGN.md; ROADMAP.md has no slop-guards item: no changes. No feature map. No eval cases.
- Only warning: plan.md 131 lines vs ~120 budget (plan predates the gate).

## Receipts
`receipts/c1-verification.md`, `receipts/c2-verification.md`, `notes/seed-review-and-plan.md`.

Final checks: 20 unit tests pass; shortcut grep clean.
Retired: none — the run only added checks and docs; nothing it replaced
