# Maintaining the workflow skill

Rules for editing the skill itself. An agent running a step never needs this file. For using the
skill, see [`README.md`](README.md).

## File layout

| File | Role | You edit it? |
|---|---|---|
| `SKILL.md` | The hub: invocation, runs and state machine, seats and invariants, reporting rule, command index | No |
| `ROUTING.md` | **Your mapping**: seat to vendor, model, effort and context, the trial column, fallbacks, and effort and approval per step. The closing card reads it every step, so keep it small | **Yes, this is the whole setup** |
| `ROUTING-NOTES.md` | How models earn seats, the upkeep loop and mode notes. Only `checkup` reads it | Rarely |
| `references/*.md` | Full instructions per command, one loaded per invocation | No |
| `scripts/check-run.py` | Checks a run folder against the shapes in `SKILL.md` and `references/`: headers, budgets, ticket fields, behaviour coverage, review dispositions, layout. Slop guards (per-ticket `Budget:` and overruns, test-to-code ratio, operator `Risk:`, review `Size:`, wrap `Retired:`, tests that read run folders) fire only on artifacts created from `SLOP_SINCE`; their thresholds are the constants at the top. Steps run it before marking a file `complete`. `checkup` runs it with `--all`. Its tests: `python3 -m unittest discover -s scripts/tests` | No |
| `SKILL-IMPACT.md` | Log of every skill change and what the runs after it showed. Its `Mode:` line sets whether skill edits are autonomous or approved | The mode line, and accepting or rejecting rows |

## Rules for edits

- **Growth.** A new feature is a new or extended reference file plus one command index line. The
  hub stays under about 180 lines.
- **Vendors.** Only `ROUTING.md` and `ROUTING-NOTES.md` name vendors or models. No skill file
  names a CLI product. A brand name in the wrong place is a bug. The skill uses generic verbs
  such as *reset*, *compact*, *context meter*, *model picker* and *explicit invocation*, and the
  README cheat sheet holds the real commands. The README is for people and may name tools.
  Check model names and efforts in the CLI's own picker before you edit `ROUTING.md`.
- **Writing.** State each rule once, in one place. Phrase rules as the behaviour wanted, not the
  one banned. Define the outcome, the limits and a checkable bar for done, rather than every step.
  Keep always and never for true invariants. Delete sentences the model already obeys by default.
  Prefer a word the model already knows, such as *grill*, *frontier*, *tracer bullet*, *seam* or
  *red to green*, over a sentence that explains it.
- **Approval.** The principle lives in `SKILL.md`. The mapping from step to approval lives in
  `ROUTING.md`.
- **Retiring a command.** Grep the whole folder, `ROUTING.md` and the README included, or you
  leave dangling references.

## Design limits

The skill speaks in one voice. It has no reviewer personas and starts no sub-agents of its own.
A CLI's parallel mode is allowed only for read-only seats, to cover more ground.

Everything is bounded: the worklog keeps about 15 entries, the reviewer exam set holds at most 10
cases, and a patch loop runs at most three cycles.

Every command takes an explicit slug, and there is no hidden current run. That lets a
coordinating agent hand runs to other agents, several at once, with git and the run folders as
the only shared state. Nothing depends on that yet, but nothing blocks it.

## Run folder rules

Every file in a run opens with a five-line header. The state machine reads it rather than
guessing from which files exist:

```
Command: workflow plan
Created: 2026-07-28
Base:    <git sha when the file was created>
Inputs:  .workflow/<slug>/brainstorm.md @ <its own Base sha>
Status:  drafting        # becomes complete when the step writes its closing section
```

`Status: drafting` always means resume that step. So a half-written plan never passes for a
finished one, and a review that died at 90% looks different from one that never ran. `Inputs`
and `Base` let a step notice that its input went stale and ask before building on it.

Two more rules keep the archive honest:

- **Receipts and code.** `*.md` and `*.txt` files, and a run's `screens/`, `prototypes/` and
  `understand/` folders, are receipts. Anything else, such as a script in `.workflow/` or a
  config in `docs/`, is code. Code must be reviewed and cannot ship through wrap's commit.
- **Freshness is per file.** A plan is stale when any file it names changed since its `Base`,
  other than through its own ticket commits. A parked plan gets audited again, not executed.

Runs are never deleted. Grounding reads only live runs, so the archive costs nothing. A finished
run is read through its `wrap.md` alone.

When a reviewer misses a P0 or P1 bug, wrap can save the diff as an exam case in the private
`j-skills-evals` repo, as `strict-reviewer/missed-<topic>.md`. The repo is private because cases
copy code from other repos.

## Context budget

A run's reading cost repeats every step, so the skill keeps it small. `PRODUCT.md` and
`DESIGN.md` still guard against drift. They are read in part, never skipped.

**What each step reads.** The rule lives in the *Grounding* section of `SKILL.md`.

| Tier | Files |
|---|---|
| Always | The run's live files, but only the current cycle of `review.md` and its `## Resolved` table. `ROUTING.md`, `AGENTS.md`, the `MEMORY.md` index, `git log --oneline -15` and `git status`. A `memory/` page only when its "Applies when" line matches |
| Targeted | `PRODUCT.md` and `DESIGN.md`: headings first, then only the sections the brief or ticket touches, recorded as `Docs read:`. A full read only for new product direction, `realign`, a proposal to depart from the design, or a ticket that might contradict them. `TODO.md` and `ROADMAP.md` only in brainstorm, wrap and `todo` |
| Never by default | `MEMORY_ARCHIVE.md`, `TODO_ARCHIVE.md`, `ROADMAP_ARCHIVE.md`, `WORKLOG.md` past its latest entry, other runs' folders, `.workflow/archive/`. Grep these and read the matching lines |

**Size budgets.** Check with `wc -c`, and flag a file that passes its budget.

| File | Budget |
|---|---|
| `SKILL.md` | about 10 KB, under about 180 lines |
| `ROUTING.md` | about 5.5 KB. Trial and upkeep notes go in `ROUTING-NOTES.md` |
| one step reference | about 10 KB |
| `brainstorm.md`, `plan.md`, `review.md`, finished `wrap.md` | about 80, 120, 100 and 40 lines |
| the repo's `TODO.md` and `ROADMAP.md` | about 15 KB and 12 KB. Wrap flags them and proposes archiving, never deletes |
| a committed receipt | a few KB of numbers and checksums, not data |

So plan, execute and review each read `SKILL.md`, `ROUTING.md` and one step reference, about
22 to 25 KB, plus the repo's `AGENTS.md`, the `MEMORY.md` index and the run's live files. When a
change adds a rule every step reads, remove or move another one.
