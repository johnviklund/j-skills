Command: workflow brainstorm guard-keys
Created: 2026-10-18
Base:    29c49c7
Inputs:  none
Status:  complete

## Problem
A guard that matches on several keys (an ID, a date, a lane, a kind) keeps an untested key after the writer's one mutation and the reviewer's one mutation. This cost a review cycle three times (lean-runs C1-1, growth-ratchets C1-1 and C2-1). growth-ratchets T2 also trimmed `phase-3-execute.md` to meet a net-zero line cap and lost wording (C1-2).

## Outcome
`tests.md`, `phase-4-review.md` and `phase-3-execute.md` carry the key rule and the restored wording, within about +6 net lines. A logged trial judges it on the next 3 runs.

## Behaviours
- B1 — a ticket adds a guard that matches on several keys → `tests.md` tells the writer to add one case per key, differing only in that key.
- B2 — a review finds one untested key on a guard → `phase-4-review.md` tells the reviewer to list every key the guard matches on and mutate each.
- B3 — a reader opens "The ticket is the whole job" in `phase-3-execute.md` → it says to build what the acceptance lines describe at its seam, names a nearby bug, a tempting refactor and a missing feature as out-of-scope work, and says the ticket continues.
- B4 — the assertion-count and waiver rules in that paragraph → still present and unchanged in meaning (`Ratio waived: T#`, `Budget waived: T#`, the 2026-10-19 date).
- B5 — the doc diff against the base → at most +6 net lines across the three reference files, and `check-run.py --all` still reports 0 errors.
- B6 — `SKILL-IMPACT.md` → one `trialing` row naming the change, with the judge: any untested-key P1 in cycle 2 or later across the next 3 runs.

## Decisions
- D1 — the rule goes in both `tests.md` and `phase-4-review.md` — the writer line prevents the gap, the reviewer line catches what slips through (product call)
- D2 — size cap about +6 net lines, not net zero — a net-zero cap is what caused C1-2 (product call)
- D3 — C1-2's restored wording is this run's, so `TODO.md` drops the review deferral at wrap (code: `TODO.md`)
- D4 — the memory entry in `.github/skills/workflow/MEMORY.md` stays; wrap marks it as promoted (code: `MEMORY.md`)

## Test seams
- Doc text, read by `grep` for the new phrases and `git diff --numstat <Base>` for the line count — observes B1–B5 (existing)
- `python3 .github/skills/workflow/scripts/check-run.py --all` — observes B5 (existing)
- `SKILL-IMPACT.md` row, read by `grep` — observes B6 (existing)

## Out of scope
- A mechanical check in `check-run.py` that finds guards and their keys — needs a parser for arbitrary guards
- Any change to the waiver code or its tests — the code is reviewed and shipped
- Changes to `WORKLOG.md`, `ROUTING.md` or the plan and wrap references — the rule lives in execute, tests and review only

Docs read: none in scope (j-skills has no PRODUCT.md or DESIGN.md)
