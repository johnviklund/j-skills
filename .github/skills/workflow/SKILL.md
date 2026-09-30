---
name: workflow
description: >
  Personal solo-dev coding workflow, run only on an explicit "workflow <command>" or
  "/workflow <command>" message; never on casual mentions of brainstorm, plan, execute, review
  or learn elsewhere in a message. Commands: brainstorm, improve, plan, execute, review, park,
  wrap, status, next, learn, log, todo, bootstrap, realign; bare "workflow" = next.
---

# Workflow

> ⚠️ Invoke this skill first; the references are read through it, never on their own.

Four phases and a wrap: **brainstorm → plan → execute → review → wrap**. Each phase is a **seat**
(a job with an output contract) filled by whatever model currently earns it. Writer and reviewer
sit with different vendors on purpose — independence is the point. `ROUTING.md` maps seats to
vendors, models and efforts and is the only file that names them; which CLI serves a model is not
this skill's concern.

**Invocation:** `workflow <command> [slug]`; if the CLI swallows the slash, drop it, and where the
CLI invokes skills with its own prefix, send the card's line with that prefix. Only a message
that starts with `workflow` invokes the skill.

## The run — `.workflow/<slug>/`

One run = one folder, tracked in git, kept forever. The files are the state machine: any fresh
session picks the run up from its files alone.

