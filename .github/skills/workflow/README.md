# workflow

A coding workflow for one developer working with CLI coding agents. It takes a task through five
steps, and a model from another vendor reviews the code. It works in Claude Code, Codex CLI and
GitHub Copilot CLI. Version 2.1.

## The steps at a glance

| Step | What happens | You do |
|---|---|---|
| Brainstorm | The agent asks questions until the task is clear, then writes a short brief. It builds throwaway sketches when trying beats asking | Answer questions, confirm the behaviours |
| Plan | The agent checks the brief against the real code and writes usually 2–5 tickets, at most eight. Each ticket says how to prove it is done | Approve the ticket list |
| Execute | One ticket at a time, up to 3 tickets per session: write a failing test, make it pass, commit | Try each UI change before its commit. Run the live or risky steps |
| Review | A model from the other vendor reviews the result and rates findings P0 to P3. Fixes go through at most two patch cycles | Choose which P2 and P3 findings to fix |
| Wrap | Final checks, push, docs updated, lessons saved to memory, the run closed | Nothing, unless asked |

Every step ends with a **closing card**. It says whether to reset the session, which model and
effort to pick, what to read, and the exact line to send next. Reset the session when the card
says so. A reset loses nothing, because each step reads its state back from files.

## One run, start to finish

```text
workflow brainstorm auth-refresh
workflow plan auth-refresh
workflow execute auth-refresh
workflow review auth-refresh
workflow wrap auth-refresh
```

The run name, here `auth-refresh`, is called the slug. With only one live run you can leave it
out. Only a message that starts with `workflow <command>` or `/workflow <command>` starts the
skill. Saying "plan" or "review" in passing does not.

## Commands

| Command | What it does |
|---|---|
| `workflow brainstorm <slug>` | Creates `.workflow/<slug>/`, asks questions with a recommended answer for each, and writes the brief to `brainstorm.md`. It also checks `TODO.md` for related items |
| `workflow improve <feature> - goal: <goal>` | A brainstorm that starts from an audit of the existing code |
| `workflow plan` | Writes `plan.md` with usually 2–5 tickets, at most eight, after you approve them |
| `workflow execute` | Runs the next ready tickets, up to 3 tickets per session, and saves progress after each one |
| `workflow review` | Writes `review.md`. A re-review looks only at the fix diff |
| `workflow wrap` | Checks, commits and pushes, updates docs, saves lessons, adds a worklog entry and closes the run |
| `workflow park [slug]` | Sets a run aside at any step. Nothing is deleted |
| `workflow status` | Lists every live and parked run and its next command |
| `workflow next` | Shows the closing card again. A bare `workflow` does the same |
| `workflow todo <idea>` | Adds an idea to `TODO.md` |
| `workflow log`, `workflow learn` | Adds a worklog entry, or saves one lesson |
| `workflow bootstrap` | Sets up `AGENTS.md`, `MEMORY.md`, `TODO.md` and repo conventions in a new project |
| `workflow realign` | Checks `PRODUCT.md` and `DESIGN.md` against what shipped, and proposes changes for you to approve |

## Where it stops for you

The agent works on its own between these points:

- It asks before it starts work that is unclear or risky. Each question is one decision, with
  lettered options and a recommended default.
- You approve the plan before any code is written.
- You try every UI change before it is committed.
- Steps that touch live systems or cannot be undone become **operator tickets**. The agent
  prepares the commands, you run them, and a saved receipt shows they ran.
- Wrap refuses to ship code the review never saw.

## Seats and models

The skill never names a model. It names **seats**, which are roles: brainstorm partner, default
executor, heavy executor, mechanical lane and strict reviewer. `ROUTING.md` maps each seat to a
vendor, a model and an effort level. To change models, you edit that one file.

The strict reviewer should come from a different vendor than the model that wrote the code. Each
run records who wrote it. If the reviewer finds it is the same vendor, it says so in `review.md`
and marks the review as degraded.

The `ROUTING.md` in this repo is the author's own setup. OpenAI models write the code and
Anthropic models brainstorm, plan and review.

## The run folder

Each run lives in `.workflow/<slug>/`. The folder is tracked in git and kept after wrap as the
run's history. Subfolders appear only when a run needs them.

```text
.workflow/auth-refresh/
  brainstorm.md    the brief: problem, outcome, behaviours, decisions, test seams, out of scope
  plan.md          findings, the tickets and their status, risks
  patch_plan.md    fix tickets during a patch cycle, deleted at wrap
  review.md        the current findings and verdict, plus a table of earlier cycles
  learnings.md     lessons from the run, each marked with where it was saved
  wrap.md          the run's short summary, the only file later runs read
  receipts/        test output, diffs and operator receipts
  screens/         before and after screenshots of UI tickets
  notes/           investigations, audits, runbooks, drafts
  scripts/         one-off scripts, reviewed like any other code
  data/            small frozen inputs and outputs
  prototypes/      brainstorm's throwaway sketches, never shipped
  understand/      the explainer page from the understand skill
```

Each file opens with a short header that says which step wrote it and whether it is finished.
A file marked `Status: drafting` means that step should resume. It never means move on.

Beyond the run folder, a run writes commits, `WORKLOG.md`, `MEMORY.md` and its `memory/` pages,
`TODO.md` and product docs.

## Several runs at once

```text
workflow brainstorm export-csv    # good idea, not now: it ends parked
workflow brainstorm rate-limits   # a second live run
workflow status                   # one line per run with its next command
workflow park rate-limits         # set it aside
workflow plan export-csv          # to unpark, run the step it stopped at
```

