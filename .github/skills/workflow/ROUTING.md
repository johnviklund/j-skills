# ROUTING — current personal mapping (edit me)

This is the **only** file in the skill that names vendors or models. `SKILL.md` and `references/`
speak in seats; this file maps those seats onto *my current* models. Fork the skill, rewrite this
file for yours, and nothing else needs to change. (Last verified: 2026-09-30 — picker IDs
`gpt-6.1-sol`, `gpt-6-sol`, `claude-opus-5.5`, `claude-sonnet-5.5` confirmed.
The 2026-09-30 seat change was a direct promotion by the human, without trial runs; the strict
reviewer's `evals.run reviewer` for Opus 5.5 is still owed.)

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

## Vendors and models

| Vendor | Models in use | Effort scale |
|---|---|---|
| OpenAI | GPT-6.1 Sol — the coding workhorse (cache read about half the price of the other models); GPT-6 Sol as fallback | `medium / high / xhigh` |
| Anthropic | Claude Opus 5.5, Claude Sonnet 5.5 (stronger, pricier — judgement and dialogue seats; Sonnet 5.5 is also the cross-vendor fallback) | `medium / high / xhigh` |

Only the models above are in use; no other model is a primary, trial or fallback. Effort runs
`medium` to `xhigh` only — `medium` and `high` are the best value for output, so `xhigh` is
reserved for the rows that name it.

Vendor split: Anthropic fills the dialogue and judgement seats (brainstorm, plan, review, wrap);
OpenAI fills the writing seats (execute). That is what makes review cross-vendor: GPT
writes, Claude audits and reviews. The invariant is the *split*, not the direction — reversed
works too.

## Seat mapping

| Seat | Primary (vendor · model · effort) | Trial (vendor · model · effort, or —) | Fallback chain |
|---|---|---|---|
| Brainstorm partner | Anthropic · Sonnet 5.5 · high | — | OpenAI · GPT-6 Sol · high |
| Default executor | OpenAI · GPT-6.1 Sol · per phase table | — | GPT-6 Sol · same effort; then Anthropic · Sonnet 5.5 (breaks the vendor split — reviewer must then be OpenAI, degraded) |
| Heavy executor | OpenAI · GPT-6.1 Sol · xhigh (P0 fixes: high) | — | GPT-6 Sol · xhigh; then Anthropic · Sonnet 5.5 · xhigh (same caveat) |
| Mechanical lane | OpenAI · GPT-6.1 Sol · medium | — | GPT-6 Sol · medium; then Anthropic · Sonnet 5.5 · medium |
| Strict reviewer | Anthropic · Opus 5.5 · high (review: xhigh) | — | Sonnet 5.5 · xhigh; then OpenAI · GPT-6 Sol · xhigh (degraded: same-vendor review — note it in `review.md`) |

**Trial column:** when a seat has a trial entry, the closing card prints the trial model on its model line,
marked `(trial)`, and the primary as the fallback; the worklog's `Seats:` line records what actually
ran. Clear it after promoting or rejecting. One trial per seat, at most two seats in trial at once —
otherwise a bad run can't be attributed.

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

## Phase → seat · effort · approval

| Phase / work | Seat | Effort | Context | Approval |
|---|---|---|---|---|
| Brainstorm (grill → brief) | Brainstorm partner | high | standard | — (dialogue; human confirms behaviours) |
| Plan (audit → tickets) | Strict reviewer | high; xhigh hardest cases | large | human approves the ticket list |
| Execute — mechanical ticket | Mechanical lane | medium | standard | auto |
| Execute — logic ticket | Default executor | high | standard | review each ticket's diff |
| Execute — contract ticket (schema/SQL/API) | Heavy executor | xhigh | standard; large if the ticket spans many files | review each ticket's diff |
| Execute — operator ticket (live/irreversible) | Default executor prepares the handoff (Heavy executor if it carries SQL or a contract) | high | standard | the human runs it; review the handoff before running |
| Review | Strict reviewer | xhigh | large | — (read-only) |
| Patch plan (fix tickets) | Strict reviewer | high | standard | — |
| Fix ticket — P0 | Heavy executor | high | standard | review each ticket's diff |
| Fix ticket — P1 (or a P2/P3 the human chose to fix), logic lane | Default executor | medium | standard | auto |
| Fix ticket — any severity, contract lane | Heavy executor | high | standard | review each ticket's diff |
| Final check & wrap-up | Brainstorm partner | medium | standard | auto |
| TODO intake (`workflow todo`) | Brainstorm partner | medium | standard | auto (writes only `TODO.md`) |
| Bootstrap (`workflow bootstrap`) | Brainstorm partner (docs) + Strict reviewer (audit) | high | large | propose each doc, confirm before writing |
| Realign (`workflow realign`) | Strict reviewer | high | large | human approval per candidate before canonical-doc write |

**Context window:** `standard` = the model's default (256K-class); `large` = the biggest the picker
offers (1M-class). Large only where the seat must hold the whole repo or a wide diff at once —
plan, review, bootstrap. Execution runs one ticket at a time and does not
benefit; dialogue seats don't either. Large costs more per call and dilutes attention on small
inputs, so it is a per-seat setting, not a default.

**Single-vendor sessions** (only one vendor available today): OpenAI only — GPT-6.1 Sol for every
seat, effort per the phase table (degraded same-vendor review).
Anthropic only — Sonnet 5.5 for brainstorm and execute (effort scaled the way the
mechanical→default→heavy lanes would), Opus 5.5 for plan and review (degraded same-vendor review). Either way, note the degradation in `review.md`.

## Model and mode notes

- **Read-only breadth.** Where the CLI serving a read-only seat offers a fan-out / sub-agent /
  "ultra"-style breadth mode, it is sanctioned only per `SKILL.md`'s read-only-breadth invariant
  (plan and review, wide problems only). It multiplies token burn — default to the seat's normal effort
  unless breadth is the bottleneck.
- **Autonomy loops** (a mode that drives a whole plan without re-prompting each step) and **speed
  modes** (reduced reasoning): default No. An autonomy loop only when explicitly asked, and
  review-each-diff stays on contract tickets even inside it. A speed mode only on mechanical
  auto-approve rows, never logic/contract tickets, plan or review.
- **Wrap in practice:** wrap usually follows review on the Anthropic side — drop Opus 5.5 → Sonnet 5.5
  in the same session after the review verdict.
- **One executor model:** every execute lane runs GPT-6.1 Sol and only the effort changes, so
  consecutive tickets of different lanes can continue in one session — change the effort, not the model.
- **Availability:** open the model picker at session start; models are plan/policy/region/rollout
  dependent. Missing Opus 5.5 → Sonnet 5.5 `xhigh` for the plan and reviewer seat; missing
  Sonnet 5.5 → GPT-6 Sol for brainstorm and wrap; missing GPT-6.1 Sol → GPT-6 Sol at the same
  effort. Nothing outside *Vendors and models* is a fallback.
