Command: workflow brainstorm run-sizing
Created: 2026-10-10
Base:    0ba7236
Inputs:  none
Status: done

Seed: notes/proposal.md (changes C1–C5, copied from the session that wrote it).

## Problem
A workflow run takes days of sessions to ship a few hundred lines: tickets are tiny, each one
needs a fresh session the human starts, and review cycles add more. Quality is fine; throughput
and human attention are the cost.

## Outcome
The next run's `workflow plan` writes 2–5 tickets of ~50–300 lines, `check-run.py` warns on a
plan of tiny tickets and errors on an unapproved third review cycle, and `workflow execute` runs up
to 3 same-effort tickets per session. Surfaces: `check-run.py` output and the skill's references.

## Behaviours
- B1 — plan.md with 4 logic tickets, code Budgets +20 +30 +30 +50 → check-run WARNs `median code Budget 30 … merge`
- B2 — plan.md with 4 logic tickets, code Budgets +60 +80 +80 +120 → no median warning
- B3 — any slop-gated plan.md with logic or contract tickets → check-run prints a note `median code Budget <n> over <k> tickets`
- B4 — a ticket with 6 acceptance lines → no acceptance-count ERROR; 7 lines → ERROR naming `1-6`
- B5 — review.md created on/after the sizing date with `## Cycle 3 findings` and no `Cycle 3 approved by human:` line → ERROR
- B6 — the same review.md plus `Cycle 3 approved by human: <when>` → no cycle ERROR
- B7 — the same review.md created before the sizing date → no cycle ERROR
- B8 — `grep` phase-2-plan.md §3 → a **Right-sized** bullet (merge under ~40 code lines, 2–5 tickets, 8 a ceiling) and Testable's relation rule are present; "five minutes" count 0
- B9 — `grep` phase-3-execute.md → step 6 carries on at same model and effort, stops at 3 tickets, a failed Verify, or a UI/operator ticket, writes `Session N: T#, T#`; the Finding stop fires only when operator spend or a target depends on it
- B10 — `grep` phase-4-review.md → one fix ticket with two commits and a `Red: <sha>` line; **Cycle bound — two** sends every open fix-now to the human, P0 escalates; MAINTAINING.md says two cycles
- B11 — `grep` ROUTING.md:58 and README.md's execute row → both describe multi-ticket sessions; learning-worklog.md, wrap.md and checkup's `Run:` line → each carries `sessions`
- B12 — `grep` SKILL-IMPACT.md → a run-sizing row with the proposal's judge measures and the C5 loosening note; the slop-guards row judges lines per behaviour and net product lines per run

## Decisions
- D1 — A multi-ticket execute session stops after at most 3 tickets, plus C2's stops (failed Verify, UI or operator ticket next) — the agent cannot read the context meter; a count is checkable (product call)
- D2 — Execute carries on only while the next ticket's card names the same model and effort; a change stops with `Reset: yes` — effort cannot change mid-session without the human (code: ROUTING.md Modes)
- D3 — This run edits ROUTING.md line 58 (the one-ticket-per-session sentence) to match; approved by the human here (product call)
- D4 — Execute writes one `Session N: T#, T#` line into `## Execution state` per session; wrap adds `sessions` to the WORKLOG `Run:` line — reset cards live only in chat (code: learning-worklog.md Run: shape)
- D5 — slop-guards' SKILL-IMPACT judge changes from "lines per ticket fall" to lines per behaviour and net product lines per run, noted in its row — C1 raises lines per ticket on purpose (product call)
- D6 — The cycle-3 check applies only to review.md files created on or after a new date constant, like `SLOP_SINCE` — done runs with 3+ cycles must not start erroring (code: check-run.py SLOP_SINCE)
- D7 — `ACCEPT_MAX` in check-run.py goes from 4 to 6 to match C1 (code: check-run.py:49)
- D8 — check-run computes and prints the median code Budget; no `Tickets: · median` template line — one less line to keep right (product call)
- D9 — A bug fix ticket records its red commit as a `Red: <sha>` line; review diffs tests from it to the fix; check-run does not enforce it — it can't tell bug tickets apart (product call)
- D10 — After cycle 2, every open fix-now finding goes to the human as one decision (a one more cycle · b defer to TODO.md); a P0 always escalates (product call)
- D11 — The 2026-10-08 execute-rules row stays `trialing`; the new row notes that C5 loosens its rule (1) (product call)
- D12 — The merge warning counts logic and contract tickets only, the lanes that carry a Budget (code: check-run.py:305)

## Test seams
- `check-run.py` run as a subprocess by `scripts/tests/test_check_run.py` — observes B1–B7 (existing)
- Doc content by `grep -c <phrase> <file>` — observes B8–B12 (existing, mechanical)

## Out of scope
- The proposal's "right now" advice for A3 in cx-intelligence — another repo; the human can tell its executor today
- Cross-vendor review, red before green, operator Risk classes, receipts, the slop-guards checks — unchanged by the proposal
- A context-meter stop — the agent can't read the meter (D1)
- check-run enforcing `Red:` lines (D9) and auto-merging tickets (warn only)
- Changing `MAX_TICKETS` — 8 stays as the ceiling

Docs read: none in scope (no PRODUCT.md or DESIGN.md; ROADMAP.md — no planned work; no TODO.md)
