# jflow spec

The spec says **what** and **how we will know**. The builder decides how. Keep a line only if the
human would object to the builder choosing differently.

## 1. Ground

Read `AGENTS.md`, the code near the change, and any issue the human names. Look for
`.agents/skills/verify-*/`. Facts are your job: look up anything the repo, a command or a run can
answer, and leave only decisions for the human.

## 2. Grill the what

Ask in rounds. Each round holds every question whose prerequisites are settled, numbered, each with
your recommended answer, worded so "yes" accepts it. Then wait. Work outward from: who has the
problem, what they see, what good looks like, what must stay as it is, what is out of scope.

File paths, functions, libraries and test layout belong to the builder, so leave them out unless
they are a real constraint. Ask about a how only when it is costly to undo: a schema, a public
contract, a data migration, a new dependency, deleted data. Those go in **Ask first**.

Stop when you can predict the human's answer to your next three questions. If several rounds pass
and you still cannot, say what is missing. A very long grill means the scope is too big: propose a
split.

## 3. Draft the Proof table

Keep the table to about ten rows: one for each goal, plus the failures most likely to hurt a user,
such as losing data, showing wrong data as correct, or a break partway through. Rows say what to
observe, not how the code does it, because every row costs a proof on every check. Leave the repo's build, test and lint commands out of it: `jflow done` runs them. Each row
must be able to fail, by one of:

- a script, test or query with a pass or fail result;
- a flow driven with the repo's `verify-*` skill, ending in a state someone can observe;
- a measurement with a threshold.

Read the claim where the user meets it. A fully mocked test proves no goal. **Human checks** hold
what only a person can judge or do: taste, a trial with an outside tool, a doc that needs their
approval. They never count as proof. Prefer a stronger answer key
when one exists: the old system or saved good output beats a fresh description of what is right.

A row about a conclusion, such as a cause in a report, names the numbers that would disprove it:
"written down" proves a file exists and says nothing about whether the claim holds. Measured
2026-11-06: one such row passed while a fresh run contradicted its claim.

**Live steps.** When the change writes to real data or spends real money, find the **gate**: the
first live step that cannot be undone, or that removes a row's starting state. Name it under
Constraints. Everything before the gate gets checked first, because after it a bug has no way back
and a row's starting state may be gone. A row that only a step from the gate on can satisfy gets
Kind `live`; every other row must be provable before the gate. Measured 2026-11-06: a check run
after the live steps could not prove a guard, because the gap it refuses no longer existed.

When a row needs a surface the agent cannot drive, say what is missing. A repo with a user surface
and no `verify-*` skill gets `verify.create` first, because check has nothing to drive it with.

## 4. Run the table on the base commit

Run every row at `HEAD` before anything is built, and record `Base`:

- a `new` or `live` row must be `red`. One that passes proves nothing, so rewrite it.
- a `keep` row guards behaviour that exists today, and must be `green`.

A surface that does not exist yet counts as `red`. Keep any throwaway files out of the commit.

## 5. Play it back and write

Show the human the spec in chat and wait for an explicit yes. Then write `spec.md`, about one page,
from this exact template, commit it, then run `jflow.py next <slug>` and print its card. Done when
the spec is committed with `Status: ready`, and every row has a `Base` result.

```markdown
# <slug>
Status: ready
Base: <sha>

## Problem
<who meets it, what they see, the evidence>

## Goals
1. <an outcome someone else could check>

## Non-goals
- <what an eager agent would otherwise do>

## Constraints
- Must not break: <…>
- Ask first: <… | nothing>
- Gate: <the first live step that cannot be undone or removes a row's starting state | none>

## Proof
| # | Claim | Surface | Check | Pass signal | Kind | Base |
|---|---|---|---|---|---|---|
| 1 | <goal it proves> | <page, CLI, API, row> | <command or flow> | <what is observed> | new | red |

## Human checks
- <what only the human can judge or do | none>
```
