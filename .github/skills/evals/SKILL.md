---
name: evals
description: >
  A recall check for strict-reviewer candidates, run only before swapping that seat: "evals.run
  reviewer [vendor model effort]" shows the candidate each diff in evals/strict-reviewer/ (at
  most 10) and records which planted P0/P1 findings it named; "evals.list" shows the set's
  status. No other seat is examined — models earn every other seat on trial runs recorded in
  WORKLOG.md. Trigger only on explicit "evals.run ..." or "evals.list" invocations, never on
  casual mentions of evals or testing. Never edits the workflow skill or product code.
---

# evals

One exam, one seat. `workflow` deposits a case at wrap only when a reviewer or writer *missed* a
P0/P1 (`evals/strict-reviewer/code-review-*.md`, cap 10). Every other seat — brainstorm, plan,
execution lanes — is judged on trial runs: the worklog's `Run:`/`Seats:` lines, compared by
`checkup`. This skill exists because a reviewer miss is the expensive kind, and a diff with known
findings is a cheap, honest exam of exactly that.

Run it before giving a new model the strict-reviewer seat, and not otherwise. The human invokes it.

## Commands

- `evals.run reviewer [<vendor> <model> <effort>]` — ask for the candidate if not given.
- `evals.list` — read-only: cases present (≤10), any that are not self-contained, last exam result.

## Procedure — `evals.run reviewer`

**1. Preflight.** Load `evals/strict-reviewer/*.md`; a case must carry the diff itself and the
P0/P1 lines a pass must name — skip and flag any that don't, never fail the run on one. State the
bill: N cases × one candidate call at the reviewer's review effort, no grader model. Confirm with
the human. Fewer than 3 usable cases: say the exam is not meaningful and stop.

**2. Run the candidate — one case, fresh context each.** Give the candidate the diff with the
The review instructions from the `workflow` skill (`references/phase-4-review.md`), at the seat's review effort, and never the
findings. Capture its findings list verbatim, plus tokens/latency where the CLI reports them. One
retry on a mechanical failure; a second failure scores the case as missed.

**3. Score by recall — no grader model.** Per case, per planted P0/P1: named or not. Present the
table (case → planted finding → candidate's matching line, or "—") to the human; matching a
finding is a two-minute human read, and the human's mark is final. Total = planted findings named
÷ planted findings. Report cost and latency per case beside it.

**4. Record.** Append one block to `evals/strict-reviewer/RESULTS.md` (create if absent): date,
candidate (vendor · model · effort), recall N/M, per-case misses, cost/latency, one-line verdict.
Commit it. No scorecard directory, no routing proposal — the human edits `ROUTING.md` if the number
convinces them, and only a 100% recall on a set of ≥3 cases should.

## Ground rules

- **Writes only `evals/strict-reviewer/RESULTS.md`.** Never edits cases, the workflow skill, or code.
- **Bounded.** ≤10 cases, one seat, one candidate per invocation.
- **Provenance.** Exact model and effort, never a family name.
