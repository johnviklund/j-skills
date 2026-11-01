Command: workflow brainstorm retire-on-no-signal
Created: 2026-11-01 · claude-sonnet-5-5
Base:    952031e
Inputs:  none
Status:  drafting
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

## Out of scope
- `correction-mining` — ROADMAP step 3, own run
