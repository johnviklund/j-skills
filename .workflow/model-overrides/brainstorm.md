Command: workflow brainstorm model-overrides
Created: 2026-10-30 · Claude Sonnet 5.5
Base:    f27a9e3
Inputs:  none
Status:  complete
Mode: attended

## Problem
The closing card takes its model and effort from the one shared `ROUTING.md`. To use another model or effort for one run, the human edits that shared file, which changes every other run too.

## Outcome
A run can carry its own `.workflow/<slug>/routing.md` that replaces the model and effort for chosen phase keys. `next-step.py` (card and `--json`) shows the override for that run only; other runs and `ROUTING.md` are unchanged.

## Behaviours
- B1 — `routing.md` has a row `execute:logic | OpenAI · GPT-6 Sol | xhigh` → the card and JSON for that run show GPT-6 Sol · xhigh for `execute:logic`, with context and approval still from `ROUTING.md`
- B2 — a phase key with no row in `routing.md` → its card matches the `ROUTING.md` result
- B3 — a run with no `routing.md` → the card is byte-identical to today's
- B4 — an overridden key → the JSON `fallback` list is unchanged from `ROUTING.md`, and the card marks the model line `(override)`
- B5 — overrides put the review or plan model on the same vendor as an `execute:*` model → the card prints a one-line same-vendor warning and still exits 0
- B6 — a row with an unknown key, a malformed model cell, or an effort outside medium/high/xhigh → `next-step.py` exits 1 naming the row; `check-run.py` reports the same row as an ERROR

## Decisions
- D1 — override file is `.workflow/<slug>/routing.md`, a table `Key | Vendor · Model | Effort` — tracked, travels with the worktree, reuses `checks.table` (code: scripts/check-run.py:149)
- D2 — keys are `ROUTING.md` phase keys, not tickets — no ticket-to-key link to keep in sync (product call)
- D3 — same-vendor writer and reviewer warns and never blocks — single-provider runs are legitimate (product call)
- D4 — only the human writes it, by hand or by asking a phase to write it; no new command — keeps `ROUTING.md`'s human-only rule (product call)
- D5 — `routing.md` joins the allowed top-level artifacts in `check-run.py` (`ARTIFACTS`) and `SKILL.md`'s run table (code: scripts/check-run.py:47)
- D6 — the override replaces the model and effort only; fallback, context and approval stay from `ROUTING.md` (code: scripts/next-step.py:43)

## Test seams
- `next-step.py` `--json` and card output — observes B1–B5 (existing)
- `check-run.py` on a run folder — observes B6 (existing)

## Out of scope
- Per-ticket overrides — needs a ticket-to-key link in `plan.md`
- A `workflow route` command — one small table needs none
- Overrides in `status` output — add when a real need shows up
- Overriding fallback chains, context or approval — keeps the override to the two things asked for
- Blocking same-vendor runs — see D3
- Conductor changes (ROADMAP step 3) — it reads the JSON unchanged

Docs read: none in scope (workflow skill only; `ROUTING.md`, `MAINTAINING.md` table rows)
