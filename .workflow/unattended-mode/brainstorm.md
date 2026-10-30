Command: workflow brainstorm unattended-mode
Created: 2026-10-30 · Sonnet 5.5
Base:    59d3763
Inputs:  none
Status:  done
Mode:    attended

## Problem
When an outside conductor drives a run, plan, execute, review and wrap stop and wait for a chat
answer, or a model guesses silently. A phase needs fixed rules for a run nobody watches, and a
`decisions.md` that records what was asked, what was assumed and what still waits.

## Outcome
A run with `Mode: unattended` in its `brainstorm.md` header never waits in chat after brainstorm. `next-step.py --json` shows the conductor a blocker whenever a `decisions.md` row is `waiting`. A run without the line behaves as today. The version becomes 3.0.0.

## Behaviours
- B1 — `Mode: unattended` or `Mode: attended` in the header → `check-run.py` accepts it; any other value is an ERROR.
- B2 — a reader opens `SKILL.md` → it points to `references/unattended.md`, which holds the rules and the always-stop list once.
- B3 — A `decisions.md` row with status `assumed` → `next-step.py --json` returns the normal next step with `blocker: null`.
- B4 — A row with status `waiting` → `next-step.py --json` returns `blocker: {decision: "<id>", action: …}` and the card routes to the human.
- B5 — That row changed to `answered` → the blocker clears and the normal next step returns.
- B6 — A malformed `decisions.md` row (unknown status, missing column) → `check-run.py` ERROR.
- B7 — A run with no `Mode` line → `next-step` output is identical to today's and both existing test suites stay green.
- B8 — a reader opens `README.md` after wrap → it says Version 3.0.0 and `ROADMAP.md` step 2 is marked done.

## Decisions
- D1 — Brainstorm stays human-run; plan, execute, review and wrap get the unattended rules — the brief is the human's definition of done (product call)
- D2 — At a question an unattended phase writes a `decisions.md` row; a reversible choice takes the recommended default and goes on, an always-stop case stops with a blocker (product call)
- D3 — Always-stop cases, written once: P0/P1 deferral, a third review cycle, operator tickets that write live or irreversibly, UI approval, anything touching secrets (code: `phase-4-review.md:185-193`, `phase-3-execute.md:54,80`)
- D4 — Mode is a `Mode: unattended` header line in `brainstorm.md`, set at brainstorm; absent or `attended` means today's behaviour (product call)
- D5 — `decisions.md` is a plain table, columns id · phase · question · default · status (`assumed` | `waiting` | `answered`) · answer; `next-step.py` reads only the id and status columns (code: `review.md` `## Resolved` table)

## Test seams
- `next-step.py --json` — observes B3, B4, B5, B7 (existing)
- `check-run.py` — observes B1, B6 (existing)
- `grep` of `unattended.md`, `SKILL.md`, `README.md` — observes B2, B8 (existing files; `unattended.md` new)

## Trust boundaries
- conductor or human → `decisions.md` answers; read as data, never executed. An always-stop answer still lands in the artifact's existing field (`Approved by human:`).

## Out of scope
- The conductor, T3 tools, wake-ups, notifications — separate repo.
- An unattended brainstorm — D1.
- A decision model answering rows automatically — later roadmap step.

Docs read: none in scope (no PRODUCT.md or DESIGN.md)