| Artifact | Written by | Holds |
|---|---|---|
| `brainstorm.md` | brainstorm | the **brief**: problem, behaviours (B#), decisions, test seams, out of scope — status of record for the run |
| `plan.md` | plan, then execute | findings + **tickets** (T#), each with acceptance lines and a verify command; execution state |
| `patch_plan.md` | review | fix tickets for the current patch cycle |
| `review.md` | review | coverage, findings per cycle, verdicts |
| `learnings.md`, `wrap.md` | any / wrap | tagged lessons; wrap's own checkpoint |

Every artifact header carries `Status:` — `drafting` · `complete` · `parked` · `done`.
**`drafting` means resume that phase.** A run whose `brainstorm.md` is `parked` or `done` is not live.

| State of a live run | Next |
|---|---|
| `brainstorm.md` only | plan |
| `plan.md` with a ticket `awaiting-human` and none other ready | the human's action named in that ticket, then execute |
| `plan.md` with a ticket not `done` | execute |
| every ticket done; no `review.md`, or code changed since its `Base` | review |
| `patch_plan.md` with a ticket not `done` | execute (runs the patch plan) |
| `review.md` with no open finding and no code change since its `Base` | wrap |

**Slug:** the command names one, or exactly one run is live — otherwise list the live runs,
lettered, and ask. Live runs: `grep -l 'Status: \(drafting\|complete\)' .workflow/*/brainstorm.md`.
`workflow status` prints one line per non-done run — `slug · phase · blocker or none · next command`;
an `awaiting-human` ticket is the blocker, named with the action it waits on.
A command that doesn't fit the run's state (e.g. `execute` with no `plan.md`) gets named and asked
about. `workflow spec` was retired in v2.1: say so and route to `workflow plan <slug>`.

**Grounding** reads the run folder, `ROUTING.md`, `AGENTS.md`, `MEMORY.md` (index of `memory/`),
`PRODUCT.md`/`DESIGN.md` when product or UI is in scope, repo-root `TODO.md` and `ROADMAP.md`
when the phase says so, `git log --oneline -15`, `git status`.

## Talking to the human (every phase)

**The artifact is the record; chat is the receipt.** The human runs many projects and reads on a
phone. Above the closing card, a phase prints at most ~12 lines:

- **Result** — what the phase did, ≤3 plain lines.
- **Decisions needed** — a numbered list; each item is one decision in plain words, options
  lettered on their own lines, a ➡️ recommended default, so "all defaults except 2b" answers it.
  Every question in every phase uses this shape.
- A negative result is one line ("`PRODUCT.md` — no changes").

**Clarify gate** (every phase except brainstorm, which is all questions): before the first edit,
if something material is unclear or a misread is expensive — ambiguous scope, a command/state
mismatch, schema/contract/deletion work, a silent assumption doing heavy lifting — ask one round
of ≤3 questions and wait. Mechanical, clearly specified work proceeds.

**Budgets** — thinking is unbounded, files are not: `brainstorm.md` ≤ ~80 lines and ≤ 15
behaviours; `plan.md` ≤ ~120 lines and ≤ 8 tickets. Over budget = the run is two runs: propose
the split and ask. Meet a budget by cutting prose, never acceptance lines or checks.

## Seats

| Seat | Job | Used by |
|---|---|---|
| Brainstorm partner | the grill: dialogue that ends in a planning-ready brief | brainstorm, todo, wrap |
| Default executor | logic tickets; best quality per cost | execute (logic), P1–P3 fixes |
| Heavy executor | schema/SQL/contract tickets, hardest multi-file work | execute (contract), P0 fixes |
| Mechanical lane | tickets with an explicit expected text result | execute (mechanical) |
| Operator (the human) | runs what the agent must not: live or irreversible writes, authorizations, hosted consoles | execute (operator tickets) |
| Strict reviewer | the skeptic; read-only except `realign` | plan, review, patch plans, realign |

Invariants:

- **Cross-vendor review.** The strict reviewer is a different vendor from the code's writer; a
  same-vendor review is degraded and says so in `review.md`. One step runs in one session only.
- **Availability first.** Open the model picker at session start and walk `ROUTING.md`'s fallback
  chain in order; name any switch.
- **Effort follows risk.** Before raising effort on a struggling ticket, sharpen its acceptance
  lines — a clearer bar beats more thinking.
- **Approval follows blast radius** (map in `ROUTING.md`): read-only none, mechanical auto, logic
  and contract tickets shown to the human ticket by ticket, operator tickets executed by the human.
  The lane sets the seat and approval for fix tickets too — a fix that touches a contract is a
  contract ticket whatever its severity.
- **Sub-agents do read-only breadth**: fact-finding in brainstorm and plan, wide diffs in review.
  Their findings are verified before use. Anything that writes runs in the main session.

## Context hygiene

Every phase starts in a fresh context, re-grounded from the run folder and git; the handoff is
where the model swap happens. Artifacts are written as the phase goes, so a mid-phase **reset**
costs only warm cache — prefer it to compaction. This skill names verbs (*reset*, *compact*,
*context meter*, *model picker*); each CLI's literal commands are in `README.md`.

## The closing card — `workflow next`

Every phase ends with this card as the last output of the turn — inside the CLI's summary tool if
it has one. Open `ROUTING.md` in the closing turn and fill the model line with real values (a
*Trial* entry prints instead of the primary, marked `(trial)`); the card exists so the human never
opens a file to pick a model.

---
**▶ Next: <phase>** · <run slug> · <one-line why, or the cycle and finding ids for a patch cycle>
**Reset:** yes | no · **Model:** <vendor> · <model> · <effort> · <context> — fallback <model> <effort>
**Reads:** <files the next phase opens first>
```text
workflow <phase> <slug>
```
---

Reset is `yes` at every handoff, `no` only for same-seat work continuing. When the next step is the
human's — an operator ticket or an escalation — the model line reads `**Model:** human — <the one
action>` and **Reads:** names the handoff. When the run is done,
print the ✅ card instead: what shipped (one line); product-doc truth (edited what, or none);
recommended next (`workflow brainstorm <next ROADMAP item>`, `memory.compact` if `MEMORY.md` grew,
PR if not on `main`).

## Ground rules

- **Verify against the code — and the data.** Every interface, signature and column a phase relies on
  is checked in the real code; anything the brief says about code is a hypothesis until then. When
  the Outcome depends on real data (volumes, thresholds, coverage), a read-only query confirms the
  data can produce it before the behaviours are confirmed.
- **Contracts move in lockstep** producer → validator → consumer; backward-compat shims only when
  the human asks.
- **Provenance header** — every run artifact opens with five lines: `Command:`, `Created:` (date),
  `Base:` (git sha), `Inputs:` (`<artifact> @ <its Base>` or `none`), `Status:`. At phase entry the
  input is `Status: complete` and **fresh**: `git diff --stat <Base>..HEAD -- <files it names>` shows
  only this run's own ticket commits. Stale → name it and route to the phase that must rerun.
- **Receipts vs code.** `*.md` and `*.txt` are receipts; every other file, in any folder, is code.
  "Code changed since X" = `git diff --stat X..HEAD -- . ':(exclude)*.md' ':(exclude)*.txt'` is
  non-empty. Code outside `.workflow/` never reads anything inside it.
- **Commit after each verified ticket.** Wrap archives a run (`Status: done`); folders stay.

## Command index

Read the one reference for the invoked command; `status` and `next` need only this file and `ROUTING.md`.

| Command | Reference |
|---|---|
| `workflow brainstorm <slug>`, `workflow improve <feature> - goal: <goal>`, `workflow park [slug]` | `references/phase-0-brainstorm.md` |
| `workflow plan` | `references/phase-2-plan.md` |
| `workflow execute` | `references/phase-3-execute.md` (+ `references/tests.md`) |
| `workflow review` (+ patch cycle) | `references/phase-4-review.md` |
| `workflow wrap` | `references/wrap.md` |
| `workflow learn`, `workflow log` | `references/learning-worklog.md` |
| `workflow todo [idea]` | `references/todo.md` |
| `workflow bootstrap [PRD.md]` | `references/bootstrap.md` |
| `workflow realign` | `references/realign.md` |

Maintaining this skill (growth, vendor and prompt-style rules) is covered in `README.md`.
