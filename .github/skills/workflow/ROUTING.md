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

| Seat | Vendor | Model | Trial | Fallback chain | Notes |
|---|---|---|---|---|---|
| Brainstorm partner | Anthropic | Sonnet 5.5 | — | OpenAI · GPT-6 Sol · high | |
| Default executor | OpenAI | GPT-6.1 Sol | — | OpenAI · GPT-6 Sol; Anthropic · Sonnet 5.5 | Cross-vendor fallback requires an OpenAI reviewer; note degradation |
| Heavy executor | OpenAI | GPT-6.1 Sol | — | OpenAI · GPT-6 Sol · xhigh; Anthropic · Sonnet 5.5 · xhigh | Same reviewer caveat |
| Mechanical lane | OpenAI | GPT-6.1 Sol | — | OpenAI · GPT-6 Sol; Anthropic · Sonnet 5.5 | |
| Strict reviewer | Anthropic | Opus 5.5 | — | Anthropic · Sonnet 5.5 · xhigh; OpenAI · GPT-6 Sol · xhigh | Same-vendor fallback is degraded; record it in review.md |

**Format:** Trial is `Vendor · Model` with an optional `· effort`, or `—`. Fallback chain uses
the same entries separated by `;`. An omitted effort uses the phase row's effort. A trial prints
`(trial)` on the Model line and puts the primary first in the fallback chain. One trial per seat,
at most two seats at once. Only Notes cells may be empty.

## Phase → seat · effort · approval

| Key | Phase / work | Seat | Effort | Context | Approval | Notes |
|---|---|---|---|---|---|---|
| brainstorm | Brainstorm | Brainstorm partner | high | standard | human | Confirm behaviours |
| plan | Plan | Strict reviewer | high | large | human | Approve tickets; xhigh for hardest cases |
| execute:mechanical | Execute mechanical | Mechanical lane | medium | standard | auto | |
| execute:logic | Execute logic | Default executor | high | standard | auto | |
| execute:contract | Execute contract | Heavy executor | xhigh | standard | auto | Large context for wide changes |
| execute:operator | Execute operator | Default executor | high | standard | human | Prepare handoff; Heavy executor for SQL or contracts; review before running |
| review | Review | Strict reviewer | xhigh | large | auto | Read-only |
| patch-plan | Patch plan | Strict reviewer | high | standard | auto | |
| fix:P0 | Fix P0 | Heavy executor | high | standard | auto | |
| fix:logic | Fix P1, or chosen P2/P3, logic | Default executor | medium | standard | auto | |
| fix:contract | Fix contract | Heavy executor | high | standard | auto | |
| fix:mechanical | Fix mechanical | Mechanical lane | medium | standard | auto | |
| fix:operator | Fix operator | Default executor | high | standard | human | Same handoff rules as execute:operator |
| wrap | Final check and wrap | Brainstorm partner | medium | standard | auto | |
| todo | TODO intake | Brainstorm partner | medium | standard | auto | Writes only TODO.md |
| bootstrap | Bootstrap | Brainstorm partner | high | large | human | Strict reviewer audits; confirm each doc before writing |
| realign | Realign | Strict reviewer | high | large | human | Approve each canonical-doc change |

UI tickets use their lane's row; the human tries the result and approves before the commit.
`auto` = no human step. Execute runs up to 3 tickets per session at the same model and effort,
then stops so the human can reset; it also stops before a UI ticket's commit
(`references/phase-3-execute.md`).

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
