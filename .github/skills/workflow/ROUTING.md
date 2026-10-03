# ROUTING — current personal mapping (edit me)

The **only** skill file the card reads for models. `SKILL.md` and `references/` speak in seats; this
file maps seats onto *my current* models. Fork the skill, rewrite this file for yours, and nothing
else changes. Trial protocol, upkeep loop and mode notes live in `ROUTING-NOTES.md` (only `checkup` reads it). Only the human edits either file.

Last verified: 2026-09-30 — picker IDs `gpt-6.1-sol`, `gpt-6-sol`, `claude-opus-5.5`,
`claude-sonnet-5.5` confirmed.

## Vendors and models

| Vendor | Models in use | Effort scale |
|---|---|---|
| OpenAI | GPT-6.1 Sol — the coding workhorse (cache read about half the price of the other models); GPT-6 Sol as fallback | `medium / high / xhigh` |
| Anthropic | Claude Opus 5.5, Claude Sonnet 5.5 (stronger, pricier — judgement and dialogue seats; Sonnet 5.5 is also the cross-vendor fallback) | `medium / high / xhigh` |

Only these models are in use — none other is a primary, trial or fallback. Effort runs `medium`
to `xhigh` (`medium`/`high` are the best value; `xhigh` only where a row names it).

Vendor split: Anthropic fills the dialogue and judgement seats (brainstorm, plan, review, wrap);
OpenAI fills the writing seats (execute) — that is what makes review cross-vendor. The invariant
is the *split*, not the direction.

## Seat mapping

| Seat | Primary (vendor · model · effort) | Trial (vendor · model · effort, or —) | Fallback chain |
|---|---|---|---|
| Brainstorm partner | Anthropic · Sonnet 5.5 · high | — | OpenAI · GPT-6 Sol · high |
| Default executor | OpenAI · GPT-6.1 Sol · per phase table | — | GPT-6 Sol · same effort; then Anthropic · Sonnet 5.5 (breaks the vendor split — reviewer must then be OpenAI, degraded) |
| Heavy executor | OpenAI · GPT-6.1 Sol · xhigh (P0 fixes: high) | — | GPT-6 Sol · xhigh; then Anthropic · Sonnet 5.5 · xhigh (same caveat) |
| Mechanical lane | OpenAI · GPT-6.1 Sol · medium | — | GPT-6 Sol · medium; then Anthropic · Sonnet 5.5 · medium |
| Strict reviewer | Anthropic · Opus 5.5 · high (review: xhigh) | — | Sonnet 5.5 · xhigh; then OpenAI · GPT-6 Sol · xhigh (degraded: same-vendor review — note it in `review.md`) |

**Trial column:** a trial entry prints on the card's model line marked `(trial)`, with the primary as
fallback. One trial per seat, at most two seats at once.

## Phase → seat · effort · approval

| Phase / work | Seat | Effort | Context | Approval |
|---|---|---|---|---|
| Brainstorm (grill → brief) | Brainstorm partner | high | standard | — (dialogue; human confirms behaviours) |
| Plan (audit → tickets) | Strict reviewer | high; xhigh hardest cases | large | human approves the ticket list |
| Execute — mechanical ticket | Mechanical lane | medium | standard | auto |
| Execute — logic ticket | Default executor | high | standard | review each ticket's diff |
| Execute — contract ticket (schema/SQL/API) | Heavy executor | xhigh | standard; large if the ticket spans many files | review each ticket's diff |
| Execute — operator ticket (live/irreversible) | Default executor prepares the handoff (Heavy executor if it carries SQL or a contract) | high | standard | the human runs it, or approves the exact scope and the agent runs it; review the handoff before running |
| Review | Strict reviewer | xhigh | large | — (read-only) |
| Patch plan (fix tickets) | Strict reviewer | high | standard | — |
| Fix ticket — P0 | Heavy executor | high | standard | review each ticket's diff |
| Fix ticket — P1 (or a P2/P3 the human chose to fix), logic lane | Default executor | medium | standard | auto |
| Fix ticket — any severity, contract lane | Heavy executor | high | standard | review each ticket's diff |
| Final check & wrap-up | Brainstorm partner | medium | standard | auto |
| TODO intake (`workflow todo`) | Brainstorm partner | medium | standard | auto (writes only `TODO.md`) |
| Bootstrap (`workflow bootstrap`) | Brainstorm partner (docs) + Strict reviewer (audit) | high | large | propose each doc, confirm before writing |
| Realign (`workflow realign`) | Strict reviewer | high | large | human approval per candidate before canonical-doc write |

`standard` context = the model's default; `large` = the biggest the picker offers, used only where the
seat holds the whole repo or a wide diff (plan, review, bootstrap).

**Single-vendor sessions** (only one vendor available today): OpenAI only — GPT-6.1 Sol for every
seat, effort per the phase table (degraded same-vendor review).
Anthropic only — Sonnet 5.5 for brainstorm and execute (effort scaled the way the
mechanical→default→heavy lanes would), Opus 5.5 for plan and review (degraded same-vendor review). Either way, note the degradation in `review.md`.

**Modes:** wrap follows review in the same session — drop Opus 5.5 → Sonnet 5.5. Every execute lane
is GPT-6.1 Sol and only effort changes, so tickets of different lanes can share a session. Open the
model picker at session start; a missing model falls to the next in its row's fallback chain, and
nothing outside *Vendors and models* is a fallback.
