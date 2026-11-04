---
name: jflow
description: >
  Short path for shipping a code change: one session writes a spec with a Proof table of what a
  pass looks like, one session builds it, a fresh session proves it on the real app, and a
  read-only review runs only for risky changes. Commands: spec, build, prove, review, done; bare
  "jflow SLUG" says what is next. Run only on an explicit "jflow COMMAND SLUG" or "/jflow COMMAND
  SLUG" message; never on casual mentions of specs, builds, proof or review.
---

# jflow

**Spec, build, prove, ship.** A fresh agent proves the change on the real thing against an answer
key the builder did not write. That proof, not a discussion of the diff, decides whether the work
is done. The human decides what to build, the builder decides how, and the prover decides whether
it works.

Everything the human reads follows the Rules of the `plain` skill: invoke it once before the first
message. A question carries one decision, lettered options and a ➡️ recommended option first.

## Steps and seats

| Command | Model · effort | Session | Reference |
|---|---|---|---|
| `jflow spec <slug>` | Opus 5.5 · high | fresh, with the human | [references/spec.md](references/spec.md) |
| `jflow build <slug>` | Opus 5.5 · high | fresh; the **builder session**, kept for every fix | [references/build.md](references/build.md) |
| `jflow prove <slug>` | GPT-6.1 Terra · medium | fresh for each proof | [references/prove.md](references/prove.md) |
| `jflow review <slug>` | GPT-6.1 Sol · high | fresh for each review, read-only | [references/review.md](references/review.md) |
| `jflow done <slug>` | same model, builder session | the builder session | [references/done.md](references/done.md) |

Picker IDs: `claude-opus-5.5`, `claude-sonnet-5.5`, `gpt-6.1-terra`, `gpt-6.1-sol`. To change a
seat, edit this table.

**Independence.** Prove and review run on a different vendor from the builder, because two
sessions of one vendor share blind spots. With an OpenAI builder, prove moves to Sonnet 5.5 · medium
and review to Opus 5.5 · high. A session on the wrong vendor says so in its first line and in its
receipt, then carries on.

Read the one reference for the command. Its completion criterion ends the step.

## The run: `.jflow/<slug>/`

Tracked in git. A separate root from `.workflow/`, so no other skill's state or hook reads it.

```text
.jflow/<slug>/
  spec.md             the spec and Proof table, written by spec and read-only afterwards
  notes.md            the builder's judgement calls, a few lines
  receipts/prove-N.md one per proof, numbered from 1, plus any evidence beside it
  receipts/review-N.md one per review
```

`spec.md` is the answer key. Only `jflow spec`, with the human's confirmation, changes it, and
every row then runs again.

## What is next

Bare `jflow <slug>` reads the run folder and prints the card for the first row that holds.

| State | Next |
|---|---|
| no `spec.md`, or `Status: drafting` | `jflow spec` |
| `Status: ready`, no commit since `Base` | `jflow build` |
| code committed, no prove receipt for `HEAD` | `jflow prove` |
| newest prove receipt has BROKEN | back to the builder session with that receipt |
| newest prove receipt has BLOCKED or UNREACHABLE | the human decides, per `references/prove.md` |
| all rows PROVED, `Review: required`, no review receipt for `HEAD` | `jflow review` |
| newest review receipt has defects | back to the builder session with that receipt |
| otherwise | `jflow done` |
| `Status: done` | nothing; say so |

**Rounds are capped, because a loop that has not converged needs a person.** After a BROKEN, a row
gets two re-proves. Review gets two rounds, never a third; a fix from review gets a re-prove that
does not count against that cap. At a cap, stop and give the human what is open.

## The closing card

Every step ends with this as the turn's last output. A turn waiting for the human's answer ends on
the question.

```text
Next: <exact message to send>
Model: <model · effort>
Session: <fresh | builder session>
```

The session running `jflow prove` or `jflow review` gives the builder the receipt path in the
message: `Fix .jflow/<slug>/receipts/prove-2.md, then print the card.`

Commit each step's files before the card. Every step runs in any CLI, as a plain message in a
session the human starts. Where the builder session cannot be resumed, a new session on the
builder's model takes the branch, `spec.md`, `notes.md` and the open receipt, and says so in `notes.md`.
