Command: workflow brainstorm memory-patterns-and-budget
Created: 2026-10-26 · claude-sonnet-5-5
Base:    068776cec34bf0efb0e2ec87204ab64378e62b53
Inputs:  none
Status:  complete

## Problem
`memory.compact` compares done runs only against pages that already exist, so a lesson that appears in two runs and has no page is never noticed. `memory.remember` promotes a rule into `AGENTS.md` with no cost check, so that always-loaded file only grows. Source: the ai-memory review.

## Outcome
`skills/memory.compact/SKILL.md` and `skills/memory.remember/SKILL.md` carry both rules. A compact pass proposes a page for a repeated lesson; a remember pass routes a low-value `AGENTS.md` rule elsewhere.

## Behaviours
- B1 — compact reads every line of the `learnings.md` of the last ~10 done runs, `[drop]` and routed-to-`none` lines included → two or more runs with the same cause and the same fix, and no page, produce a proposed page.
- B2 — a proposed page → sits in `memory.proposed/` with `Occurrences: 2`, one `Evidence` entry per run, and the admission test applied; a match that belongs to a skill, `AGENTS.md` or `README.md` is named in the report, not paged.
- B3 — a lesson already on a page (its run in `Evidence`) → is not proposed again.
- B4 — remember is about to add a rule to `AGENTS.md` → it asks whether removing the rule would cause a mistake on a typical task in the repo; a no sends the rule to a memory page or a skill reference, with at most a one-line pointer left in `AGENTS.md`.
- B5 — the repo states a line cap in `AGENTS.md` and the file is within 10% of it → remember names one existing line to remove or move in the same pass; with no stated cap, only the removal test runs.
- B6 — `SKILL-IMPACT.md` → one `trialing` row per skill edit, each in its own commit, with the judge: the next 3 runs show a proposed repeat page (compact) or a routed-away rule (remember).

## Decisions
- D1 — the cap comes from the repo's own `AGENTS.md`, no default number — `workflow` already reads its cost ceiling that way (code: `skills/workflow/references/phase-2-plan.md:109`)
- D2 — a rule that fails the removal test is routed to its owner in the same pass, never dropped or tagged — matches `memory.remember`'s route-don't-stage rule (code: `skills/memory.remember/SKILL.md`)
- D3 — all learnings lines count, because `[drop]` and routed-to-`none` verdicts are where repeats hide (product call)
- D4 — a match becomes a page in `memory.proposed/`, not just a report line, so acceptance stays the one guarded swap (code: `skills/memory.compact/SKILL.md` step 6)
- D5 — one run for both edits; each skill edit is its own commit (product call)
- D6 — "recurs" means the same cause and the same fix, not the same topic (product call)

## Test seams
- Doc text of the two `SKILL.md` files, read by `grep` for the new rules — observes B1–B5 (existing)
- A dry run of the compact steps over the 7 existing `learnings.md` files, output read by hand — observes B1–B3 (new)
- `SKILL-IMPACT.md` rows, read by `grep` — observes B6 (existing)

## Out of scope
- A script that finds repeats mechanically — matching is a judgement call and the data is about 50 lines
- A line cap for `README.md` or for skills — only `AGENTS.md` is always loaded
- Changing the ~40-page memory ceiling — it already bounds pages
- Editing `agent-docs` — it already names context load; remember points to it

Docs read: none in scope (j-skills has no PRODUCT.md or DESIGN.md)
