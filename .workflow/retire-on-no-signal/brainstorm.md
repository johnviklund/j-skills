Command: workflow brainstorm retire-on-no-signal
Created: 2026-11-01 · claude-sonnet-5-5
Base:    952031e
Inputs:  none
Status:  complete
Mode: attended

## Problem
Every skill-change trial that ends in "no signal" is marked `kept` (12 times); no skill change was ever reverted. Nothing records when a rule stopped a mistake, so a rule can neither earn nor lose its place. 36 `trialing` rows in `SKILL-IMPACT.md` are unjudged.

## Outcome
`checkup seats` counts save tags per `SKILL-IMPACT.md` row and lists a finished trial with no save and no gain as a removal candidate for `workflow improve`.

## Decisions
- D1 — Save tag is `[saved→skill] <row date> <skill> — <what it stopped>` in `learnings.md`; a same-date, same-skill pair adds words of the change — plain-file grep, no table id (product call)
- D2 — A finished trial is kept when `Run:` numbers are better or it has ≥1 save tag; otherwise a removal candidate (product call)
- D3 — One-time sweep lists every open `trialing` row as keep, insurance or candidate; the human confirms before any removal (product call)
- D4 — An `insurance: <incident>` note in the row's `From` column keeps a rule out of the candidate list (roadmap)

- D5 — The count is a stdlib script in `checkup/scripts/` with a unit test; `seats.md` calls it. It parses the `|` rows of `SKILL-IMPACT.md`; tags are plain grep lines (code: .github/skills/checkup/scripts/config-scan.py is the sibling)
- D6 — The sweep is the same script's `--sweep` flag; its output is the run's receipt

## Behaviours
- B1 — a `[saved→skill] 2026-11-01 workflow — …` line in a run's `learnings.md` → the script counts one save on the matching `SKILL-IMPACT.md` row
- B2 — a finished trial with no save and no better `Run:` numbers → listed as a removal candidate naming `workflow improve`
- B3 — a finished trial with ≥1 save, or better numbers → reported kept, not a candidate
- B4 — a row whose `From` column holds `insurance: <incident>` → never listed as a candidate
- B5 — two rows with the same date and skill → a tag counts only for the row whose change words it carries
- B6 — `--sweep` over the open `trialing` rows → prints each as keep, insurance or candidate and edits nothing

## Test seams
- the checkup script's output on a fixture `SKILL-IMPACT.md` plus `learnings.md` files — observes B1 to B6 (new)

## Out of scope
- `correction-mining` — ROADMAP step 3, own run

Docs read: none in scope (no PRODUCT.md or DESIGN.md)
