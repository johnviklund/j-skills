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

**Spec, build, check, ship.** A fresh checker proves the change on the real thing against a spec
the builder did not write, then attacks cases outside it. Evidence decides whether work is done.

Everything the human reads follows the Rules of the `plain` skill: invoke it once before the first
message. A question carries one decision, lettered options and a ➡️ recommended option first.

## Steps and seats

| Command | Reference |
|---|---|
| `jflow spec <slug>` | [references/spec.md](references/spec.md) |
| `jflow build <slug>` | [references/build.md](references/build.md) |
| `jflow check <slug>` | [references/check.md](references/check.md) |
| `jflow done <slug>` | [references/done.md](references/done.md) |

Run `python3 <skill>/scripts/jflow.py seat <step>` and copy its assignment into each card.
[flow.json](flow.json) lists steps; [config.json](config.json) holds defaults.
Use only named fallbacks; null means stop.

**Config.** Merge defaults, `.jflow/config.json`, then `--config FILE` or `$JFLOW_CONFIG`,
seat by seat. The flag replaces the env file. Files have `"schema_version": 1` and `"seats"`
keyed by step. Overrides supply `model`, `vendor`, `effort` and `fallback`, null or a complete
seat. Fix, live and accept inherit build.

**Independence.** Top-level `different_vendors` defaults true; matching build/check vendors
select `other_vendor`, a complete seat on another vendor. False disables this default.
A wrong-vendor session says so in its first line and notes, then continues.
Its check card uses `--builder-vendor V`.

**Locked rules.** Seats print fixed `rules`; config may repeat them as true.
`public_paid_needs_human` requires a human for public or paid actions; `checker_read_only`
forbids product edits by checkers. Both declare session policy. `no_secrets` rejects key-like
config values and record's `--model` and `--effort` values without echoing them.

A receipt's own commit moves `HEAD`, so "changed" always means code: `.jflow/` files do not count.

Read the one reference for the command before opening anything in `.jflow/`, because check
starts blind to part of that folder. Its completion criterion ends the step.

## The run: `.jflow/<slug>/`

Tracked in git, separately from `.workflow/`.

```text
.jflow/<slug>/
  spec.md             the spec and Proof table, written by spec and read-only afterwards
  notes.md            the builder's judgement calls and anything left open, a few lines
  drive.py            the checker's one driver when a row needs it, reused by later checks, deleted at done
  receipts/check-N.md one per check, numbered from 1
  run.jsonl           one line per step, written by scripts/jflow.py: the run's numbers
```

Commit only these files. Raw output goes to a temp folder.

`spec.md` is the answer key. Only `jflow spec`, with the human's confirmation, changes it, and
every row then runs again.

**Accepted.** When the human accepts a missed bar, an unproved row or a defect in so many words,
the session they said it to adds one line under `## Accepted` at the end of `spec.md`, in its own
commit named `jflow accept <slug>`, and no row runs again. The bar stays as written, so the record
shows what was missed. An accepted item is no longer open.

```markdown
## Accepted
- Row 3 · 254 of 300 against a bar of 255 · "<the human's words>" · <date> · <sha it applies to>
- Defect 2 · <the miss> · "<the human's words>" · <date> · <sha it applies to>
```

`next` closes an item only when its line starts with `Row N` or `Defect N` and was committed
after the newest receipt. A later receipt that still fails the item saw the acceptance.

## The next step

`python3 <skill>/scripts/jflow.py next <slug>` reads the run folder and git and prints the closing
card for the next step. With `--json` it prints the same decision for a driver: `step`, `n`, `role`,
`model`, `command`, `session`, `blocker` and `why`. Bare `jflow <slug>` prints that card. A stop for
the human has `role: "human"` and a `blocker`; tell the human what it says. Pass `--builder-vendor V`
as for `seat`.

**Checks are capped, because a loop that has not converged needs a person.** A change gets three
checks at most, and a check that only reruns BLOCKED or WAITING rows does not count, since no fix
went in. At the cap, stop and give the human what is open. A `Checks allowed: N` line in
`notes.md` raises the cap to N, when the human allows more.

## The closing card

End each step, after its commit, by running `jflow.py next <slug>` and printing its card as it
stands. When waiting for the human, end on the question. The card has this shape:

````markdown
Model: <model · effort>. Session: <fresh | builder session>.

```text
<exact message to send>
```
````

In Codex, run check with `-c sandbox_workspace_write.network_access=true`: measured 2026-11-04 on
Codex 0.166, a local test client hangs in the default sandbox.

Before the commit, record the step:
`python3 <skill>/scripts/jflow.py record <slug> <step> --model <model id> --effort <effort>`, where
`<skill>` is this skill's absolute folder and the model is your own. Use the step from `flow.json`.
The script reads git and receipts. Record a check again if its receipt changes.

Commit each step's files, `run.jsonl` included, before the card. Leave pushing and the repo's full build, test and lint
commands to `jflow done`, even when the repo's own instructions ask for them at every step: they
belong to the finished change, not to each receipt.

Every step runs in any CLI, as a plain message in a session the human starts. Where the builder
session cannot be resumed, a new session on the builder's model takes the branch, `spec.md`,
`notes.md` and the open receipt, says so in `notes.md`, and records its steps with `--session fresh`.
