---
name: roadmap
description: >
  The "roadmap", "roadmap item IDEA" and "roadmap tidy" commands; load this skill to run any of
  them. Keeps a repo's roadmap readable and fresh: "roadmap item IDEA" grills the why and writes
  one problem-first item, "roadmap tidy" finds stale, overlapping and conflicting items and asks
  before changing anything, bare "roadmap" shows Next up. Items sit in fixed groups under a short
  ordered Next up list, in a format that jflow spec reads. Run only on one of those explicit
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

## The file

The script parses this format, so it is **exact**. Free text may sit between the title and
`## Next up`, for a goal or a link to a plan. Longer prose, such as plans and decisions, lives in its
own document and the preamble links to it.

```markdown
# Roadmap
Updated: <YYYY-MM-DD>

## Next up
1. <slug> · <why it is next, one line>

## Features
### <slug> · <the outcome, a few words>
Status: open
Problem: <who meets it, what they see, what it costs them, the evidence>
Why now: <what changes if we wait>
Options: ➡️ a) <chosen> · b) <other> · c) do nothing. <why a wins>
Solved when: <what someone could observe once it is done>
Out of scope: <what an eager agent would add>
Budget: <size, in the units this roadmap uses>
Run: <jflow | plain> · <repo>
Serves: <an outcome heading in PRODUCT.md>
After: <slugs this waits for | none>
Open for spec: <decisions left for jflow spec | none>
```

**Fields.** `Status`, `Problem`, `Solved when`, `Budget` and `Run` are required, and so is
`Serves` whenever a `PRODUCT.md` sits beside the roadmap; the rest are optional, in this order.
A field runs on over lines indented by two spaces. A slug is kebab-case
and is also the jflow run's slug, which is how the script sees a run's progress.

**Problem holds no solution.** It names who meets the problem, what they see, what it costs and the
evidence: a count, a measurement, a quote, a commit. A solution idea goes in `Options`, next to
"do nothing". `Solved when` names something observable; jflow spec makes it the first Proof row.

**Status** is `open`, `started`, `blocked: <why>` or `done <YYYY-MM-DD> <sha>`. A done item moves
to `<NAME>_ARCHIVE.md` beside the roadmap, under one `## Done` heading, newest first, so the
roadmap holds only open work. The heading keeps item headings one level below it, which markdown
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

**Next up** holds at most five items, in the order to start them. The first is startable today:
everything in its `After` is done. Every other open item waits in its group.

**Serves** names a heading in `PRODUCT.md`, normally one of the `###` outcomes under its
`## The desired state` section. An item that moves no outcome is off course, and an outcome that
no open item moves is a gap; `check` reports both. A repo with no `PRODUCT.md` gets one from the
`bootstrap` skill.

The same item text works as a ticket body: the heading becomes the title.

## The script

```sh
python3 <skill>/scripts/roadmap.py check FILE [--repo PATH ...] [--product PATH]
python3 <skill>/scripts/roadmap.py next FILE
```

`<skill>` is this skill's absolute folder; Python 3.9 or later, standard library only. `check`
prints `error:` lines for format problems and exits 1, and `stale:` lines for freshness findings,
which leave the exit at 0. Pass `--repo PATH` for each local repo that an item's `Run` names, so the
script can see its jflow runs. `--product PATH` names the north star when it is not `PRODUCT.md`
beside the roadmap.

## Changing the file

- **Facts are yours, decisions are the human's.** Look up what the repo, git or a run can answer.
  Every change to what the roadmap says waits for the human's yes, because it holds direction they
  committed to. A typo or a format fix that keeps the meaning is a fact.
- **Code can read the roadmap.** Before changing the file's layout, search the repo for its file
  name. A script that parses it changes in the same commit, with its tests run.
- **Finish.** Set `Updated:` to today, run `check` until it prints no `error:` line, commit the
  roadmap and its archive alone, then follow the repo's own instructions for after a roadmap change.
  End by printing `next` as it stands.
