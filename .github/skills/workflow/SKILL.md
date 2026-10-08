---
name: workflow
description: >
  Personal solo-dev coding workflow, run only on an explicit "workflow COMMAND" or
  "/workflow COMMAND" message; never on casual mentions of brainstorm, plan, execute, review
  or learn elsewhere in a message. Commands: brainstorm, improve, plan, execute, review, park,
  wrap, status, next, learn, log, todo, bootstrap, realign; bare "workflow" = next.
---

# Workflow

> ⚠️ Invoke this skill first; the references are read through it, never on their own.

Four phases and a wrap: **brainstorm → plan → execute → review → wrap**. Each phase is a **seat**
(a job with an output contract) filled by whatever model currently earns it. Writer and reviewer
sit with different vendors on purpose — independence is the point. `ROUTING.md` maps seats to
vendors, models and efforts.

**Invocation:** `workflow <command> [slug]`; the card's command line carries the CLI's own skill
prefix if it has one.

## The run — `.workflow/<slug>/`

One run = one folder, tracked in git, kept forever; its files are the state machine.

| Artifact | Written by | Holds |
|---|---|---|
| `brainstorm.md` | brainstorm | the **brief**: problem, behaviours (B#), decisions, test seams, out of scope — status of record for the run |
| `plan.md` | plan, then execute | findings + **tickets** (T#), each with acceptance lines and a verify command; execution state |
| `patch_plan.md` | review | fix tickets for the current patch cycle |
| `review.md` | review | coverage, the current cycle's findings and verdict, a `## Resolved` table of earlier cycles |
| `learnings.md`, `wrap.md` | any / wrap | tagged lessons; wrap's checkpoint, then the run's ≤ ~40-line summary |

**Layout.** The top level holds only the artifacts above; everything else goes in a subfolder by
kind, created when first needed: `receipts/` (verification output, diffs, handoffs:
`t3-verification.md`) · `screens/` (UI before/after: `t3-topic-page-before.jpg`) · `notes/`
(investigations, audits, runbooks, drafts) · `scripts/` (one-off code, reviewed like any other) ·
`data/` (small frozen `*.json`/`*.csv`; bulk data stays outside the repo) · `prototypes/`
(throwaway sketches) · `understand/` (written only by the `understand` skill).

Every artifact header carries `Status:` — `drafting` (resume that phase) · `complete` · `parked` ·
`done`. A run whose `brainstorm.md` is `parked` or `done` is not live.

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
`workflow status` prints one line per non-done run — `slug · phase · blocker or none · next command`
(an `awaiting-human` ticket is the blocker, with its action). A command that doesn't fit the run's
state gets named and asked about.

## Grounding — tiered reads

- **Always:** the run's live artifacts (`brainstorm.md`, `plan.md`, `patch_plan.md`, the *current*
  cycle of `review.md` plus its `## Resolved` table); `ROUTING.md` (the card's rows); `AGENTS.md`;
  the `MEMORY.md` index — open a `memory/<slug>.md` page only when its "Applies when" matches;
  `git log --oneline -15`; `git status`.
- **Targeted — `PRODUCT.md`, `DESIGN.md`** when product or UI is in scope: the headings, then only
  the sections the work touches, recorded as `Docs read: PRODUCT.md §Vocabulary · DESIGN.md §Tables`.
  They are the anti-drift guard: read in full for new product direction, `realign`, design-departure
  proposals, and any ticket that might contradict them.
- **Targeted — `TODO.md`, `ROADMAP.md`:** only in brainstorm, wrap and `todo`.
- **Never by default:** `*_ARCHIVE.md`, `WORKLOG.md` beyond its latest entry, other runs' folders,
  `.workflow/archive/`: `grep` them and read only matching lines. For a `done` run, read its `wrap.md` alone.

## Talking to the human (every phase)

**The artifact is the record; chat is the receipt** (the human reads on a phone). Everything the
human reads follows the Rules of the `plain` skill: invoke it once per phase before writing. Ids,
commands, paths and fixed line formats stay as they are. Above the closing card, at most ~12 lines:

- **Result** — what the phase did, ≤3 plain lines.
- **Decisions needed** — numbered, one decision each, options lettered on their own lines, a ➡️
  recommended default, so "all defaults except 2b" answers it. Every question uses this shape.
- A negative result is one line ("`PRODUCT.md` — no changes").

**Clarify gate** (every phase except brainstorm): before the first edit, when a misread is expensive
— ambiguous scope, a command/state mismatch, schema/contract/deletion work, a silent assumption —
ask one round of ≤3 questions and wait.

**Budgets** — thinking is unbounded, files are not: `brainstorm.md` ≤ ~80 lines and ≤ 15
behaviours; `plan.md` ≤ ~120 lines and ≤ 8 tickets; `review.md` ≤ ~100 lines; a finished run's
`wrap.md` ≤ ~40. Over budget = two runs: propose the split and ask. Cut prose, never acceptance
lines or checks.

## Seats

**Brainstorm partner** (the grill; also `todo`, wrap) · **default executor** (logic tickets, P1–P3
fixes) · **heavy executor** (schema/SQL/contract tickets, P0 fixes, hardest multi-file work) ·
**mechanical lane** (tickets with an explicit expected text result) · **operator** (live or
irreversible writes, authorizations, hosted consoles: run by the human, or by the agent after
approval) · **strict reviewer** (the skeptic — plan, review, patch plans, `realign`; read-only except
`realign`).

Invariants:

- **Cross-vendor review.** The strict reviewer is a different vendor from the code's writer; a
  same-vendor review is degraded and says so in `review.md`. One step runs in one session only.
- **Availability first.** Open the model picker at session start, walk `ROUTING.md`'s fallback chain
  in order, and name any switch.
- **Name the running model from a record, not memory** (`references/phase-3-execute.md`).
- **The human acts only where a human adds something** (map in `ROUTING.md`): code is checked by
  tests and the cross-vendor review, not diff reading; a user-visible change is tried by the human
  before its commit. The lane — not the severity — sets the seat, fix tickets included.
- **Sub-agents are read-only breadth**, their findings verified; writing runs in the main session.

Every phase starts fresh, re-grounded from the run folder and git; the handoff is where the model
swap happens, and a **reset** (not compaction) is how. The CLI's literal commands for *reset*,
*context meter* and *model picker* are in `README.md`.

## The closing card — `workflow next`

Every phase ends with this card as the turn's last output. **A turn that waits for a chat answer** (a
UI check, a clarify question, the plan's ticket-list round) **ends on the Decisions list, no card**.
Fill the model line from `ROUTING.md`'s rows (a *Trial* entry replaces the primary, marked
`(trial)`) so the human never opens a file to pick a model.

---
**▶ Next: <phase>** · <run slug> · <one-line why, or the cycle and finding ids for a patch cycle>
**Reset:** yes | no · **Model:** <model> · <effort> · <context> · fallback <model> <effort>
**Reads:** <files the next phase opens first>
```text
workflow <phase> <slug>
```
---

**Reads:** names run files and receipts only; the CLI already loads `AGENTS.md` and its kin. Before
the card, the run's commits are on the primary branch and pushed: the next phase opens the primary
checkout, so a `check-run.py` worktree or branch warning is resolved first, or asked about.
Reset is `yes` at every handoff, `no` only for same-seat work continuing. A human-only step (an
operator ticket, an escalation) reads `**Model:** human · <the one action>` with **Reads:** naming
the handoff. A finished run gets wrap's ✅ card (`references/wrap.md`).

## Ground rules

- **Verify against the code — and the data.** Every interface, signature and column a phase relies on
  is checked in the real code; the brief's claims are hypotheses until then. An Outcome that depends
  on real data gets a read-only query before its behaviours are confirmed.
- **Provenance header** — every run artifact opens with five lines: `Command:`, `Created:`, `Base:`
  (git sha), `Inputs:` (`<artifact> @ <its Base>` or `none`), `Status:`. At phase entry the input is
  `Status: complete` and **fresh**: `git diff --stat <Base>..HEAD -- <files it names>` shows only this
  run's own ticket commits. Stale → name it and route to the phase that must rerun.
- **Receipts vs code.** Receipts are `*.md`, `*.txt`, and all of a run's `screens/`,
  `prototypes/`, `understand/`; every other file is code. "Code changed since X" = `git diff --stat X..HEAD -- .
  ':(exclude)*.md' ':(exclude)*.txt' ':(exclude,glob).workflow/*/screens/**'
  ':(exclude,glob).workflow/*/prototypes/**' ':(exclude,glob).workflow/*/understand/**'` is non-empty — the **receipt-rule diff**. Code
  outside `.workflow/` never reads anything inside it.
- **Simplicity.** The smallest diff that passes is the target: every added line is one more for
  review to read and the next run to keep. Search the repo for an existing helper before writing
  one, and say in the ticket report what the search found. A new abstraction needs two live callers.
- **Commit after each verified ticket.** Wrap archives a run (`Status: done`); folders stay.

## Command index

Read the one reference for the command; `status` and `next` need only this file and `ROUTING.md`.

| Command | Reference in `references/` |
|---|---|
| `brainstorm <slug>`, `improve <feature> - goal: <goal>`, `park [slug]` | `phase-0-brainstorm.md` |
| `plan` | `phase-2-plan.md` |
| `execute` | `phase-3-execute.md` (+ `tests.md`) |
| `review` (+ patch cycle) | `phase-4-review.md` |
| `wrap` | `wrap.md` |
| `learn`, `log` | `learning-worklog.md` |
| `todo [idea]` | `todo.md` |
| `bootstrap [PRD.md]` | `bootstrap.md` |
| `realign` | `realign.md` |

Maintaining this skill is covered in `MAINTAINING.md`.
