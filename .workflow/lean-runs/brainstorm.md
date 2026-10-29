Command: workflow brainstorm lean-runs
Created: 2026-10-17
Base:    5ff0790
Inputs:  none
Status:  done

## Problem
Workflow runs in work-repo grow the test suite and take many sessions. Plans fill the caps
(12–15 behaviours, 7–8 tickets, 29–44 acceptance lines per run), each acceptance line becomes its own
test, and half the tickets add more test lines than code lines. Evidence: `notes/evidence.md`.

## Outcome
On the next work-repo run, `check-run.py` errors on a brief over 8 behaviours or a plan over 20
acceptance lines unless the human declined the split, and on a ticket commit whose tests pass 1.5× its
code. The plan reference asks for one test per behaviour. Seen in check-run output and the references.

## Behaviours
- B1 — complete brief, 9 behaviours, no `Split declined by human:` line → check-run ERROR naming 9 and 8; with the line → no error; 1 behaviour → no warning
- B2 — complete plan, 21 acceptance lines across its tickets, no approval line → ERROR naming 21 and 20; 20 lines → clean; 21 lines with the line → clean
- B3 — done contract-lane ticket commit adding tests +76, code +50 → ERROR; tests +75, code +50 → no error; the logic lane the same
- B4 — plan ticket `Budget: code +60 · tests +120` with no reason → WARN; the same with `· why: <reason>` → no warning
- B5 — brief or plan created before the new gate date, over the new limits → only today's warnings, no new ERROR
- B6 — `phase-2-plan.md` states one test per behaviour at its seam with parametrized cases, and limits *Inherited semantics* to consumers the plan names at risk → "Each acceptance line is one test" occurs 0 times
- B7 — workflow docs and both READMEs state 8 behaviours, 20 acceptance lines and 1.5× → "15 behaviours", "5–15" and "3×" occur 0 times outside `SKILL-IMPACT.md` and `WORKLOG.md`
- B8 — this run's edits to workflow `*.md` (excluding `SKILL-IMPACT.md`, `WORKLOG.md`) → net lines ≤ 0 in a numstat receipt

## Decisions
- D1 — The `check_worklog` TODO item stays out — unrelated to run size; one outcome per run (product call)
- D2 — A run holds at most 8 behaviours and 20 acceptance lines across its plan tickets (product call; evidence: notes/evidence.md)
- D3 — Over either limit, check-run errors unless the artifact records `Split declined by human: <when>` — same shape as `Cycle 3 approved by human:` (code: scripts/check-run.py:488)
- D4 — One test per behaviour at its seam; acceptance lines sharing a seam are cases of one parametrized test; `phase-2-plan.md:57` rewritten to match `tests.md:12` (product call)
- D5 — Tests over 1.5× code (≥ 50 test lines) in a logic or contract ticket commit is an ERROR; a plan Budget with tests > code and no reason warns (product call; flags 13 of 39 recent tickets)
- D6 — *Inherited semantics* applies only to consumers the plan names as at risk (product call)
- D7 — This run's workflow doc edits are net ≤ 0 lines, `SKILL-IMPACT.md` and `WORKLOG.md` excluded (product call)
- D8 — Behaviours per brief 1–8; the under-5 warning goes (product call)
- D9 — A Budget with tests > code carries its reason on the same line as `· why: <reason>` (code: check-run `field(t, "Budget")`)
- D10 — New checks gate on a new `*_SINCE` date, like `SLOP_SINCE`, so finished runs stay clean (code: scripts/check-run.py:56)

## Test seams
- `scripts/tests/test_check_run.py` — check-run run as a subprocess on fixture runs — observes B1–B5 (existing)
- `grep -c` over the workflow docs and READMEs — observes B6, B7 (existing)
- `git diff --numstat <Base>..HEAD` receipt — observes B8 (existing)

## Out of scope
- `TODO.md` `check_worklog` path bug — unrelated to run size (D1)
- Ratchets, a simplify pass before review, real retiring at wrap — the second run
- Fix-ticket sizing in `patch_plan.md` — cycles are already bounded at two
- Edits inside work-repo (`work-repo-implementation-practices`) — read-only here; the human edits it
- Execute's tickets per session — set by run-sizing, still trialing

Docs read: none in scope (j-skills has no PRODUCT.md or DESIGN.md)
