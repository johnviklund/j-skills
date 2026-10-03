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
vendors, models and efforts; which CLI serves a model is not this skill's concern.

**Invocation:** `workflow <command> [slug]` — only a message starting with `workflow` (or `/workflow`)
invokes the skill; the card's line carries the CLI's own skill prefix if it has one.

## The run — `.workflow/<slug>/`

One run = one folder, tracked in git, kept forever; its files are the state machine.

| Artifact | Written by | Holds |
|---|---|---|
| `brainstorm.md` | brainstorm | the **brief**: problem, behaviours (B#), decisions, test seams, out of scope — status of record for the run |
| `plan.md` | plan, then execute | findings + **tickets** (T#), each with acceptance lines and a verify command; execution state |
| `patch_plan.md` | review | fix tickets for the current patch cycle |
| `review.md` | review | coverage, the current cycle's findings and verdict, a `## Resolved` table of earlier cycles |
| `learnings.md`, `wrap.md` | any / wrap | tagged lessons; wrap's checkpoint, then the run's ≤ ~40-line summary |

**Layout.** The run folder's top level holds only the artifacts above. Everything else goes in a
subfolder by kind, created when first needed, so a human can find things later:

| Subfolder | Holds |
|---|---|
| `receipts/` | verification output, diffs, handoffs and operator receipts (`t3-verification.md`) |
| `screens/` | before/after screenshots of UI tickets (`t3-topic-page-before.jpg`) |
| `notes/` | longer working documents: investigations, audits, runbooks, drafts |
| `scripts/` | one-off scripts and harnesses (code: reviewed like any other) |
| `data/` | small frozen inputs and outputs (`*.json`, `*.csv`); bulk data stays outside the repo |
| `understand/` | the human explainer, written only by the `understand` skill |

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
state gets named and asked about; `workflow spec` is retired — route to `workflow plan <slug>`.

## Grounding — tiered reads

- **Always:** the run's live artifacts (`brainstorm.md`, `plan.md`, `patch_plan.md`, the *current*
  cycle of `review.md` plus its `## Resolved` table); `ROUTING.md` (the card's rows); `AGENTS.md`;
  the `MEMORY.md` index — open a `memory/<slug>.md` page only when its "Applies when" matches;
  `git log --oneline -15`; `git status`.
- **Targeted — `PRODUCT.md`, `DESIGN.md`** when product or UI is in scope: read the headings, then
  only the sections the brief or ticket touches (vocabulary, principles, current phase, the surface
  being changed). Record them in the artifact as `Docs read: PRODUCT.md §Vocabulary, §Principles ·
  DESIGN.md §Tables`. These docs are the anti-drift guard: read in full for brainstorming new product
  direction, `realign` and design-departure proposals, and before any ticket that might contradict them.
- **Targeted — `TODO.md`, `ROADMAP.md`:** only brainstorm ("already captured? already committed?"),
  wrap (hygiene) and `todo`. Plan, execute and review get what they need from the brief and plan.
- **Never by default:** `*_ARCHIVE.md` (`MEMORY_`, `TODO_`, `ROADMAP_`), `WORKLOG.md` beyond its
  latest entry, other runs' folders, `.workflow/archive/`. `grep` them on demand and read only the
  matching lines. A `done` run is history: if one matters, read its `wrap.md` alone.

## Talking to the human (every phase)

**The artifact is the record; chat is the receipt** (the human reads on a phone). Above the closing
card, a phase prints at most ~12 lines:

- **Result** — what the phase did, ≤3 plain lines.
- **Decisions needed** — a numbered list; each item is one decision in plain words, options
  lettered on their own lines, a ➡️ recommended default, so "all defaults except 2b" answers it.
  Every question in every phase uses this shape.
- A negative result is one line ("`PRODUCT.md` — no changes").

**Clarify gate** (every phase except brainstorm): before the first edit, if something material is
unclear or a misread is expensive — ambiguous scope, a command/state mismatch, schema/contract/
deletion work, a silent assumption — ask one round of ≤3 questions and wait. Clear mechanical work
proceeds.

**Budgets** — thinking is unbounded, files are not: `brainstorm.md` ≤ ~80 lines and ≤ 15
behaviours; `plan.md` ≤ ~120 lines and ≤ 8 tickets; `review.md` ≤ ~100 lines; a finished run's
`wrap.md` ≤ ~40. Over budget = the run is two runs: propose the split and ask. Meet a budget by
cutting prose, never acceptance lines or checks.

## Seats

**Brainstorm partner** (the grill; also `todo`, wrap) · **default executor** (logic tickets, P1–P3
fixes) · **heavy executor** (schema/SQL/contract tickets, P0 fixes, hardest multi-file work) ·
**mechanical lane** (tickets with an explicit expected text result) · **operator** (live or irreversible
writes, authorizations, hosted consoles: the human runs them, or approves and the agent runs them) · **strict reviewer** (the skeptic — plan,
review, patch plans, `realign`; read-only except `realign`).

Invariants:

- **Cross-vendor review.** The strict reviewer is a different vendor from the code's writer; a
  same-vendor review is degraded and says so in `review.md`. One step runs in one session only.
- **Availability first.** Open the model picker at session start, walk `ROUTING.md`'s fallback chain
  in order, and name any switch.
- **Name the running model from a record, not memory** — read the ID from the harness context or CLI
  config, write only the model (`references/phase-3-execute.md`).
- **Approval follows blast radius** (map in `ROUTING.md`): read-only none, mechanical auto, logic
  and contract tickets shown to the human ticket by ticket, operator tickets run or approved by the human.
  The lane — not the severity — sets seat and approval, fix tickets included.
- **Sub-agents are read-only breadth** (fact-finding, wide diffs), their findings verified; writing
  runs in the main session.

Every phase starts fresh, re-grounded from the run folder and git; the handoff is where the model
swap happens, and a **reset** (not compaction) is how. The CLI's literal commands for *reset*,
*context meter* and *model picker* are in `README.md`.

## The closing card — `workflow next`

Every phase ends with this card as the last output of the turn. **A turn that waits for an answer in
chat** — a diff approval, a clarify question, the plan's ticket-list round — **ends on the Decisions
list, with no card**: the reply is the answer. Fill the model line from `ROUTING.md`'s rows (a
*Trial* entry prints instead of the primary, marked `(trial)`) so the human never opens a file to
pick a model.

---
**▶ Next: <phase>** · <run slug> · <one-line why, or the cycle and finding ids for a patch cycle>
**Reset:** yes | no · **Model:** <model> · <effort> · <context> — fallback <model> <effort>
**Reads:** <files the next phase opens first>
```text
workflow <phase> <slug>
```
---

Reset is `yes` at every handoff, `no` only for same-seat work continuing. A step only the human can
take (an operator ticket, an escalation) reads `**Model:** human — <the one action>`, **Reads:**
naming the handoff. A finished run gets wrap's ✅ card instead (`references/wrap.md`).

## Ground rules

- **Verify against the code — and the data.** Every interface, signature and column a phase relies on
  is checked in the real code; the brief's claims about code are hypotheses until then. An Outcome
  that depends on real data gets a read-only query before its behaviours are confirmed.
- **Provenance header** — every run artifact opens with five lines: `Command:`, `Created:`, `Base:`
  (git sha), `Inputs:` (`<artifact> @ <its Base>` or `none`), `Status:`. At phase entry the input is
  `Status: complete` and **fresh**: `git diff --stat <Base>..HEAD -- <files it names>` shows only this
  run's own ticket commits. Stale → name it and route to the phase that must rerun.
- **Receipts vs code.** Receipts are `*.md`, `*.txt`, and everything in a run's `screens/` and
  `understand/`; every other file is code. "Code changed since X" = `git diff --stat X..HEAD -- .
  ':(exclude)*.md' ':(exclude)*.txt' ':(exclude,glob).workflow/*/screens/**'
  ':(exclude,glob).workflow/*/understand/**'` is non-empty — the **receipt-rule diff**. Code
  outside `.workflow/` never reads anything inside it.
- **Commit after each verified ticket.** Wrap archives a run (`Status: done`); folders stay.

## Command index

Read the one reference for the command; `status` and `next` need only this file and `ROUTING.md`.

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