Each idea has one home. `TODO.md` holds ideas nobody has brainstormed yet. A parked folder holds
ideas that were brainstormed and set aside. A live folder is work in progress.

Park before planning when you can. A plan goes stale as soon as a file it names changes, and
the agent then makes you plan again.

## Install

The skill is a plain folder. Keep one copy and link the other CLIs to it:

```bash
mkdir -p .agents/skills && cp -r workflow .agents/skills/workflow
mkdir -p .claude/skills && ln -s ../../.agents/skills/workflow .claude/skills/workflow
mkdir -p .codex/skills  && ln -s ../../.agents/skills/workflow .codex/skills/workflow
git add .workflow/   # runs are tracked, so never gitignore .workflow/
```

Copilot CLI reads `.agents/skills/` directly. Codex CLI before 0.160 reads only
`.codex/skills/` and `~/.codex/skills/`, so it needs the link.

| CLI | Project folder | Personal folder | Check it loaded | Start it with |
|---|---|---|---|---|
| Claude Code | `.claude/skills/workflow/` | `~/.claude/skills/workflow/` | `/workflow status` | `/workflow` |
| Codex CLI | `.codex/skills/workflow/` | `~/.codex/skills/workflow/`, or `$CODEX_HOME/skills/` | `/skills` | `$workflow` |
| Copilot CLI | `.github/skills/`, `.claude/skills/` or `.agents/skills/` | `~/.copilot/skills/` or `~/.agents/skills/` | `/skills list` | matched by description, or `/<plugin>:workflow` as a plugin |

Then:

1. Rewrite `ROUTING.md` for your vendors and models. That is the whole setup.
2. Run `workflow status` in each CLI to check it loads, and `workflow next` to check it reads
   `ROUTING.md`.
3. Do one toy run, `workflow brainstorm hello` through `workflow wrap hello`. Check that
   `.workflow/hello/` is committed with `Status: done`.

Skill discovery changes between CLI versions. `/skills` in Codex and Copilot and `/doctor` in
Claude Code show what your machine actually loaded. The tables were checked against Codex CLI
0.159 and Copilot CLI 1.0.91. If Codex ignores the skill, look for a `[[skills.config]]` entry in
`~/.codex/config.toml` that disables it.

To update, pull or re-copy the folder, but keep your own `ROUTING.md`, `ROUTING-NOTES.md` and
`SKILL-IMPACT.md`. Then run `/skills reload` in Copilot CLI, or restart Codex and Claude Code,
and repeat the smoke test.

## CLI cheat sheet

The skill uses generic words such as *reset* and *model picker*. This table gives the real
command in each CLI. Commands change, so check each one against the CLI's own `/` menu.

| CLI | Serves | Reset | Compact | Context meter | Model picker | Start the skill | Extra modes |
|---|---|---|---|---|---|---|---|
| Codex CLI | OpenAI models | `/new` or `/clear` | `/compact` | `/status` | `/model`, or `model_reasoning_effort` in `~/.codex/config.toml` | `$workflow` | `/goal` for autonomy, `/fast` for speed, `ultra` where the model has it |
| Copilot CLI | Both vendors | `/clear` | `/compact`, automatic near 80%: reset at a step boundary before then | `/context` | `/model`, or `--reasoning-effort` | matched by description, or `/<plugin>:workflow` | none by default |
| Claude Code | Anthropic models | `/clear` | `/compact` | `/context` | `/model` | `/workflow` | `/effort ultracode`, and sub-agents for read-only seats |

The skill has no compact command. A reset is safe at any point, so it replaces compaction.

## Companion skills

These live in the same repo and plug into the workflow:

| Skill | What it does for a run |
|---|---|
| `memory.remember` | At wrap, saves each lesson as a `memory/` page. A lesson seen three times moves into a skill |
| `memory.compact` | Proposes merges and removals for memory pages that overlap or went stale |
| `checkup` | A read-only health report. It also compares models and skill changes using worklog numbers |
| `evals` | Tests a reviewer model on up to ten diffs with known bugs, before it takes the reviewer seat |
| `retro` | Finds where a run or session lost time and suggests fixes |
| `understand` | After wrap, writes a cited HTML page that explains the run |

## Trying a new model or a skill change

Nothing is benchmarked up front. Changes are tried on real runs.

- **A new model.** Put it in the seat's Trial column in `ROUTING.md`. The card shows it, and
  wrap records it in the worklog. After two runs, `checkup seats` compares it with the current
  model, and you keep it or drop it.
- **A skill change.** The change gets a `trialing` line in `SKILL-IMPACT.md`. `checkup` compares
  the runs before and after. If the runs got worse, revert the commit and log why.

The first line of `SKILL-IMPACT.md` sets who applies skill edits. With `Mode: autonomous`,
`memory.remember` commits them directly. With `Mode: approve`, it writes `SKILL.md.proposed`
next to the skill, and you accept it with `mv`.

## Moving from v1

In v1, `.workflow/` held one flat set of files. Move them into a run folder and remove
`.workflow/` from `.gitignore`:

```bash
mkdir .workflow/<slug> && git mv .workflow/*.md .workflow/<slug>/
```

Then run `workflow status`. A flat `MEMORY.md` keeps working until `memory.compact` splits it
into pages.

## Changing the skill

[`MAINTAINING.md`](MAINTAINING.md) has the rules for editing the skill: the file layout, size
budgets, the vendor-name rule and the design limits.

## License

MIT, see `LICENSE` at the repo root.
