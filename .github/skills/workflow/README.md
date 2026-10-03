# workflow (v2.1) — a four-phase coding workflow skill for CLI coding agents

A vendor-neutral [agent skill](https://code.claude.com/docs/en/skills) that runs a disciplined
solo-dev loop across whatever CLI coding agents you use: **brainstorm → plan → execute → review →
wrap**. The brainstorm is a grill that ends in a planning-ready brief; the plan is a short list of
tracer-bullet tickets, each proven by tests. Models fill **seats** (roles with an output contract); you map seats
to your own CLIs and models in one file. Born as a personal two-CLI workflow; open-sourced
because the shape turned out to be portable.

## Why it exists

- **Seats, not vendors — and never CLIs.** The workflow speaks in roles — brainstorm partner,
  default executor, heavy executor, mechanical lane, strict reviewer. `ROUTING.md` maps those to
  vendors and models; which CLI serves a model is your environment's business, not the skill's.
  One CLI that serves both vendors, or one CLI per vendor — same mapping either way. Swapping
  models is a one-file edit; the workflow never changes.
- **Cross-vendor review.** The strict reviewer should be a different vendor from whichever model
  wrote the code. Each run records its writer, so the reviewer detects a same-vendor pairing and
  declares degraded mode itself instead of relying on being told.
- **Files are the state machine.** Every phase reads and writes `.workflow/<slug>/*.md`, so any fresh
  session re-grounds from disk instead of trusting its own memory. Every phase persists *as it
  goes* — findings as they're confirmed, tickets as they settle, execution state after every
  ticket — so running out of context costs warm cache and nothing else.
- **Learning compounds.** Each run routes durable lessons to memory/skills/design docs, keeps a
  bounded worklog whose `Run:`/`Seats:` lines are the evidence a model is judged on — models
  earn seats on real trial runs, not synthetic exams — and, rarely, deposits a **reviewer exam
  case**: a diff whose P0/P1 a model missed, capped at 8.
- **Chat is the receipt, files are the record.** Every phase's turn is bounded (~12 lines above
  the closing card); artifacts have line budgets and the plan is capped at 8 tickets; every
  question is one decision with lettered options and a recommended default. Detail lives in
  `.workflow/`, not in the conversation.
- **Gates where mistakes are expensive.** Clarifying questions before ambiguous or risky work,
  a hands-on check of every UI change before it is committed, operator tickets for live or irreversible steps
  (the agent prepares the handoff, you run it, a receipt proves it), review with P0–P3 verdicts
  that checks the outcome on the surface users reach, patch loops bounded at three cycles, and a
  wrap that refuses to ship code the review never saw.

## Walkthrough — one run

```text
workflow brainstorm auth-refresh      # creates .workflow/auth-refresh/; grilling rounds → brief:
                                      # behaviours B1..Bn, decisions, test seams, out of scope
workflow plan auth-refresh            # cross-vendor audit against real code → ≤8 tracer-bullet
                                      # tickets, each with acceptance lines + a verify command
workflow execute auth-refresh         # one ticket at a time: red → green → commit
workflow review auth-refresh          # P0–P3 verdict → review.md; patch cycle if needed
workflow wrap auth-refresh            # checks, push, docs reconciled, learnings → memory/,
                                      # worklog entry, folder archived (Status: done)
```

Every phase ends with a **closing card** — reset or continue, the exact model · effort
· context to pick, what to read, the line to send. Reset the session at each handoff; the card
tells you to. With only one live run the slug is optional.

## Several runs at once

```text
workflow brainstorm export-csv        # ... "good idea, not now" → Status: parked
workflow brainstorm rate-limits       # a second live run
workflow status                       # auth-refresh · execute · none · workflow execute auth-refresh
                                      # rate-limits  · plan · none · workflow plan rate-limits
                                      # export-csv   · parked at brainstorm · unpark: <what would>
workflow park rate-limits             # set aside at any phase; nothing deleted
workflow plan export-csv              # unpark = invoke the phase it was at
```

One home per idea: `TODO.md` holds ideas not yet brainstormed; a parked folder holds ideas that
have been; a live folder is in flight. Park before planning when you can — a parked plan goes
stale with the next commit, and the provenance gate will make you re-plan.

## What a run folder holds

