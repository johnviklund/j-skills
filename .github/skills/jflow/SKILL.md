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
the builder did not write, then attacks cases outside it.

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
select `other_vendor`, a complete seat on another vendor. False disables it.
A wrong-vendor session says so in its first line and notes, then continues.
Its check card uses `--builder-vendor V`.

**Locked rules.** Seats print fixed `rules`; config may repeat them as true.
`public_paid_needs_human` gates public/paid actions on the human; `checker_read_only`
forbids product edits by checkers; `no_secrets` rejects key-like
config and arguments without echoing them.

A receipt's own commit moves `HEAD`, so "changed" always means code: `.jflow/` files do not count.

Read the one reference for the command before opening anything in `.jflow/`, because check
starts blind to part of that folder. Its completion criterion ends the step.

## The run: `.jflow/<slug>/`

Tracked in git, except in [issue and pull request mode](references/github.md): each step's last section.

```text
.jflow/<slug>/
  spec.md             spec and Proof table (read-only after spec)
  notes.md            builder judgement calls and open notes
  drive.py            checker driver, reused across checks, deleted at done
  receipts/check-N.md one per check, from 1
  run.jsonl           step records written by scripts/jflow.py
```

Commit only these files; raw output goes to a temp folder.

`spec.md` is the answer key. Only `jflow spec`, with the human's confirmation, changes it, and
every row then runs again.

**Accepted.** When the human accepts a missed bar, unproved row or defect explicitly,
the builder adds a line under `## Accepted` at the end of `spec.md` in its own
commit `jflow accept <slug>`; no row reruns and the bar stays as written. Accepted defects stay
there; `jflow.py escaped <slug> "<line>" [--ref R]` appends a bug found after done to
`run.jsonl`; commit it.

```markdown
## Accepted
- Row 3 · 254 of 300 against a bar of 255 · "<the human's words>" · <date> · <sha it applies to>
- Defect 2 · <the miss> · "<the human's words>" · <date> · <sha it applies to>
```

`next` closes an item whose line names the sha of the newest or source check for a carried verdict,
committed in or after that check's receipt; a defect carried unchanged across two checks stops for
the human.

## The next step

`python3 <skill>/scripts/jflow.py next <slug>` reads the run folder and git and prints the closing
card (or bare `jflow <slug>`). `--json` prints `step`, `n`, `role`, `model`, `command`, `session`,
`blocker` and `why`. A human stop has `role: "human"` and a `blocker` (question, lettered options,
recommended first). Pass `--builder-vendor V` as for `seat`.

**Checks are capped, because a loop that has not converged needs a person.** A change gets three
checks; one that only reruns BLOCKED or WAITING rows does not count. At the cap, stop and give the
human what is open. A `Checks allowed: N` line in `notes.md` raises the cap; the last such line counts.

**Wait points.** `next` also stops for the human at four points, each cleared by a line in
`notes.md`: `Yes: approach` for an **Ask first** approach, `Yes: gate` before the `Gate:`,
`Yes: done` before done when there are Human checks or Maybes, and `Yes: edits` for the
`## Proposed edits` an unattended done left. `--json` names it in `wait_point`, which other stops
omit. The session the human answered commits `Yes: <point> · "<the human's words>" · <date>`. A
line that starts with `Yes: <point>` clears only that point. A mid-run `jflow spec` resets the
check cap and voids earlier `## Proposed edits` and `Yes:` lines.

**Decisions happen in the builder session, never elsewhere.** Another session's card for a stop
sends the human there with `jflow <slug>`. The builder session prints `next <slug> --ask`: the
question, ending "Reply A or B." On the reply it writes the line the option stands for (a `Yes:`
line, `Checks allowed: <used + 1>` or `## Accepted` lines), commits, does what the option says,
then prints the next card. The human never edits run files.

## The closing card

End each step, after its commit, by running `jflow.py next <slug>` (`--ask` in the builder
session) and printing its output as it stands, last in the message. It is the only next action:
add no options, questions or prompts of your own. A question asked mid-step ends the message
instead. A step ends at its card: never run the step it names, `done` included. Text to paste sits
alone in its own code block.

In Codex, run check with `-c sandbox_workspace_write.network_access=true`: on Codex 0.166 a local
test client hangs in the default sandbox.

`record` validates spec, check and accept steps; fix problems first.
Before the commit, record the step:
`python3 <skill>/scripts/jflow.py record <slug> <step> --model <model id> --effort <effort>`, where
`<skill>` is this skill's folder and the model is yours, never `unknown` (`jflow.py seat <step>`
prints it). Use the step from `flow.json`.
Record a check again if its receipt changes.

Commit each step's files, `run.jsonl` included, before the card. Leave pushing to `jflow done`.

Every step runs in any CLI, as a plain message in a session the human starts. Where the builder
session cannot be resumed, a new session on the builder's model takes over the branch and run
folder, says so in `notes.md`, and records its steps with `--session fresh`.
