Command: workflow brainstorm next-step
Created: 2026-10-29 · Sonnet 5.5
Base:    62e8c26
Inputs:  none
Status:  done

## Problem
The "what is next" answer is read by the model from the SKILL.md state table and copied from ROUTING.md rows, so two models can print two cards, and an orchestrator cannot read the card at all. TODO.md P1 checkup-next-actions C1-1 asks for a script to print the card's Model and Fallback lines.

## Outcome
`python3 skills/workflow/scripts/next-step.py <slug> --json` prints one JSON object for the run's next step. The closing card, `workflow next` and each `workflow status` line are that output, not text the model writes.

## Behaviours
- B1 — a run with only `brainstorm.md` → `phase: "plan"`, `command: "workflow plan <slug>"`, seat Strict reviewer, Anthropic · Opus 5.5 · high, context large, the ROUTING.md fallback chain, `reset: true`, `blocker: null`.
- B2 — a plan whose first ready ticket is `T2` with `Lane: contract` → `phase: "execute"`, `ticket: "T2"`, seat Heavy executor, OpenAI · GPT-6.1 Sol · xhigh, `approval: "auto"`.
- B3 — a plan whose only unfinished ticket is `awaiting-human` → `blocker` names that ticket and its action (the handoff path in `receipts/`), `model` is null, and `command` is still `workflow execute <slug>`.
- B4 — every ticket done, and no `review.md` or code changed since its `Base` → `phase: "review"`, Strict reviewer, Opus 5.5 · xhigh, context large.
- B5 — `patch_plan.md` with a `P0` fix ticket not done → `phase: "execute"`, that ticket id, Heavy executor, GPT-6.1 Sol · high; a P1 logic fix → Default executor · medium.
- B6 — `review.md` with no open finding and no code change since its `Base` → `phase: "wrap"`, Brainstorm partner, Sonnet 5.5 · medium.
- B7 — any run → the JSON carries `schema_version: 1` and a `card` string, and the closing card, `workflow next` and `workflow status` print that string or its fields unchanged, and a trial model prints marked `(trial)` with the primary as fallback.
- B8 — a ROUTING.md row that does not parse, or a key the run needs that has no row → exit 1 with the row or key named on stderr, and no JSON on stdout.

## Decisions
- D1 — a new sibling `scripts/next-step.py` that loads `check-run.py` with `importlib` and reuses its ticket, header and review parsers; `check-run.py` stays a validator — a different job and exit-code meaning (code: scripts/check-run.py:255, :526).
- D2 — ROUTING.md's seat table and phase table become strictly parseable: separate vendor, model and effort columns, `;`-separated fallback chain, and a key column on the phase table (`execute:logic`, `fix:P0`); a test fails when any row does not parse — one human-edited source, no prose parsing (product call).
- D3 — the script renders the whole card (Why, Reset, Model, Fallback, Reads, Run) into the `card` field; the model writes only the Result and Decisions above it (product call).
- D4 — no version bump in this run; the JSON's `schema_version` is the contract, and 3.0.0 ships with `unattended-mode` (product call).
- D5 — extra fields beyond the human's list: `approval`, `context`, `trial`, `reads` (product call).
- D6 — the JSON is consumer-neutral: j-skills names no orchestrator, bot or agent, so any assistant that reads the JSON (a conductor skill, a chat bot, another agent runtime) gets the same answer; model names stay as ROUTING.md writes them and mapping to a harness's IDs belongs to the consumer (product call).
- D7 — the awaiting-human action is the handoff path the ticket's execute step already writes into `receipts/` plus the ticket title; no new ticket field (code: references/phase-3-execute.md:80).
- D8 — the script reports ROUTING.md's configured primary and chain only; seat availability, single-vendor degradation and model switching are the consumer's job (product call).

## Test seams
- `next-step.py <slug> --json` stdout and exit code, plus the `card` string — observes B1–B8 (new), tested in `scripts/tests/` against fixture run folders in a temp git repo, like `test_check_run.py`.

## Trust boundaries
- Run-folder text (ticket titles, handoff paths) → a consumer that may act on the JSON; the script copies it as data in string fields and never as a command, and the only command it emits is `workflow <phase> <slug>`.

## Out of scope
- unattended mode, autopilot, `decisions.md` — the next run, `unattended-mode`.
- the conductor skill and any consumer — separate repo, built later.
- a decision model for judgement calls (Jev, Decision-1) — later.
- mapping model names to harness IDs — the consumer's job (D6).
- PRs — no PR work in this run.
- the version bump to 3.0.0 — D4.

Docs read: none in scope