```text
.workflow/auth-refresh/
  brainstorm.md    the brief: problem · outcome · behaviours · decisions · test seams · out of scope  ← status of record
  plan.md          findings · ≤8 tickets (acceptance, verify, status) · coverage of behaviours · risks · impacts · deviations
  patch_plan.md    fix tickets, only during a patch cycle; run by `workflow execute`; deleted at wrap
  review.md        coverage · the current cycle's P0–P3 findings and verdict · a `## Resolved` table of earlier cycles (≤ ~100 lines)
  learnings.md     tagged lines, routed by memory.remember (each marked [routed → …]); kept as the record
  wrap.md          wrap's checkpoint (an interrupted wrap resumes), then the run's ≤ ~40-line summary — the only file later runs read
  receipts/        verification output, diffs, operator handoffs and receipts; kept as evidence
  screens/         before/after screenshots of UI tickets (t3-topic-page-before.jpg)
  notes/           investigations, audits, runbooks, drafts
  scripts/         one-off scripts and harnesses (code — reviewed)
  data/            small frozen inputs/outputs; bulk data stays outside the repo
  prototypes/      brainstorm's throwaway sketches (P1-density/), evidence for a decision; never shipped
  understand/      explainer.html, written by the `understand` skill after wrap
```

The top level holds only the artifacts; subfolders appear when first needed.

Runs are tracked in git and never deleted: after wrap the folder is the run's history, readable
by anyone (or any agent) later. Grounding only ever reads live runs, so the archive costs nothing.

Two rules keep the archive honest. **Receipts vs code:** `*.md`/`*.txt` and a run's `screens/`,
`prototypes/` and `understand/` are receipts; anything
else — a script in `.workflow/`, a config in `docs/` — is code, must be reviewed, and can't ship
through wrap's commit. **Freshness is per file, not per ancestry:** a plan is stale when any file
it names changed since its `Base` (other than by its own ticket commits), which is exactly what happens to
a parked plan — it gets re-audited, not executed.

## Repo layout

| File | Role | You edit it? |
|---|---|---|
| `SKILL.md` | The hub: invocation, runs & state machine, seats & invariants, reporting rule, per-command index | No |
| `ROUTING.md` | **Your mapping**: seat → (vendor · model · effort · context), trial column, fallbacks, phase → effort/approval. Small on purpose: the closing card reads it every phase | **Yes — this is the whole setup** |
| `ROUTING-NOTES.md` | How models earn seats, the upkeep loop, mode notes — read only by `checkup` | Yes (rarely) |
| `references/*.md` | Full instructions per command, loaded one-per-invocation | No |
| `scripts/check-run.py` | Checks a run folder against the shapes in `SKILL.md` and `references/`: headers, budgets, ticket fields, behaviour coverage, review dispositions, layout. Phases run it before marking an artifact `complete`; `checkup` runs it with `--all` | No |
| `SKILL-IMPACT.md` | Log of every change to these skills and what the runs after it showed; `Mode:` line sets whether skill edits are autonomous or approved | Yes (mode line; accept/reject rows) |

`SKILL.md` and `references/` contain no vendor names by design, and no file in the skill names a
CLI product; a brand name in the wrong place is a bug. The skill names only generic verbs —
*reset*, *compact*, *context meter*, *model picker*, *explicit invocation* — and the cheat sheet
below holds the literal command per CLI. This README is reader-facing and names tools freely. The
shipped `ROUTING.md` is the author's real mapping (OpenAI writes, Anthropic reviews).

## CLI cheat sheet (reader-facing — the skill never depends on this)

Verify each cell against the CLI's own `/` menu — these drift.

| CLI | Serves | Reset session | Compact | Context meter | Model picker | Explicit skill invocation | Autonomy / speed / breadth modes |
|---|---|---|---|---|---|---|---|
| Codex CLI | OpenAI models | `/new` (`/clear` also works) | `/compact` | `/status` | `/model` (effort also via `model_reasoning_effort` in `~/.codex/config.toml`) | `$workflow` | `/goal` (autonomy), `/fast` (speed), `ultra` where the model offers it (breadth) |
| Copilot CLI | Both vendors | `/clear` | `/compact` (auto-compacts near ~80% — treat as a deadline, reset at a step boundary first) | `/context` | `/model` (effort also via `--reasoning-effort`) | description-matched; as a plugin, `/<plugin>:workflow` | none sanctioned by default |
| Claude Code | Anthropic models | `/clear` | `/compact` | `/context` | `/model` | `/workflow` | `/effort ultracode` and the Task/sub-agent tool (breadth, read-only seats only) |

## What a run writes

Each run lives in `.workflow/<slug>/`, tracked in git, and stays after wrap as the run's record
(transient files dropped, `Status: done`). Every artifact opens with a
five-line provenance
header, and the state machine reads it rather than guessing from which files exist:

```
Command: workflow plan
Created: 2026-07-28
Base:    <git sha when the file was created>
Inputs:  .workflow/<slug>/brainstorm.md @ <its own Base sha>
Status:  drafting        # → complete when the phase writes its closing section
```

`Status: drafting` always means *resume that phase*, never advance — so a half-drafted plan can't
be mistaken for a finished one, and a review that died at 90% is distinguishable from one that
never ran. `Inputs` and `Base` let a phase notice its input went stale and ask, instead of
silently building on it.

Durable output goes to the repo: commits, `WORKLOG.md`, `MEMORY.md` + `memory/` pages, `TODO.md`, product docs, and
reviewer exam cases in the private `j-skills-evals` repo (`strict-reviewer/missed-<topic>.md`, the only eval set; private because cases copy code).

## Install

The skill is a plain folder. Put it where your CLI looks, then rewrite `ROUTING.md`.

**One-copy layout (recommended).** No single directory is read by all three, but each harness
follows a symlink, so keep one canonical copy and point the others at it:

```bash
mkdir -p .agents/skills && cp -r workflow .agents/skills/workflow   # canonical copy
mkdir -p .claude/skills && ln -s ../../.agents/skills/workflow .claude/skills/workflow
mkdir -p .codex/skills  && ln -s ../../.agents/skills/workflow .codex/skills/workflow
git add .workflow/               # runs are tracked — do not gitignore .workflow/
```

Copilot CLI reads `.agents/skills/` directly, so the canonical copy already covers it.

Or install per harness:

| Harness | Project location | Personal location | Verify | Explicit invocation |
|---|---|---|---|---|
| **Claude Code** | `.claude/skills/workflow/` | `~/.claude/skills/workflow/` | `/workflow status` | `/workflow` — the directory name *is* the command |
| **Codex CLI** | `.codex/skills/workflow/` | `$CODEX_HOME/skills/workflow/` (defaults to `~/.codex/skills/`) | `/skills` lists it | `$workflow status` |
| **Copilot CLI** | `.github/skills/`, `.claude/skills/` or `.agents/skills/` | `~/.copilot/skills/` or `~/.agents/skills/` | `/skills list`, `/skills info workflow` | description-matched; as a plugin, `/<plugin>:workflow` |

Codex CLI does **not** read `.agents/skills/` — it discovers only `$CODEX_HOME/skills`
(`~/.codex/skills` when `CODEX_HOME` is unset) plus the project's `.codex/skills/`. A copy left
solely in `.agents/skills/` loads in Copilot CLI and silently never appears in Codex.

Then:

1. **Rewrite `ROUTING.md`** for your vendors and models — seat table, phase table, mode notes.
   That is the entire configuration; add your CLI to the cheat sheet above if it isn't listed.
2. **Smoke test**: `workflow status` in each CLI (does it load?), `workflow next` (does it read
   `ROUTING.md`?), then one toy `workflow brainstorm hello` → `workflow wrap hello` end to end,
   and check `.workflow/hello/` is committed with `Status: done`.

**Verify locally before trusting the paths above.** Skill discovery has moved before and is
version-dependent — some builds gated skills behind a feature flag. `/skills` (Codex, Copilot)
and `/doctor` (Claude Code) are the ground truth on your machine; the tables above were verified
against Codex CLI 0.159 and Copilot CLI 1.0.91. If a
skill loads but never triggers, check its description isn't being shortened out by a crowded
skill list; if Codex ignores it, check `~/.codex/config.toml` for a `[[skills.config]]` entry
disabling it.

## Update

```bash
cd .agents/skills/workflow && git pull      # or re-copy the folder
```

Keep your own `ROUTING.md`, `ROUTING-NOTES.md` and `SKILL-IMPACT.md` — they are the files you edit, and an update
should never overwrite them. Copy the incoming `ROUTING.md` only to pick up new *sections*, then re-enter your own mappings. After updating, run `/skills reload` in Copilot CLI, or restart
the session in Codex and Claude Code, then re-run the smoke test.

If you edit the skill itself: keep `SKILL.md` under ~180 lines and ~10 KB (see *Context budget*), keep vendor names out of
`SKILL.md` and `references/`, and grep the **whole** folder — `ROUTING.md` and this README
included — when you retire a command, or you will leave dangling references behind.

## Commands

Invocation is deliberate — a message starting `workflow <command>` (or `/workflow <command>`);
casual mentions of "plan" or "review" never trigger it.

| Command | What it does |
|---|---|
| `workflow brainstorm <slug>` | Creates `.workflow/<slug>/`; grilling rounds with recommended answers → the brief in `brainstorm.md`; reviews `TODO.md` for related items |
| `workflow improve <feature> - goal: <goal>` | Brainstorm seeded by a real code audit |
| `workflow plan` | Cross-vendor audit of the brief against real code → ≤8 tracer-bullet tickets, human-approved → `plan.md` |
| `workflow execute` | One ticket at a time: acceptance tests red → green, diff, commit, persist state |
| `workflow review` | Acceptance + defects review, P0–P3 against a written severity bar; re-reviews scoped to the fix diff; patch cycle bounded at 3 |
| `workflow park [slug]` | Set a run aside at any phase; unpark by invoking the phase it was at |
| `workflow wrap` | Final checks, commit/push, reconcile product docs, route learnings to `memory/`, deposit eval cases, archive done TODO/roadmap items, worklog, run summary; archive the run folder |
| `workflow todo <idea>` | Capture an idea into `TODO.md`, well-placed and well-shaped |
| `workflow bootstrap` | Stand up `AGENTS.md`/`MEMORY.md`/`TODO.md` and repo conventions in a fresh project |
| `workflow realign` | Evidence-backed, human-approved re-check of `PRODUCT.md`/`DESIGN.md` against what actually shipped |
| `workflow status` / `next` / `log` / `learn` | Where am I / what's the closing card / ad-hoc worklog entry / capture a learning |

Every phase response ends with a **closing card** (except a turn that waits for your in-chat
answer, such as a UI check, which ends on its lettered options): reset-or-continue, which model/
effort (from `ROUTING.md`), what to read, and the exact line to send. There is no compact
command — resetting is lossless and safe at any context fullness, so it replaced compaction
entirely.

## Companion skills (separate folders, same repo)

| Skill | Role in the loop |
|---|---|
| `memory.remember` | Routes a run's `learnings.md` at wrap: repeats bump an existing `memory/` page's occurrence count; new lessons become pages; `Occurrences: 3` promotes a principle into a skill (logged in `SKILL-IMPACT.md`, trialed) |
| `memory.compact` | Manual, proposal-only cleanup of `memory/`: merges same-claim pages, splits legacy inline `MEMORY.md` entries into pages, archives stale ones |
| `checkup` | Read-only health report: skill wiring, memory pages, docs, runs (stalled/parked), config, and the per-seat and per-skill-change comparison of worklog numbers that decides promotions |
| `evals` | The one exam: `evals.run reviewer`, recall and false alarms on ≤10 cases, run before swapping the strict reviewer or keeping a change to the review instructions |
| `retro` | Manual retrospective on a run or session: where the agent lost time → ranked environment fixes, routed through `memory.remember`, `workflow todo` and `checkup` |
| `understand` | After wrap: `understand <slug>` writes `.workflow/<slug>/understand/explainer.html`, a cited, human-friendly page (prose, diagrams, before/after screenshots from `screens/`, unrequested UI changes flagged); `understand <area>` does the same for a part of the codebase |

## How models and skills earn their place

Neither is benchmarked; both are trialed on real runs. Put a candidate model in a seat's **Trial**
column in `ROUTING.md`; the card prints it, wrap records it in the worklog's `Seats:` line;
`checkup seats` compares it with the incumbent after two runs; you promote or reject in
`ROUTING.md`. A skill change works the same way: `memory.remember` (or you) edits the skill, adds
a `SKILL-IMPACT.md` line marked `trialing`, and the next runs' `Skills:` lines let `checkup`
compare before/after. Worse means revert the commit and log it.

**Autonomous or approved — your call.** `SKILL-IMPACT.md` starts with `Mode: autonomous` or
`Mode: approve`. Autonomous: `memory.remember` applies skill edits directly, in their own commit.
Approve: it writes `SKILL.md.proposed` beside the skill and logs the row as `proposed`; you accept
with `mv`, and `checkup` nags about anything left proposed. The log is identical either way.

## Migrating a v1 repo

A flat `.workflow/*.md` from v1 is one run: `mkdir .workflow/<slug> && git mv .workflow/*.md
.workflow/<slug>/`, remove `.workflow/` from `.gitignore` if it is there, and run `workflow status`.
A flat `MEMORY.md` keeps working as an index with inline entries until `memory.compact` splits it
into pages; nothing breaks in between.

## Built for the next step

v2 keeps every run as a self-describing folder, keeps memory as pages, and gives every command an
explicit slug — no hidden "current run." That is deliberate: it lets a coordinating agent in a
persistent thread hand runs to delegated agents, even several at once, with git and the run
folders as the only shared state. Nothing in v2 depends on that future; everything in it is
compatible with it.

## Context budget

A run's grounding is the cost that repeats every phase, so the skill keeps it small and targeted —
without weakening `PRODUCT.md`/`DESIGN.md` as the anti-drift guard (targeted, never skipped).

**Tiered reads** (the rule lives in `SKILL.md` *Grounding*):

| Tier | Files |
|---|---|
| Always | the run's live artifacts (current `review.md` cycle + its `## Resolved` table only), `ROUTING.md`, `AGENTS.md`, the `MEMORY.md` index (a `memory/` page only when its "Applies when" matches), `git log --oneline -15`, `git status` |
| Targeted | `PRODUCT.md`/`DESIGN.md` — headings first, then only the sections the brief or ticket touches; the sections read are recorded as `Docs read:`. Full read only for new product direction, `realign`, a design-departure proposal, or a ticket that might contradict them. `TODO.md`/`ROADMAP.md` — brainstorm, wrap and `todo` only |
| Never by default | `MEMORY_ARCHIVE.md`, `TODO_ARCHIVE.md`, `ROADMAP_ARCHIVE.md`, `WORKLOG.md` beyond its latest entry, other runs' folders, `.workflow/archive/` — `grep` and read matching lines. A `done` run is read through its `wrap.md` alone |

**Targets** (check with `wc -c`; flag a regression when a file passes its budget):

| File | Budget |
|---|---|
| `SKILL.md` | ≤ ~10 KB |
| `ROUTING.md` | ≤ ~5.5 KB (trial and upkeep notes belong in `ROUTING-NOTES.md`) |
| one phase reference | ≤ ~10 KB |
| `brainstorm.md` / `plan.md` / `review.md` / finished `wrap.md` | ~80 / ~120 / ~100 / ~40 lines |
| repo `TODO.md` / `ROADMAP.md` | ~15 KB / ~12 KB — wrap flags and proposes archiving, never deletes |
| a committed receipt | a few KB: numbers and checksums, not data |

Default grounding for plan, execute or review is therefore `SKILL.md` + `ROUTING.md` + one
phase reference (about 22–25 KB) plus the repo's `AGENTS.md`, the `MEMORY.md` index and the run's
live artifacts. When a change adds an always-read rule, remove or move another.

## Design constraints (on purpose)

Single-voice: no reviewer personas, no self-orchestrated sub-agents (a CLI's parallel mode
is allowed only on read-only seats, for breadth). Bounded everything: worklog ~15 entries, the
reviewer eval set 8 cases, patch loops max 3 cycles. The hub stays under ~180 lines; growth
means a new reference file, not a longer hub.

## Maintaining this skill

Rules for editing the skill itself (moved out of `SKILL.md`: an agent running a phase never needs them).

- **Growth:** a new feature is a new or extended reference file plus one command-index line; the
  hub stays under ~180 lines.
- **Vendors:** only `ROUTING.md` and `ROUTING-NOTES.md` name vendors or models; no skill file names a CLI product
  (this README is reader-facing and exempt). Verify model names and efforts in the CLI's own
  picker before editing `ROUTING.md`.
- **Writing:** state each rule once, in one place. Phrase rules as the behaviour wanted, not the
  one banned. Define outcome, constraints and a checkable completion bar rather than every step.
  Reserve always/never for true invariants. Hunt sentences the model already obeys by default and
  delete them whole. Prefer a pretrained word (*grill*, *frontier*, *tracer bullet*, *seam*,
  *red → green*) over a sentence that re-explains it.
- **Approval:** the principle lives in `SKILL.md`, the phase → approval mapping in `ROUTING.md`.

## License

MIT — see `LICENSE` at the repo root.
