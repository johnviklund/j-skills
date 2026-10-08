Command: workflow brainstorm slop-guards
Created: 2026-10-08
Base:    8fa6782
Inputs:  none
Status:  done

## Problem
The workflow checks that code is correct but never how much code a run adds. Its own rules (literal acceptance values, tests at the reached surface, full operator ceremony) make runs grow with nothing pushing back. In cx-intelligence a 12-line fix got a 178-line test, and a $0.005 probe got about 600 lines of script, test and receipts. Seed and evidence: `notes/seed-review-and-plan.md`.

## Outcome
A run's plan carries a size baseline and a line budget per ticket. `check-run.py` warns or errors on overruns, test bloat, missing review size lines and missing wrap retire lines. The skill's docs tell planners, executors and reviewers to prefer the smallest diff, reuse before writing, test proportionally, and delete what a run made obsolete. No new phases.

## Behaviours
- B1 — a plan with a `Size:` block and a `Budget:` on each ticket → `check-run.py` reports no new finding.
- B2 — a logic or contract ticket with no `Budget:` → WARN naming the ticket.
- B3 — a ticket commit with net lines over 2× its budget and no `## Deviations` line → WARN naming the ticket.
- B4 — a logic ticket with +12 code lines and +178 test lines and no stated reason → ERROR.
- B5 — an operator ticket with `Risk: cheap` whose commit adds `test_*.py` under the run's `scripts/` → WARN.
- B6 — an operator ticket with no `Risk:` → WARN; a repo that states no cost ceiling treats every paid call as `costly`.
- B7 — an acceptance line over 40 words → WARN naming the ticket.
- B8 — a `review.md` Coverage with no `Size:` line → ERROR.
- B9 — a `wrap.md` with no `Retired:` line → ERROR.
- B10 — `check-run.py --all` on a repo where a test outside `.workflow/` opens a `.workflow/` path → WARN naming the file.
- B11 — reading `SKILL.md` → it has a Simplicity block (smallest diff, search before writing a helper, new abstraction needs two live callers) and stays at or under 180 lines.
- B12 — reading `tests.md` → it has the smallest-seam, one-concept, parametrize, no-test-imports-test, no-source-text-asserts, mutation and test-budget rules, stays near 70 lines, and "Extra tests are welcome" is gone; the execute report has a `Mutation:` line.
- B13 — reading `phase-2-plan.md` → it has Reuse findings, prefactor consolidation, the one-outcome ~25-word acceptance line and the operator risk-class table (`cheap`/`costly`/`irreversible`, cheap handoff ≤ 20 lines).
- B14 — reading `phase-4-review.md` → it has a same-run-waste P1 row, a reachability check, the verify-the-verification check, the numstat `Size:`/`Reachability:` Coverage lines and the blind-first reading order.
- B15 — reading `wrap.md` → it has a Retire step (one lettered decision, one delete commit) and the wording is "nothing is deleted from the run folder"; `THIRD-PARTY-NOTICES.md` has the MIT notice for addyosmani/agent-skills; `SKILL-IMPACT.md` has a row with the baseline numbers.

## Decisions
- D1 — one run, tickets T1–T6 and T8 from the seed plan — fits the 8-ticket cap (product call)
- D2 — new checks WARN for one release; ERROR only for B4 and B8 (and B9 once wrap adopts the step) — old runs keep passing (product call)
- D3 — thresholds are fixed in the skill: file 1,000 lines, ticket 2× budget, tests 3× code, acceptance line 40 words — one place to change (product call)
- D4 — `cheap` means reversible and under the repo's stated ceiling (named in `AGENTS.md`); no stated ceiling means `costly` — the skill stays generic (product call)
- D5 — wrap's Retire step asks once, then deletes in one commit after approval (product call)
- D6 — `check-run.py` has no tests today; T1 adds a small fixture-based test file under `scripts/tests/` (code: .github/skills/workflow/scripts/)

## Test seams
- `check-run.py` run on fixture run folders in a temp git repo — observes B1–B10 (new)
- `grep` and `wc -l` on the skill docs — observes B11–B15 (existing)

## Out of scope
- T7, exam slop cases — live in the private `j-skills-evals` repo and cannot get this run's review; separate run
- R8, cx-intelligence cleanup runs (`delete-dead-trees`, `governed-run-module`) — product runs in another repo
- Personas, `/ship`, CI/CD, observability, the sdd-cache and simplify-ignore hooks from agent-skills — not the slop problem
- Per-repo threshold overrides in `AGENTS.md` — add later if a repo needs them

Docs read: none in scope (PRODUCT.md and DESIGN.md absent)
