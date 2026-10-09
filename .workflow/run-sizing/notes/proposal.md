# Proposal: right-size workflow runs (ticket size, sessions, review cycles)

Date: 2026-10-09 · For: j-skills `workflow` skill · Status: proposed (not applied)
Run it as a j-skills run like `slop-guards`: `workflow brainstorm run-sizing` with this file as input.

## Problem
Runs are slow because the cost of each ticket is fixed and the tickets are tiny. A run takes days
of sessions to ship a few hundred lines. The code quality is fine; the problem is throughput and
how much human attention the process needs.

Evidence (cx-intelligence):
| Run | Tickets | Code budget | Sessions (approx.) | Notes |
|---|---|---|---|---|
| governed-execution-migration (A3) | 6 logic + 1 operator | +197 code, +290 tests in total, about 33 code lines per ticket (+10 … +55) | 7 + review + wrap | a re-plan after T2 because a 10-digit dollar literal moved when the retry count went from 3 to 6 |
| governed-execution (A2) | 8 + 12 patch tickets | — | about 20 ticket sessions | 4 review cycles even though the limit is 3 |
| self-service-gaps + 3 follow-up runs | about 22 tickets | — | — | one ROADMAP step |

Causes in the skill text:
1. `phase-2-plan.md` §3 **Small**: "a diff a reviewer can read in about five minutes, one fresh
   session to build". Nothing sets a minimum size, and the limit of 8 tickets gets treated as a target.
2. `phase-3-execute.md` loop step 6: every logic, contract and patch ticket "ends the turn with
   the closing card, `Reset: yes` … one ticket per session". The human has to start every ticket.
3. `phase-4-review.md` After the verdict: "A behavioural bug is two tickets", so each bug doubles
   the patch tickets.
4. `phase-4-review.md` limits review to three cycles, but the limit isn't enforced (A2 ran 4).
5. `phase-2-plan.md` §3 **Testable** asks for exact values, so computed numbers (cost, ratio)
   become long decimals. A changed constant then triggers a stop and a re-plan (`phase-3-execute.md`).

## Changes
C1. Tickets have a minimum size (`phase-2-plan.md` §3)
  Replace the **Small** bullet with:
  "**Right-sized.** One seam or one module, 1–6 acceptance lines, roughly 50–300 changed lines
  (code plus tests). If a ticket's Budget is under about 40 code lines, merge it with the next
  ticket in the same module and lane, unless other tickets are blocked on it as a prefactor. Most
  runs need 2–5 tickets; 8 is a ceiling, not a target."
  In §4 the merge option stays; also add to the plan template: "Tickets: <n> · median code Budget <n>".
  `check-run.py`: WARN when a plan has 4 or more logic or contract tickets and their median code
  Budget is under 40.

C2. Several tickets per session (`phase-3-execute.md` step 6)
  Replace "Every other ticket … one ticket per session" with:
  "Logic and contract tickets carry straight on to the next ready ticket **of the same lane** in
  the same session. Stop with `Reset: yes` when the context meter passes about 50%, when a
  `Verify` fails, when the next ticket's lane needs a different seat, or when the next ticket is a
  UI or operator ticket. Each ticket still commits, reports and updates `## Execution state` before
  the next one starts, so a reset loses nothing."
  The rule that a mechanical ticket rolls into the next mechanical ticket becomes part of this rule.

C3. A bug fix is one ticket with two commits (`phase-4-review.md` After the verdict)
  Replace "A behavioural bug is two tickets: …" with:
  "A behavioural bug is one fix ticket with two commits: first a test that reproduces it, run and
  seen to fail, committed alone; then the fix, which leaves every test file untouched."
  C2 applies to patch plans too: all fix tickets in one cycle that share a lane run in one session.

C4. Review cycles are capped at two, and the cap is enforced (`phase-4-review.md`, `check-run.py`)
  "**Cycle bound — two.** After cycle 2, an open P1 goes to the human as one decision:
  a) one more cycle · b) defer to `TODO.md` ➡️ when it breaks no B# and not the Outcome.
  A P0 always escalates." `check-run.py`: ERROR on a `## Cycle 3 findings` section unless a
  `Cycle 3 approved by human:` line is present. Update `MAINTAINING.md`'s "at most three cycles" to match.

C5. Computed numbers are checked as relations (`phase-2-plan.md` §3 Testable, `phase-3-execute.md`)
  Add to **Testable**: "A computed value (cost, ratio, duration, estimate) is checked as a relation
  to its inputs or to a named constant (`worst_case == 2 × three-attempt basis`,
  `== TRANSPORT_ATTEMPTS × …`), not as a long decimal."
  In execute, narrow the stop rule: "A deviation that changes a number a Finding rests on stops
  the run **when an operator ticket's spend or a target depends on it**. Otherwise update the
  Finding in place, log a `## Deviations` line and continue."

## Not changed
Cross-vendor review, test first (red before green), the operator risk classes, the receipts,
and every `slop-guards` check.

## Interaction with the slop-guards trial
- `slop-guards` is still in its 3-run trial, and one of its judging measures is "lines per ticket
  fall". C1 deliberately **raises** lines per ticket. Before both are trialled, change that measure
  to **lines per behaviour (B#)** and **net product lines per run**. Otherwise C1 will look like a
  regression of `slop-guards`.
- Log this as its own `SKILL-IMPACT.md` row. The two changes target different things (`slop-guards`:
  code volume; this one: throughput), so both can be judged on the same next 3 runs if the measures
  are kept apart.

## Judge (next 3 runs)
Baseline: A3 has 7 tickets with a median of about 33 code lines; A2 needed about 20 ticket sessions over 4 review cycles.
- median code Budget per ticket of at least 80 · at most 5 tickets per run · at most 2 review cycles
- sessions per run (count the `Reset: yes` cards) at least halved
- elapsed time from first plan commit to wrap commit (git timestamps) falls
- review P0/P1 per run does not rise; `slop-guards`' test-to-code ratio does not rise

## Right now, without changing the skill (A3, T3–T7 left)
Tell the executor: "Run T3–T6 in an autonomy loop; stop only for T7 or a failed Verify."
(`phase-3-execute.md` allows an autonomy loop when the human asks for it.) Or approve merging
T3 + T4 and T5 + T6.
