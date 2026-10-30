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

**Invocation:** `workflow <command> [slug]`; pass the CLI's skill prefix to the card script with
`--prefix` if it has one.

**Checkout:** Before reading a run, follow [references/worktrees.md](references/worktrees.md).
It resolves every phase and status to the run's checkout; execute opens isolation, wrap lands it.
For plan, execute, review and wrap, read [Unattended runs](references/unattended.md) when the brief's line 6 is `Mode: unattended`. Its question rules override chat waits.

## The run — `.workflow/<slug>/`

One run = one folder, tracked in git, kept forever; its files are the state machine.

| Artifact | Written by | Holds |
|---|---|---|
| `brainstorm.md` | brainstorm | the **brief**: problem, behaviours (B#), decisions, test seams, out of scope — status of record for the run |
| `plan.md` | plan, then execute | findings + **tickets** (T#), each with acceptance lines and a verify command; execution state |
| `patch_plan.md` | review | fix tickets for the current patch cycle |
| `review.md` | review | coverage, the current cycle's findings and verdict, a `## Resolved` table of earlier cycles |
| `decisions.md` | any phase after brainstorm | headerless table of questions, defaults, statuses and answers |
| `routing.md` | human, directly or by request | headerless `Key \| Vendor · Model \| Effort` table; replaces a phase's model and effort for this run; fallback, context and approval stay shared |
| `learnings.md`, `wrap.md` | any / wrap | tagged lessons; wrap's checkpoint, then the run's ≤ ~40-line summary |

**Layout.** The top level holds only the artifacts above; everything else goes in a subfolder by
kind, created when first needed: `receipts/` · `screens/` · `notes/` · `scripts/` · `data/` ·
`prototypes/` · `understand/`. What each holds: `references/phase-3-execute.md`, *Run folder layout*.

Provenance headers carry `Status:` — `drafting` (resume that phase) · `complete` · `parked` ·
`done`. A run whose `brainstorm.md` is `parked` or `done` is not live.

| State of a live run | Next |
|---|---|
| `brainstorm.md` only | plan |
| `plan.md` with a ticket `awaiting-human` and none other ready | the human's action named in that ticket, then execute |
| `plan.md` with a ticket not `done` | execute |
| every ticket done; no `review.md`, or code changed since its `Base` | review |
| `patch_plan.md` with a ticket not `done` | execute (runs the patch plan) |
| `review.md` with no open finding and no code change since its `Base` | wrap |

## Grounding — tiered reads

- **Always:** the run's live artifacts (`brainstorm.md`, `plan.md`, `patch_plan.md`, `decisions.md` when present, the *current*
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
- **Decisions needed** — numbered, one decision each, and every question uses this shape, one row
  per option, never a run-on paragraph:

  ```
  **1. <title>** <the question, ≤2 plain sentences>
  - ➡️ **a) <option>** — recommended: <why it wins, in the reader's terms>
  - b) <option> — <what it costs or risks, why it is the weaker pick>
  - c) <option> — <same>
  ```

  The ➡️ row is first and bold, so the recommendation is seen without reading on. Every option
  carries a reason: the winner says why it wins, each other says why it loses; "also fine" is not a
  reason. When two options truly tie, say so and say what would tip it. Keep each row to one or two
  lines and one blank line between questions, so "all defaults except 2b" answers it.
- A negative result is one line ("`PRODUCT.md` — no changes").

**Clarify gate** (every phase except brainstorm): before the first edit, when a misread is expensive
— ambiguous scope, a command/state mismatch, schema/contract/deletion work, a silent assumption —
ask one round of ≤3 questions and wait.

**Budgets** — thinking is unbounded, files are not. The limits sit in each phase's reference and in
`check-run.py`, which flags an overrun. Over budget: propose two runs and ask; record a refusal as
`Split declined by human: <when>`. Cut prose, never acceptance lines or checks.

## Seats

**Brainstorm partner** (the grill; also `todo`, wrap) · **default executor** (logic tickets, P1–P3
fixes) · **heavy executor** (schema/SQL/contract tickets, P0 fixes, hardest multi-file work) ·
**mechanical lane** (tickets with an explicit expected text result) · **operator** (live or
irreversible writes, authorizations, hosted consoles: run by the human, or by the agent after
approval) · **strict reviewer** (the skeptic — plan, review, patch plans, `realign`; read-only except
`realign`).

Invariants:

- One step runs in one session only. Name any model switch.
- **Name the running model from a record, not memory** (`references/phase-3-execute.md`).
- **Sub-agents are read-only breadth**, their findings verified; writing runs in the main session.

Every phase starts fresh, re-grounded from the run folder and git; the handoff is where the model
swap happens, and a **reset** (not compaction) is how. The CLI's literal commands for *reset*,
*context meter* and *model picker* are in `README.md`.

## The closing card — `workflow next`

Every phase ends with this card as the turn's last output. **A turn that waits for a chat answer** (a
UI check, a clarify question, the plan's ticket-list round) **ends on the Decisions list, no card**.

Before the card, commit and push from the resolved checkout per `references/worktrees.md`.
Resolve unexpected `check-run.py` worktree or branch warnings first, or ask about them.
Then run `python3 <skill>/scripts/next-step.py <slug> --repo <checkout>` and print stdout unchanged
as the turn's last output. `<skill>` is this skill's absolute folder; `<checkout>` is the resolved
checkout. `workflow next` runs the same command. Add `--prefix /` when the CLI needs that prefix.
An error stops the card: report stderr and resolve it before retrying.

`--json` returns schema version 1 with `phase`, `command`, `ticket`, `model`, `fallback`, `reads`,
`blocker` and the rendered `card`. Consumers copy these fields; the script reads `ROUTING.md`
for the configured assignment. Availability and model switching remain the consumer's job.
A finished wrap keeps its ✅ summary card (`references/wrap.md`).

## Ground rules

- **Verify against the code — and the data.** Every interface, signature and column a phase relies on
  is checked in the real code; the brief's claims are hypotheses until then. An Outcome that depends
  on real data gets a read-only query before its behaviours are confirmed.
- **Provenance header** — `learnings.md`, `decisions.md` and `routing.md` are headerless; other artifacts open with five lines: `Command:`, `Created:` (a brief or plan adds `· <model>`), `Base:`
  (git sha), `Inputs:` (`<artifact> @ <its Base>` or `none`), `Status:`. At phase entry the input is
  `Status: complete` and **fresh**: `git diff --stat <Base>..HEAD -- <files it names>` shows only this
  run's own ticket commits. Stale → name it and route to the phase that must rerun.
- **Receipts vs code.** Receipts are `*.md`, `*.txt`, and all of a run's `screens/`,
  `prototypes/`, `understand/`; every other file is code. "Code changed since X" = `git diff --stat X..HEAD -- .
  ':(exclude)*.md' ':(exclude)*.txt' ':(exclude,glob).workflow/*/screens/**'
  ':(exclude,glob).workflow/*/prototypes/**' ':(exclude,glob).workflow/*/understand/**'` is non-empty — the **receipt-rule diff**. Code
  outside `.workflow/` never reads anything inside it.
- **The human's edits.** A dirty path that no run commit touched (`git diff --name-only <plan Base>..HEAD`
  omits it) is the human's own work, such as a config file the app rewrites on save. Leave it
  uncommitted and name it once in the phase report; it never stops a gate or makes the tree unclean.
- **Simplicity.** The smallest diff that passes is the target: every added line is one more for
  review to read and the next run to keep. Search the repo for an existing helper before writing
  one, and say in the ticket report what the search found. A new abstraction needs two live callers.
- **Secret scan before every push.** `gitleaks git --log-opts="@{u}..HEAD" --redact -v --no-banner`
  (no upstream: `origin/<primary>..HEAD`); `--redact` keeps the value out of the transcript.
  Receipts are the usual source: a live query or log with a token in it. Exit 0 → push. Otherwise follow [references/secret-scan.md](references/secret-scan.md).
- **A run artifact is committed only on a passing check.** Chain it: `python3 <skill>/scripts/check-run.py <slug> && git commit ...`.
  A pipe such as `| tail` hides check-run's exit code, and a review once went out that cited files
  and shas that do not exist. Write an artifact only after the reads it reports on have returned.

## Command index

Read the one reference for the command; `status` and `next` need only `worktrees.md` and `ROUTING.md`.

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
