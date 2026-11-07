---
name: jflow
description: >
  Short path for shipping a code change: one session writes a spec with a Proof table of what a
  pass looks like, one session builds it, and a fresh session proves it on the real app and attacks
  what the table never asked. Commands: spec, build, check, done; bare "jflow SLUG" says what is
  next. Run only on an explicit "jflow COMMAND SLUG" or "/jflow COMMAND SLUG" message; never on
  casual mentions of specs, builds, proof or review.
---

# jflow

**Spec, build, check, ship.** A fresh agent proves the change on the real thing against an answer
key the builder did not write, then attacks what that key never asked. That evidence, not a
discussion of the diff, decides whether the work is done. The human decides what to build, the
builder decides how, and the checker decides whether it works.

Everything the human reads follows the Rules of the `plain` skill: invoke it once before the first
message. A question carries one decision, lettered options and a ➡️ recommended option first.

## Steps and seats

| Command | Model · effort | Session | Reference |
|---|---|---|---|
| `jflow spec <slug>` | Opus 5.5 · high | fresh, with the human | [references/spec.md](references/spec.md) |
| `jflow build <slug>` | Opus 5.5 · high | fresh; the **builder session**, kept for every fix | [references/build.md](references/build.md) |
| `jflow check <slug>` | GPT-6.1 Sol · high | fresh for each check | [references/check.md](references/check.md) |
| `jflow done <slug>` | same model, builder session | the builder session | [references/done.md](references/done.md) |

Picker IDs: `claude-opus-5.5`, `gpt-6.1-sol`. To change a
seat, edit this table.

**Independence.** Check runs on a different vendor from the builder, because two sessions of one
vendor share blind spots. With an OpenAI builder, check moves to Opus 5.5 · high. A session on the
wrong vendor says so in its first line and in its receipt, then carries on. Measured 2026-11-04:
Terra gave up when it had to write a driver, so this seat stays on Sol.

A receipt's own commit moves `HEAD`, so "changed" always means code: `.jflow/` files do not count.

Read the one reference for the command before opening anything in `.jflow/`, because check
starts blind to part of that folder. Its completion criterion ends the step.

## The run: `.jflow/<slug>/`

Tracked in git. A separate root from `.workflow/`, so no other skill's state or hook reads it.

```text
.jflow/<slug>/
  spec.md             the spec and Proof table, written by spec and read-only afterwards
  notes.md            the builder's judgement calls and anything left open, a few lines
  drive.py            the checker's driver, when a row needs one: one file, reused by later checks
  receipts/check-N.md one per check, numbered from 1
  run.jsonl           one line per step, written by scripts/jflow.py: the run's numbers
```

Commit only these files. Raw output goes to a temp folder: measured 2026-11-05, committed evidence
was 5,769 of the 6,850 lines one run added.

`spec.md` is the answer key. Only `jflow spec`, with the human's confirmation, changes it, and
every row then runs again.

**Accepted.** When the human accepts a missed bar, an unproved row or a defect in so many words,
the session they said it to adds one line under `## Accepted` at the end of `spec.md`, in its own
commit named `jflow accept <slug>`, and no row runs again. The bar stays as written, so the record
shows what was missed. An accepted item is no longer open.

```markdown
## Accepted
- Row 3 · 254 of 300 against a bar of 255 · "<the human's words>" · <date> · <sha it applies to>
```

## What is next

Bare `jflow <slug>` reads the run folder and prints the card for the first row that holds.

| State | Next |
|---|---|
| no `spec.md`, or `Status: drafting` | `jflow spec` |
| `Status: ready`, no commit since `Base` | `jflow build` |
| code changed since the newest check receipt's sha, or no receipt yet | `jflow check` |
| newest check receipt has BROKEN rows or defects still open | back to the builder session with that receipt |
| newest check receipt has BLOCKED or UNREACHABLE rows still open | the human decides, per `references/check.md` |
| newest check receipt has WAITING rows, and `notes.md` has no `Live done:` line | the builder session runs the live steps, per `references/build.md` |
| newest check receipt has WAITING rows | `jflow check` |
| otherwise | `jflow done` |
| `Status: done` | nothing; say so |

**Checks are capped, because a loop that has not converged needs a person.** A change gets three
checks at most, and a check that only reruns BLOCKED or WAITING rows does not count, since no fix
went in. At the cap, stop and give the human what is open.

## The closing card

Every step ends with this as the turn's last output, fence included: one line of text, then the
message alone in its own code block, so the human can copy it. A turn waiting for the human's answer
ends on the question.

````markdown
Model: <model · effort>. Session: <fresh | builder session>.

```text
<exact message to send>
```
````

The session running `jflow check` gives the builder the receipt path in the message:
`Fix .jflow/<slug>/receipts/check-2.md, then print the card.`

In Codex, run check with `-c sandbox_workspace_write.network_access=true`: measured 2026-11-04 on
Codex 0.166, a local test client hangs in the default sandbox.

Before the commit, record the step:
`python3 <skill>/scripts/jflow.py record <slug> <step> --model <model id> --effort <effort>`, where
`<skill>` is this skill's absolute folder and the model is your own, from the card. The steps are
`spec`, `build`, `check`, `fix`, `live`, `accept` and `done`. The script reads the receipt and git
itself, so nobody counts a number by hand. Record a check again if its receipt changes afterwards.

Commit each step's files, `run.jsonl` included, before the card. Leave pushing and the repo's full build, test and lint
commands to `jflow done`, even when the repo's own instructions ask for them at every step: they
belong to the finished change, not to each receipt.

Every step runs in any CLI, as a plain message in a session the human starts. Where the builder
session cannot be resumed, a new session on the builder's model takes the branch, `spec.md`,
`notes.md` and the open receipt, says so in `notes.md`, and records its steps with `--session fresh`.
