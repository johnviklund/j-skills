Command: workflow brainstorm checkup-next-actions
Created: 2026-10-25 · Claude Opus 5.5
Base:    080ecdf
Inputs:  none
Status:  drafting

## Problem
A checkup ends with "Recommended next": at most three one-line actions that name a skill but give no prompt to paste, no model to pick and no word on starting a new session. The human finishes the report and still has to work out how to act (example: cx-intelligence checkup, 2026-10-25).

## Decisions
- D1 — Each action is a workflow-style closing card: Why, Reset, Model, Fallback, then a fenced prompt — the shape the human already reads after every phase; the fence gives a copy button (product call)
- D2 — The fenced prompt is self-contained: the command plus the finding's evidence (slugs, paths, lines), so it works in a fresh session and Reset is yes for every agent action (product call)
- D3 — Checkup holds a small delegate → seat table (memory.*, evals.run, verify.maintain, workflow commands); the model and fallback come from ROUTING.md for that seat, so a routing change needs no checkup edit (product call; code: skills/workflow/ROUTING.md)
- D4 — Human-only calls (promote a seat, prune the exam set) are asked as decisions in the workflow shape (➡️ option first, a reason per option); the card reads  and quotes the exact new line (product call)
- D5 — At most three actions stay; warnings that share one fix become one action with one prompt (e.g. "tidy finished runs") (product call)
