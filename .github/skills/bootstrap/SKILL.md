---
name: bootstrap
description: >
  The "bootstrap" and "bootstrap update" commands for a repo's steering docs, not for setting up an
  app or framework; load this skill to run either. Writes the steering docs: PRODUCT.md, the short north star of the desired state; DESIGN.md, how it is built
  and how it looks; ROADMAP.md, the ordered steps toward that state; and TODO.md, the scratchpad.
  "bootstrap [PRD]" creates them from a PRD or splits existing long docs into them; "bootstrap
  update CHANGE" changes the north star or the design on purpose. jflow and roadmap read these
  docs to stay on course. Run only when the message itself starts with "bootstrap". A message that
  starts with "workflow" belongs to the workflow skill, and a question about bootstrapping an app,
  framework or project template is not this skill.
---

# bootstrap

Every repo carries four **steering docs**. They steer development of that repo: `jflow` and
`roadmap` read them so specs and items stay inside the frame, and nothing else does. Each meaning
has one home, because when the same sentence sits in two docs, one of them is wrong.

| Doc | Holds | Size |
|---|---|---|
| `PRODUCT.md` | The **north star**: what it is, who it is for, the desired state as a few outcomes, how we know it works, principles, what we will not build, open decisions | About one page, at most ~80 lines |
| `DESIGN.md` | How it is built and how it looks: the parts and how they fit, key decisions with their reasons, data and storage, the UI system when there is a UI | As long as it needs, by heading |
| `ROADMAP.md` | The order of the steps toward the desired state, in the `roadmap` skill's format; every item `Serves` an outcome in `PRODUCT.md` | Open items only |
| `TODO.md` | Ideas not yet decided, one short line each | Small; never a roadmap |

`PRODUCT.md` describes where the repo is going, in words a person reads in two minutes. It holds no
file paths, commands, field names or implementation history; those are `DESIGN.md`'s, the code's or
git's. Each outcome is a `###` heading under `## The desired state`, because roadmap items name
these headings and the `roadmap` check matches them.

Everything the human reads follows the Rules of the `plain` skill: invoke it once before the first
message. A question carries one decision, lettered options and a ➡️ recommended option first.

## bootstrap [PRD]

1. **Ground.** Find the source: the named PRD, a `PRD.md` at the root, or the repo's existing docs
   when they are long or mixed, such as a plan that holds vision, design and roadmap together. With
   no source, ask; a north star written from nothing is invented. Read the source in full, then
   `AGENTS.md`, `README.md`, any decision log and any existing steering doc. A `README.md` whose
   purpose differs from the source is a sign of drift: raise it in step 2. Done when every paragraph of the source
   has a home in the table above, or is marked history.
2. **Ask about identity, in one round.** Ask only what the source leaves open about the desired
   state: who it is for, which outcomes matter, what is the first implementation rather than the
   goal, the non-goals, and whether there is a UI. Order and sizing of work can wait.
3. **Draft** the four docs from the templates below, in the working tree, uncommitted. Every claim
   traces to the source or to a human answer; a claim with no source becomes a question, never a
   line. A roadmap conversion follows the `roadmap` skill's `tidy` reference, and each item gets
   `Serves`. Keep existing docs' content by moving it, never by rewriting what it says.
4. **Play back.** Show `PRODUCT.md` in chat in full, and the headings of the other docs with one
   line each on what moved where. Then test the direction: give three tempting moves that would
   pull the product off course, drawn from the source's own tensions, one at a time, each with the
   strongest case for and against and the principle it presses on. Fold the human's answers in.
5. **Write.** After an explicit yes: run the `roadmap` skill's `check` until it prints no `error:`
   line. Add the pointer block below to `AGENTS.md`, creating the file if missing. Bring
   `README.md` in line: its purpose matches `PRODUCT.md`, and it points to the steering docs instead
   of restating them. A repo with a decision log keeps it as the home for decisions, and the source's
   decisions move into it as dated entries. Retire the
   source: a PRD moves to `docs/archive/PRD-<date>.md`; a long doc that was split becomes a
   one-paragraph pointer, or is deleted when the human says so. Commit in one commit, or open a PR
   when the repo's `main` takes changes only through PRs.

Done when the four docs are committed, `check` passes, and every part of the source has a home or
was dropped with the human's yes. On a repo whose steering docs already exist and keep to their
sizes, say so and offer `bootstrap update` or `roadmap tidy` instead.

## bootstrap update CHANGE

A deliberate change to the north star or the design, such as a new outcome, a dropped principle or
a decision reversed. `roadmap item` sends an idea here when it moves no outcome.

1. Read `PRODUCT.md`, `DESIGN.md` and `ROADMAP.md`, and state the change as a redline: the exact
   lines before and after.
2. List what it touches: roadmap items whose `Serves` changes or goes off course, decisions in
   `DESIGN.md` that no longer hold, and lines in `README.md` that no longer match.
3. Wait for an explicit yes on the redline, apply it, run the `roadmap` check, and commit the docs
   together. Done when the redline is committed and the check prints no `error:` line.

## Templates

`PRODUCT.md` is a **default**: adapt the outcomes, keep the section names that `roadmap` reads.

```markdown
# <Name>

<One paragraph: what it is and who it is for.>

## The desired state

### <Outcome, a few words>
<Two to four sentences: what is true for the user when this is reached.>

## How we know it works
- <A measure someone could read, with its direction: fewer, faster, none>

## Principles
- **<Rule.>** <Why, in one sentence.>

## Not building
- <What an eager agent would add, and why not>

## Open decisions
- <A product question still open | none>
```

`DESIGN.md` is a **default**: headings follow the parts of the system. With no UI, it says so in
one line under `## UI`.

```markdown
# <Name>: design

How <Name> is built. The desired state is in [PRODUCT.md](PRODUCT.md).

## Parts
## Decisions
| # | Decision | Why |
## Data and storage
## UI
```

`TODO.md` starts as a header line, "Ideas not yet decided. Nothing here is committed; `roadmap item`
turns one into an item.", followed by one line per idea.

The `AGENTS.md` pointer block is **exact**:

```markdown
## Steering docs

`PRODUCT.md` is the north star, `DESIGN.md` says how it is built, `ROADMAP.md` orders the next steps
and `TODO.md` holds undecided ideas. Specs and roadmap items stay inside them; a change to
`PRODUCT.md` or `DESIGN.md` waits for the human's yes.
```
