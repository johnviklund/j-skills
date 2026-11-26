---
name: roadmap
description: >
  The "roadmap", "roadmap item IDEA" and "roadmap tidy" commands; load this skill to run any of
  them. Keeps a repo's roadmap readable and fresh: "roadmap item IDEA" grills the why and writes
  one problem-first item, "roadmap tidy" finds stale, overlapping and conflicting items and asks
  before changing anything, bare "roadmap" shows Next up. Items sit in fixed groups under a short
  ordered Next up list, in a format that jflow spec reads; in GitHub mode the roadmap is the repo's
  open issues and the `next` label. Run only on one of those explicit
  messages; never on general questions about roadmaps, plans or ideas.
---

# roadmap

A roadmap answers two questions for a person who has just switched in: **where do I start**, and
**why is each item worth doing**. Every item starts from a **problem** with evidence, and names
the outcome in `PRODUCT.md` it moves. `PRODUCT.md` is the north star: the desired state, short and
readable. `DESIGN.md` says how the product is built. The roadmap only orders the steps toward that
state, so it points at both files and restates neither. An agent
handed a solution grills the how, while one handed a problem questions whether this is the right
fix, so the why is settled here, before `jflow spec` picks the item up.

Everything the human reads follows the Rules of the `plain` skill: invoke it once before the first
message. A question carries one decision, lettered options, and a ➡️ recommended option first,
worded so "yes" accepts it. Ask in numbered rounds and wait for the answers.

## Commands

| Message | What it does |
|---|---|
| `roadmap [FILE]` | Runs `next` and `check` below and shows both. Changes nothing |
| `roadmap item <idea> [FILE]` | Grills the why and writes one item: [references/item.md](references/item.md) |
| `roadmap tidy [FILE]` | Reviews the whole roadmap and proposes changes: [references/tidy.md](references/tidy.md) |

`FILE` defaults to `ROADMAP.md` at the repo root. Read the command's reference before editing.

## GitHub mode

A repo that runs jflow in issue and pull request mode keeps its roadmap on GitHub instead of in
`ROADMAP.md`. The skill is in GitHub mode when `git config jflow.mode` is `github` and no `FILE` is
named, or when the message says `--github`. Pass `--github` to the script in that case. Each open
issue is an item, and its labels place it:

| Column | Label | Holds |
|---|---|---|
| Next | `next` | At most five issues, the ones to start soonest |
| In flight | `ready-for-agent`, `in-progress` or `needs-human` | Issues jflow has picked up |
| Backlog | any other | Every other open issue |

The repo's `.github/workflows/board.yml` moves each card to its Kanban column from these labels, so
the skill changes labels and never touches the project board. An issue body holds the item's
fields as in *The file*, without `Status`: the issue's state and labels are its status. `check`
reports a body without `Problem:` or `Solved when:`, and without `Serves:` when a `PRODUCT.md`
exists. It also reports a `next` label left on an in-flight issue. Bare `roadmap` shows Next and
Backlog and those findings.

In GitHub mode `roadmap tidy` can also scan a wiki folder, set by the repo-local
`git config roadmap.wikiPath`, for pages changed since `git config roadmap.wikiLastScan`. It
reads them against `PRODUCT.md` and the open issues and proposes at most three updates, preferring a
scope note on an existing issue over a new Backlog issue. It moves `wikiLastScan` only after the
human has answered. [references/tidy.md](references/tidy.md) has the steps.

Opening an issue, commenting and changing a label are public writes. Each waits for the human's
explicit yes, like any change to the roadmap file.

## The file

The script parses this format, so it is **exact**. Free text may sit between the title and
`## Next up`, for a goal or a link to a plan. Longer prose, such as plans and decisions, lives in its
own document and the preamble links to it.

```markdown
# Roadmap
Updated: <YYYY-MM-DD>

## Next up
1. <slug> · <why it goes before the next line, one line>

## Features
### <slug> · <the outcome, a few words>

- **Status:** open
- **Problem:** <who meets it, what they see, what it costs them, the evidence>
- **Impact:** <what gets better once it is solved, and by how much, in the unit similar items use>
- **Why now:** <what waiting costs, or what it blocks>
- **Solved when:** <what someone could observe once it is done>
- **Out of scope:** <what an eager agent would add>
- **Budget:** <the most this is worth spending, in the units this roadmap uses>
- **Run:** <jflow | plain> · <repo>
- **Serves:** <an outcome heading in PRODUCT.md>
- **After:** <slugs this waits for | none>
- **Open for spec:** <questions for jflow spec, fix ideas among them | none>
```

