Command: workflow brainstorm threat-model-review
Created: 2026-10-22 · Sonnet 5.5
Base:    6aa7823
Inputs:  none
Status: done

## Problem
Review's only security check is the one clause "security flaws" (`phase-4-review.md:31`) plus the dependency check and the push-time secret scan. A run that adds a trust boundary (outside input, credentials, writes, shell, permissions) gets no systematic question about what an attacker could do there.

## Outcome
A brief names its trust boundaries when the work touches one, and Review checks the diff against a short fixed checklist for each. A run that touches none pays nothing. Surface: `brainstorm.md` and `review.md` of any run, and the workflow reference docs.

## Behaviours
- B1 — a brief whose work touches a trigger (outside input, auth or credentials, file or network writes, shell execution, new permissions) → carries a `## Trust boundaries` section, one line per boundary
- B2 — a brief that touches no trigger → no `## Trust boundaries` section and no review threat pass
- B3 — Review of a run with `## Trust boundaries`, or whose diff adds a trigger the brief missed → `review.md` has a threat-model line per boundary answering the six checklist questions
- B4 — a threat found by that pass → rated on the existing bar (exploitable hole P0/P1, unmitigated plausible threat P2, hardening idea P3), no second severity table
- B5 — `SKILL-IMPACT.md` → a row for this change, 3-run trial, judge: review names at least one boundary on trigger runs and raises no false alarm on non-trigger runs
- B6 — `check-run.py` on a brief with and without `## Trust boundaries` → no error either way

## Decisions
- D1 — brainstorm records boundaries, Review checks them; no new command — names the risk while the design is cheap, and Review verifies (product call)
- D2 — fires only on a trigger in the brief or the diff — most runs touch none (product call)
- D3 — checklist, STRIDE-lite, six questions per boundary: who can send input, what it can reach, what it can change, what is logged, what fails open, what is the worst case — repeatable and cheap (product call)
- D4 — severity uses the existing bar (code: references/phase-4-review.md:64)
- D5 — trial as a `SKILL-IMPACT.md` row, like today's two security rows (code: SKILL-IMPACT.md:13)
- D6 — edits go in `.github/skills/workflow/`; `skills/` is a symlink to it (code: `ls -la skills`)

## Test seams
- `check-run.py` through `scripts/tests/test_check_run.py` — observes B6 (existing); B1–B5 are doc greps and a read of the edited references

## Out of scope
- full STRIDE, data-flow diagrams, a threat register — heavy for solo runs
- a `workflow threat-model` command — one more thing to remember
- a plan-phase threat step — the brief already names boundaries, tickets inherit them
- a check-run gate on the section — the pass is judgement, not a form field
- TODO.md items — none match

Docs read: none in scope (no PRODUCT.md or DESIGN.md in this repo)
