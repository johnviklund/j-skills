---
name: verify
description: >
  The verify.create and verify.maintain commands; load this skill to run either. Builds and
  maintains a repo's own verification skill: a project-local verify-APP skill with a small
  control CLI that launches, health-checks, drives and screenshots the real app, plus a feature
  map saying how a user reaches each feature and what proves it works. "verify.create"
  generates it and proves it on one feature; "verify.maintain" re-checks every mapped feature
  from source and live, then commits only proven corrections. Run only on an explicit
  "verify.create" or "verify.maintain" message; never on casual mentions of verifying, testing
  or checking a change.
---

# verify

Agents can only close the loop on their own work when they can drive the real app the way a
user does. This skill gives a repo that ability once, as a **lever** (a tool every later agent
runs instead of improvising): a project-local skill named `verify-APP` with a control CLI and a
**feature map**. `workflow` execute and review use it when it exists; `checkup` flags it when it
goes stale.

Two commands:

| Command | Does |
|---|---|
| `verify.create` | Interviews the repo, builds the control CLI, writes `verify-APP`, seeds the feature map, proves it on one feature, wires it up |
| `verify.maintain` | Re-checks every mapped feature from source and live, fixes drift in the skill's own folder, commits the proven corrections |

Every message to the human follows the Rules of the `plain` skill: invoke it once before the
first report. Questions use one decision each, options lettered, a ➡️ recommended default.

## Where the generated skill lives

Measured 2026-10-03 (Claude Code, Codex CLI 0.160.0, Copilot CLI 1.0.91): Claude Code reads
repo skills only from `.claude/skills/`, Codex only from `.agents/skills/`, and Copilot from
`.github/skills/`, `.agents/skills/` and `.claude/skills/`, listing a symlinked skill once. So:

- The real folder is `.agents/skills/verify-APP/`, where `APP` is the repo's short name in
  kebab-case.
- `.claude/skills/verify-APP` is a relative symlink to it:
  `ln -s ../../.agents/skills/verify-APP .claude/skills/verify-APP`.

```text
.agents/skills/verify-APP/
  SKILL.md              launch · doctor · drive · evidence · cleanup · helpers
  scripts/control       the control CLI (executable)
  features/README.md    the map: baseline, conventions, proof rules, feature index, Last maintained
  features/<feature>.md one file per user-facing feature
```

The generated skill is for anyone who works in the repo, with or without j-skills, so it names
no j-skill and needs nothing outside the repo.

## verify.create

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
add that folder to `.gitignore`.

Done when `up`, `doctor`, one drive, `shot` and `down` run clean twice in a row.

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

## verify.maintain

A feature map goes stale as soon as the app changes. This pass keeps it honest. Its unit is the
**feature**: every feature file gets a source check and a live drive.

**Outcome:** exactly one, stated at the end. **clean**: every feature covered, nothing to fix, no
commit except the stamp. **changed**: one commit of proven corrections. **blocked**: coverage
could not finish, or a fix could not be proven; say exactly what blocked it.

**Edit scope:** only the `verify-APP` folder (its `SKILL.md`, `features/`, `scripts/`). Product
code is never edited here. A behaviour the map describes that the app no longer has is either
drift (fix the map) or a product bug (report it): which one is decided in step 5.

**0. Locate.** Find `.agents/skills/verify-*/`. Several → ask which. None → stop and point at
`verify.create`.

**1. Index hygiene.** Read `features/README.md` and list its sibling files. Fix missing, extra,
duplicate and dead index lines.

**2. Source wave.** One read-only sub-agent per feature file, run in parallel. Each reads the
code behind the feature and returns: a short summary, the source entry points with `file:line`,
likely drift with citations (or none), and one recipe to verify it live. Sub-agents never drive
the app and never edit. Done when every feature file has a returned summary.

**3. Reconcile.** Merge overlapping recipes into as few app states as practical. Spot-check
cited drift; leave clean claims alone. Then look for features missing from the map:
`git log --oneline SHA..HEAD` from the `Last maintained` stamp, filtered to user-facing paths. A
feature counts as missing only with a concrete source path.

**4. Live pass.** Required even when the source looks clean, because only a live drive proves
the recipe still works. This session does all the driving, using the skill's own launch model.
Drive every feature at least once, and hold three rules throughout:

1. Run `doctor` before the first drive, and again after any failed or surprising drive. When
   doctor cannot see the problem (a stuck UI on a healthy process), reset to the baseline or
   relaunch.
2. Evidence captured so far survives every cleanup: check it where the skill says it is.
3. Nothing a drive started outlives the drive: clean up after failed attempts too.

A doctor failure caused by drift in the skill is drift: fix it, restart what the fix touched,
and retry once before calling the pass blocked. A feature is `unreachable` only with the
concrete missing precondition (auth, entitlement, OS, external state) and the route tried; a
precondition the map does not mention is drift too. Every harness fix is driven live again
before it ships. Tear down after the last drive.

**5. Triage** each problem into one class:

- **Doc drift:** the map's user-side description is wrong or missing. Fix the feature file.
- **Harness gap:** the app works but the CLI cannot drive it. Fix `scripts/control`, and show
  the new command in `SKILL.md`.
- **Product gap:** the app is actually broken. Keep it out of this commit; report it to the
  human as a lettered decision with ➡️ "add a line to `TODO.md`".

**6. Ship or stop.** Re-read every changed file, update the stamp to
`Last maintained: TODAY @ HEAD-SHA`, and commit as `verify.maintain: <what changed>`. A clean pass
commits the stamp alone. A blocked pass commits nothing and says what blocked it.

**7. Report**, in plain words, at most six lines: the outcome, features covered (count), drift
fixed, harness fixes, unreachable features with their precondition, and product gaps as the
decision list.