**Write for a reader.** Each field is a list line with a bold label, so a rendered roadmap shows
one field per line instead of one long paragraph. Keep a field to one or two sentences; a
`Problem` that needs more links to the issue, note or measurement that holds it. A blank line
separates an item's heading from its fields and from the next item. Older roadmaps write fields as
plain `Field: value` lines: `check` still reads them and reports them as stale, and `tidy`
converts them.

**Fields.** `Status`, `Problem`, `Impact`, `Solved when`, `Budget` and `Run` are required, and so is
`Serves` whenever a `PRODUCT.md` sits beside the roadmap; the rest are optional, in this order.
A field runs on over lines indented by two spaces. A slug is kebab-case
and is also the jflow run's slug, which is how the script sees a run's progress.

**The item holds the problem, not the fix.** `Problem` names who meets the problem, what they see,
what it costs and the evidence: a count, a measurement, a quote, a commit. Choosing the fix is
jflow spec's job, after it has grilled the problem, so an idea for a fix goes in `Open for spec` as
a question, unranked ("would a nightly re-sync be enough?"). `Solved when` names something
observable; jflow spec makes it the first Proof row. `Budget` is the most the item is worth, not an
estimate of a fix nobody has chosen.

**Impact and Why now are what you rank by.** `Impact` says what gets better and by how much: "p95
load of the overview 6 s → under 1 s, every user, every visit". Items that move the same thing use
the same unit, such as seconds of p95, hours a week or wrong rows a month, so a reader can compare
them; an estimate starts with `~` and says what it rests on. `Why now` says what waiting costs,
such as a deadline, a cost that grows, or an item that is blocked until this one is done. An item
whose waiting costs nothing says so, and waits.

**Status** is `open`, `started`, `blocked: <why>` or `done <YYYY-MM-DD> <sha>`. A done item moves
to `<NAME>_ARCHIVE.md` beside the roadmap, under one `## Done` heading, newest first, and leaves
Next up, so the roadmap holds only open work. The `<sha>` is the change's last commit before this roadmap edit. The heading keeps item headings one level below it, which markdown
linters require.

**Groups** are fixed, so items never drift into new ones. Each item sits in the one group of its
main outcome, and empty groups are left out:

| Group | Holds |
|---|---|
| Features | New behaviour a user asks for |
| Bugs | Something that works wrong today |
| Design | What a user sees and how it feels: UI and UX |
| Architecture | Structure, data, contracts and dependencies other code relies on |
| Tooling | Skills, scripts, CI and how the work gets done |
| Measurement | Evals, metrics and the data collected to judge work |

**Order is priority.** Within a group, items sit highest priority first: the most `Impact` for
the `Budget`, then the costliest wait. So the top of Architecture answers "which change does most
for performance". **Next up** holds at most five items, in the order to start them, across groups.
Each line says why it goes before the line below it: more impact, a costlier wait, or that it
unblocks it. The first is startable today: everything in its `After` is done. Every other open item
waits in its group.

**Serves** names a heading in `PRODUCT.md`, normally one of the `###` outcomes under its
`## The desired state` section. An item that moves no outcome is off course, and an outcome that
no open item moves is a gap; `check` reports both. A repo with no `PRODUCT.md` gets one from the
`bootstrap` skill.

The same item text works as a ticket body: the heading becomes the title.

## The script

```sh
python3 <skill>/scripts/roadmap.py check [FILE] [--repo PATH ...] [--product PATH] [--github]
python3 <skill>/scripts/roadmap.py next [FILE] [--github]
python3 <skill>/scripts/roadmap.py wiki [--wiki PATH] [--since YYYY-MM-DD]
```

`<skill>` is this skill's absolute folder; Python 3.9 or later, standard library only. `check`
prints `error:` lines for format problems and exits 1, and `stale:` lines for freshness findings,
which leave the exit at 0. Pass `--repo PATH` for each local repo that an item's `Run` names, so the
script can see its jflow runs. `--product PATH` names the north star when it is not `PRODUCT.md`
beside the roadmap. With `--github` both commands read open issues through `gh` and write nothing;
a missing or logged-out `gh` stops them with one `error:` line. `wiki` lists the wiki pages that
`roadmap tidy` should read: see [references/tidy.md](references/tidy.md).

## Changing the file

- **Facts are yours, decisions are the human's.** Look up what the repo, git or a run can answer.
  Every change to what the roadmap says waits for the human's yes, because it holds direction they
  committed to. A typo or a format fix that keeps the meaning is a fact.
- **Code can read the roadmap.** Before changing the file's layout, search the repo for its file
  name. A script that parses it changes in the same commit, with its tests run.
- **Finish.** Set `Updated:` to today, run `check` until it prints no `error:` line, commit the
  roadmap and its archive alone, then follow the repo's own instructions for after a roadmap change.
  End by printing `next` as it stands.
