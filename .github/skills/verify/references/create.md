## verify.create

Contents: 0. Locate · 1. Interview · 2. Start · 3. Control CLI · 4. Skill · 5. Feature map · 6. Proof · 7. Wiring · 8. Report

**0. Locate.** If `.agents/skills/verify-*/` already exists, stop: the repo has one, and
`verify.maintain` is the command. A repo with no runnable app yet (an empty bootstrap) also
stops: say what must exist first.

**1. Interview the repo, not the human.** Answer each from the code, docs and config. Ask the
human only what you cannot observe, in one round.

- **Surface:** what a user actually touches: web UI, desktop app, CLI or TUI, HTTP API, mobile.
  Pick the primary one and note the rest in the map's README.
- **Run:** the repo's own documented start command (package scripts, Makefile, README), its
  ports, env vars, seed data and auth, including test users and staging endpoints.
- **Drive:** existing harnesses first: Playwright or Cypress specs, expect scripts, a debug port,
  curl-able endpoints. Only then a default per surface: Playwright for web and Electron (its
  CDP connection for Electron), tmux for CLI and TUI, curl for HTTP. Adding a dev dependency is
  the human's decision: ask.
- **Observe:** what evidence exists: screenshots, ARIA snapshots, terminal transcripts, response
  bodies, logs, exit codes, database state, perf traces.
- **Isolate:** whether two instances can run side by side (ports, data dirs, profiles). When they
  cannot, the generated skill says so and refuses to drive an instance it did not start, because
  driving the human's own session can corrupt it.

Done when every bullet has an answer with a source (`file:line`, a command, or the human).

**2. Make it start.** Run the start command. A checkout that does not build or start is fixed
first, or reported precisely, because a skill written against a broken base teaches wrong
steps. A missing asset that blocks startup but is irrelevant to the app may be created by the
CLI's `up`, marked as verification scaffolding, and removed by `down`.

**3. Build the control CLI.** Drive one feature by hand first to learn the recipe, then script
it. `scripts/control` uses the repo's own language, or Python 3 standard library plus the chosen
driver. It has these subcommands at minimum:

| Subcommand | Does |
|---|---|
| `up` | starts an isolated instance (own port, data dir, seed data), waits until ready, prints its id |
| `doctor` | read-only: process up, expected build or revision, port owned by this run, auth valid. Exit 0 only when the instance is worth driving |
| `down` | stops only what `up` started (never kill by process name) and removes scratch state, never evidence |
| drive commands | the surface's verbs, using stable handles: ARIA role and name, data attributes, routes, prompt strings. For example `open ROUTE`, `click --role R --name N`, `fill`, `run -- CMD` |
| `shot`, `snapshot` | screenshot or text snapshot to `--out DIR` |

It is built for an agent reader: output in JSON, subcommands that reveal detail step by step,
`--help` on every level with an example, `--dry-run` on anything with side effects, and errors
that say what to do instead ("port 4173 busy: run `control down` or pass `--port`"). Evidence
goes to the `--out` directory the caller names, or `.verify-evidence/` when none is named;
add that folder to `.gitignore`. Evidence often lands in a committed run folder, so the CLI masks
secrets before it writes or prints anything: auth headers, cookies, tokens, passwords and keys in
captured requests, logs and env dumps become `***`. Test credentials are read from env vars or an
ignored file, and the skill and feature files name where they live, never their values.

Done when `up`, `doctor`, one drive, `shot` and `down` run clean twice in a row, and their output
holds no credential value.

**4. Write `verify-APP/SKILL.md`.** Frontmatter `name: verify-APP` and a `description` that names
the app and its surface and says to use it to prove a change works in the running app, take
before/after screenshots, or reproduce a reported bug; under 900 characters, no angle
brackets. The body has these sections, each from what steps 1–3 found, no placeholders left:

