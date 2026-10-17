Command: workflow brainstorm growth-ratchets
Created: 2026-10-18
Base:    1971256
Inputs:  none
Status:  complete

## Problem
check-run's ticket ratio gate counts lines added, so a rewrite or move trips it (governed-execution-discovery T2, T3). The writer then names the ticket under `## Deviations`, and any mention of the ticket ID skips the budget and ratio checks (`check-run.py:380`), even a receipt pointer (T4). Separately, `check_worklog` reads only a repo-root `WORKLOG.md`; this repo's is in the skill folder, so done runs report "no entry".

## Outcome
On the next run, `check-run.py` flags a ticket whose tests grow past 1.5× its code without counting rewrites or moves, and a ticket skips that check only through a keyed waiver line that check-run prints back with its numbers. `check-run.py --all` in j-skills reports no worklog error. Seen in check-run output.

## Behaviours
- B1 — logic ticket commit with tests +201 −305, code +89 −313 (T2 shape), or tests +252 −128, code +134 (T3 shape) → no ratio ERROR
- B2 — logic ticket commit with tests +130 −10, code +60 → ERROR naming tests net 120 and allowed 90; tests net 90 → no error; tests net 49, code 0 → no error
- B3 — over-ratio ticket with `Ratio waived: T2 — <reason>` under `## Deviations` → no ERROR, one warning naming tests net and allowed; with only `T2 proof: receipts/…` there → ERROR
- B4 — a `Ratio waived: T2 —` line with no reason → the ratio ERROR stands
- B5 — ticket net over 2× its Budget: with `Budget waived: T2 — <reason>` → no warning; with a bare `T2` mention → warning
- B6 — plan created before `GROWTH_SINCE` (2026-10-19) → added-lines ratio and any-mention skip behave as today
- B7 — `check-run.py --all` in j-skills → no `WORKLOG.md has no entry` error for run-sizing or lean-runs; `WORKLOG.md` sits at the repo root
- B8 — `tests.md`, `phase-3-execute.md` and the check-run messages name net tests and the waiver keys → "explain exceptions under `## Deviations`" and "log the reason under `## Deviations`" occur 0 times; this run's workflow `*.md` edits (excluding `SKILL-IMPACT.md`, `WORKLOG.md`) net ≤ 0 lines

## Decisions
- D1 — Ratio compares tests net (added − deleted) with code added; 1.5× and the 50-line floor stay — clears T2, T3, T4 and still flags bloat (prototype: P1)
- D2 — Waiver is a keyed line under `## Deviations`: `Ratio waived: T# — <reason>`, `Budget waived: T# — <reason>`; a bare ID skips nothing; each waiver prints a warning with the numbers; review reads it (code: scripts/check-run.py:347,380)
- D3 — Waivers are written by the writer, not the human — review is the independent check (product call)
- D4 — No run-level gate; review's `Size:` line already reports net (product call; prototype: P1 shows 5 of 12 historic runs would flag)
- D5 — `git mv .github/skills/workflow/WORKLOG.md WORKLOG.md`; no check-run change — wrap, checkup and bootstrap already read the root (code: references/learning-worklog.md:86)
- D6 — New checks gate on `GROWTH_SINCE = 2026-10-19`, like `LEAN_SINCE` (code: scripts/check-run.py:59)
- D7 — This run's workflow doc edits are net ≤ 0 lines (product call, as lean-runs D7)

## Test seams
- `scripts/tests/test_check_run.py` — check-run as a subprocess on fixture runs — observes B1–B6 (existing)
- `check-run.py --all` and `ls WORKLOG.md` in j-skills — observes B7 (existing)
- `grep -c` over the workflow docs and `git diff --numstat` receipt — observes B8 (existing)

## Out of scope
- Run-level ratio gate (warn or error) — D4; the cheap next step if tickets pass and runs still bloat
- Ratio gate on the mechanical lane — floor and Budget already cover it
- A simplify pass before review, real retiring at wrap — the lean-runs remainder, a later run
- Moving the skill folder's `MEMORY.md` and `SKILL-IMPACT.md` — not named by the TODO
- Edits inside cx-intelligence — read-only here
- Human-approved waivers — D3

Docs read: none in scope (j-skills has no PRODUCT.md or DESIGN.md)
