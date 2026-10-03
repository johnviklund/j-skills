# ROUTING-NOTES — trial protocol, upkeep and mode notes

Read by `checkup` only — not by the phases or wrap. `ROUTING.md` holds the mapping itself
and is the only file the closing card needs; like it, this file may name models.

**History.** The 2026-09-30 seat change (GPT-6.1 Sol on every execute lane, Opus 5.5 on plan and
review, Sonnet 5.5 on brainstorm and wrap) was a direct promotion by the human, without trial
runs; the strict reviewer's `evals.run reviewer` for Opus 5.5 is still owed.

**How a model earns a seat — trial runs.** Put the candidate in the seat for one or two real
runs; the worklog's `Run:` and `Seats:` lines (tickets, review cycles, deviations, findings
overturned, model per seat) are the evidence, and `checkup` compares them against the
incumbent's last runs on that seat. Promote when the candidate ties or beats on cycles and
deviations at lower cost or effort; demote when it doesn't. The one exception is the strict
reviewer: before a candidate takes that seat, run `evals.run reviewer` — a recall check on ≤8
diffs with known P0/P1s — because a reviewer miss is the expensive kind. No other seat is examined.

**The CLI is not part of the mapping.** Some environments expose one CLI that serves both vendors;
others need one CLI per vendor. Either way this file is the same: pick the model, and use
whatever CLI serves it. The literal commands for *reset*, *compact*, *context meter* and *model
picker* are the CLI's own — `README.md` keeps a per-CLI cheat sheet.

**Trial column.** When a seat has a trial entry, the closing card prints the trial model on its model
line, marked `(trial)`, and the primary as the fallback; the worklog's `Seats:` line records what
actually ran. Clear it after promoting or rejecting. One trial per seat, at most two seats in trial at
once — otherwise a bad run can't be attributed.

## Maintaining this file

Nothing edits this file but the human; wrap writes evidence, checkup recommends. The loop:

1. **New model released** → add it to *Vendors and models*, confirm its ID and the effort levels in
   the picker, then put it in one seat's *Trial* column (for the strict reviewer, run
   `evals.run reviewer` first). Effort: start at the incumbent's, try one level lower on the second run (never below `medium`).
2. **Run one or two real runs** → wrap records `Run:`/`Seats:`.
3. **`checkup seats`** → prints the per-seat table and says promote / reject / need another run.
4. **Edit here** → promote to *Primary* (old primary becomes first fallback) or reject; clear *Trial*;
   bump *Last verified*. Effort and context columns change only on evidence from step 3 — never
   because a new model "should" need less.
5. **Stale check** → `checkup` flags *Last verified* older than 90 days; re-open the picker and
   confirm every model ID still exists, because deprecations are silent.

**Context window:** `standard` = the model's default (256K-class); `large` = the biggest the picker
offers (1M-class). Large only where the seat must hold the whole repo or a wide diff at once —
plan, review, bootstrap. Execution runs one ticket at a time and does not
benefit; dialogue seats don't either. Large costs more per call and dilutes attention on small
inputs, so it is a per-seat setting, not a default.

## Model and mode notes

- **Read-only breadth.** Where the CLI serving a read-only seat offers a fan-out / sub-agent /
  "ultra"-style breadth mode, it is sanctioned only per `SKILL.md`'s read-only-breadth invariant
  (plan and review, wide problems only). It multiplies token burn — default to the seat's normal effort
  unless breadth is the bottleneck.
- **Autonomy loops** (a mode that drives a whole plan without re-prompting each step) and **speed
  modes** (reduced reasoning): default No. An autonomy loop only when explicitly asked, and
  UI and operator tickets still stop for the human inside it. A speed mode only on mechanical
  rows, never logic/contract tickets, plan or review.
- **Wrap in practice:** wrap usually follows review on the Anthropic side — drop Opus 5.5 → Sonnet 5.5
  in the same session after the review verdict.
- **One executor model:** every execute lane runs GPT-6.1 Sol and only the effort changes, so
  consecutive tickets of different lanes can continue in one session — change the effort, not the model.
- **Availability:** open the model picker at session start; models are plan/policy/region/rollout
  dependent. Missing Opus 5.5 → Sonnet 5.5 `xhigh` for the plan and reviewer seat; missing
  Sonnet 5.5 → GPT-6 Sol for brainstorm and wrap; missing GPT-6.1 Sol → GPT-6 Sol at the same
  effort. Nothing outside *Vendors and models* is a fallback.
- **Single-vendor sessions** are the paragraph in `ROUTING.md`; note the degradation in `review.md`.