- **Launch:** the exact `control up` call and what "ready" looks like; teardown with `control down`.
- **Doctor:** run `control doctor` first, and again after any surprising result or failed
  drive. Driving an instance that failed doctor wastes the run.
- **Drive:** point at `features/README.md`, then the feature's file, as the recipe for any
  feature; the CLI's drive commands with one real example from this repo.
- **Evidence:** the proof standards: drive the real user path, never internal setters or
  test-only endpoints; capture the action and the resulting state, not only the final screen;
  check side effects (files written, rows inserted, messages sent) beside what is visible;
  mock only where a production boundary already isolates the external system; a dry-run is
  checked for what it really skips (files, network, git refs), not trusted by its name.
- **Cleanup:** `control down`, run after every failed attempt too, so nothing strands ports or
  processes. Cleanup never deletes evidence.
- **Helpers:** each script, executable, with its invocation shown.

**5. Seed the feature map.** `features/README.md` plus one file for each of the top 3–5
user-facing features, found from routes, commands, menus and docs. The README holds:

- **Baseline preconditions:** how to launch, the data seeded, `control doctor` required first.
- **Driving conventions:** start every recipe from the baseline; stable handles over CSS or
  position; commands are literal; restore seeded data after a mutation.
- **Proof rules:** UI proof is a screenshot plus a text snapshot; CLI proof is command, stdout,
  stderr and exit code; mutation proof is a second, read-only view of the stored value; every
  artifact names its feature id and entry point; an unreachable path is reported with the
  command tried and the missing precondition, never as verified through another path.
- **Features:** one line per feature file, linked.
- `Last maintained: DATE @ SHA` as the last line; `checkup` reads it.

Each feature file has an H1, one paragraph on what the user can do, then exactly these four H2s
in order. Example, for a notes app:

```markdown
# Create a note

A user saves a titled note from the browser or the CLI, and can cancel an unfinished draft.

## Sub-features
- `create-save` persists a title and body.
- `create-cancel` discards an unfinished draft.

## How to get to it (user POV)
- The `New note` button in the toolbar.
- `notes create --title TITLE --body BODY` in a terminal.

## Driving it with control
Preconditions: baseline; no note titled `Release checklist`.
- **Open editor.** `control click --role button --name "New note"` → a form `Note editor` appears.
- **Save.** `control fill --role textbox --name Title --value "Release checklist"`, then
  `control click --role button --name "Save note"` → status `Note saved`.
- **Confirm persistence.** `control click --role link --name "All notes"` → the list shows `Release checklist`.

## Gotchas
- Titles are trimmed on save: assert the rendered title, not the input value.
- A save status alone is not proof: reopen the note from the list.
```

The map is user-facing only: user paths, stable handles, required state, commands and
observable proof. Implementation details go stale fastest, so they stay out. A feature with
several entry points lists all of them, and a proof that drove only one of them says so.

**6. Prove it.** Follow the new `SKILL.md` cold, end to end, on one mapped feature: launch,
doctor, drive, evidence, cleanup. After cleanup, confirm the evidence still exists where the
skill says. Fix what fails and rerun, with `control down` after every failed attempt. A skill
that was never run end to end is a draft. Done when one clean pass has run and its evidence
survived.

**7. Wire it up.**

- Create the `.claude/skills/verify-APP` symlink and check it resolves.
- In `AGENTS.md`'s `## Verifying your work` block (create the block if missing), add one line:
  "Drive the running app with the `verify-APP` skill (`.agents/skills/verify-APP/`); start
  with its `features/README.md`." Replace a `verify.create` TODO line if bootstrap left one.
- Run `copilot skill list --json` in the repo and confirm `verify-APP` appears, when Copilot
  is installed.
- Commit the skill folder, the symlink, `.gitignore` and `AGENTS.md` together.

**8. Report**, in plain words, at most six lines: the surface and driver chosen, the CLI's
subcommands, the features mapped, the feature proven and where its evidence is, anything not
reachable and why, and next: run `verify.maintain` after a stretch of UI changes.

