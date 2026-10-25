Command: workflow brainstorm checkup-next-actions
Created: 2026-10-25 · Claude Opus 5.5
Base:    080ecdf
Inputs:  none
Status:  complete

## Problem
A checkup ends with "Recommended next": at most three one-line actions that name a skill but give no prompt to paste, no model to pick and no word on starting a new session. The human finishes the report and still has to work out how to act, and where checkup lacked a fact it guessed instead of asking (example: cx-intelligence checkup, 2026-10-25).

## Outcome
The checkup report in chat ends with numbered questions, then at most three action cards, then the safe-fix line. Each card carries a model and fallback taken from `ROUTING.md`, says whether to start a new session, and holds a fenced prompt that works in a fresh session. The report follows the `plain` Rules.

## Behaviours
- B1 — `skills/checkup/references/report.md` holds the output format, card, question shape and skill → seat table; `SKILL.md` points to it, has no inline output-format block and is under 23,646 bytes (`wc -c`)
- B2 — checkup on cx-intelligence → every action is a card with Why, Reset, Model and Fallback bullets and a fenced `text` prompt, with no Reads line; a section with no ⚠️/🔴 is one ✅ line
- B3 — a `memory.remember` card → Model `Sonnet 5.5 · high`, Fallback `GPT-6 Sol · high`: the Brainstorm partner row that the table maps `memory.*` to
- B4 — one card's prompt pasted into a fresh cx-intelligence session → the session starts the named work on the named pages or paths without asking for the checkup's context (receipt)
- B5 — a seat promotion candidate → a numbered question with the ➡️ option first and a reason on every option, above the cards; its card reads `Model: human · <the edit>` and quotes the new `ROUTING.md` row
- B6 — a finding whose severity hangs on a fact no file shows (cx: the missing `.claude/skills/verify-*` link, where "Claude Code is blocked here" was assumed) → asked as a question with its evidence, not settled by a guess
- B7 — warnings that share one fix → one card (cx: leftover `## Execution state` blocks, `.DS_Store` and loose files in finished runs → one "tidy finished runs" card); never more than three cards
- B8 — `grep plain skills/checkup/SKILL.md` → a line telling checkup to invoke `plain` once before writing the report

## Decisions
- D1 — Each action is a workflow-style closing card: Why, Reset, Model, Fallback, then a fenced prompt — the shape the human already reads after every phase; the fence gives a copy button (product call)
- D2 — The fenced prompt is self-contained: the command plus the finding's evidence (slugs, paths, lines), so it works in a fresh session and Reset is yes for every agent action (product call)
- D3 — Checkup holds a small skill → seat table (memory.*, evals.run, verify.maintain, workflow commands); the model and fallback come from ROUTING.md for that seat, so a routing change needs no checkup edit (product call; code: skills/workflow/ROUTING.md)
- D4 — Human-only calls (promote a seat, prune the exam set) are asked in the workflow question shape (➡️ option first, a reason per option); the card reads `Model: human · <the one edit>` and quotes the exact new line (product call)
- D5 — At most three actions; warnings that share one fix become one action with one prompt (product call)
- D6 — The new rules go in `skills/checkup/references/report.md`, read only when writing the report; `SKILL.md` shrinks by about 2 KB (product call)
- D7 — No Reads field: the self-contained prompt already names the paths (product call)
- D8 — Proof is a cx-intelligence checkup receipt plus one card's prompt run in a fresh session (product call)
- D9 — Order: questions, then action cards, then the safe-fix line (product call)
- D10 — Unknowns are asked, not assumed: when a finding's severity or fix hangs on a fact checkup cannot read (intent, whether a tool is used, whether a parked run is still wanted), it becomes a question in the same list as D4's, at most 5 in all (human, 2026-10-25)
- D11 — Checkup invokes `plain` once before writing the report, as `retro` does (human, 2026-10-25; code: skills/retro/SKILL.md:28)

## Test seams
- `grep` and `wc -c` over `skills/checkup/` — observes B1, B8 (existing)
- `checkup` report on `~/cx-intelligence` after a pull, saved as a receipt — observes B2, B3, B5, B6, B7 (manual)
- One card's prompt run in a fresh cx-intelligence session, saved as a receipt — observes B4 (manual)

## Out of scope
- A full trim of checkup's `SKILL.md` to ~10 KB — its own run with its own review
- Edits to `ROUTING.md` — only the human edits it (D3)
- Changes to the checks themselves, their severities or the safe-fix allow-list
- Editing cx-intelligence — read-only reference

Docs read: none in scope (checkup and workflow skills only)
