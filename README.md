# j-skills

Thirteen skills for working with coding agents in Claude Code, Codex CLI and GitHub Copilot CLI.
Use `jflow` to take a code change from spec to pushed, proved code. Use the other skills when you
need a roadmap, an explanation, app checks, saved lessons or help improving how you work.

**Start with one change. You do not need to run every skill each time.**

[Install the skills](#setup) · [Follow a change](#follow-one-change-from-spec-to-done) ·
[Choose a skill](#which-skill-do-i-need) · [Read the details](#skill-reference)

## Start here

After [installation](#setup), open your coding agent in the project you want to work on.
Send this as a chat message:

```text
jflow spec export-csv
I want users to download the current table as a CSV file.
```

`export-csv` is the **run name**, also called a slug. Choose a short name for your own change.
The agent asks what to build, writes a one-page spec, and gives you the next message to send.

Commands in the tables are **messages to your agent**. The shell blocks under setup go in a
terminal. When installed as a plugin, a skill may appear with a prefix such as `j-skills:jflow`.
Use the exact message on the agent's closing card when it includes a prefix.

## Follow one change from spec to done

Send **one message at a time**. Wait for the result before continuing, and keep the same run name.

| Step | Message to send | What you get | Your part |
|---|---|---|---|
| 1. Say what to build | `jflow spec export-csv` | A one-page spec with a Proof table: what a pass looks like | Answer questions and confirm the spec |
| 2. Build it | `jflow build export-csv` | The whole change, with tests, in one session | Answer any question it stops on |
| 3. Prove it | `jflow check export-csv` | A fresh session on another vendor runs each Proof row on the real thing, then attacks what the table never asked | Decide on any row it could not prove |
| 4. Ship it | `jflow done export-csv` | Final checks, updated `TODO.md` and `ROADMAP.md`, saved lessons and a push | Approve any doc edits it proposes |

When a check finds a defect, the card sends you back to the build session to fix it, then to a
new check. Every step ends with a **closing card**: the model to pick, whether to start a fresh
session, and the exact message to send. Send `jflow export-csv` to see it again. Progress lives in
`.jflow/export-csv/`, so a fresh session can resume from the saved files.

To save an idea for later, add a line to `TODO.md`. To decide what to work on next, use
`roadmap`. For a new project, `bootstrap` writes the steering docs. Once the app runs,
`verify.create` gives the agent a repeatable way to drive and check it.

## Which skill do I need?

Choose the row that matches your situation.

| When you need… | Skill | Example message | Result |
|---|---|---|---|
| A code change specified, built and proved | [jflow](#jflow) | `jflow spec export-csv` | A one-page spec with a Proof table, then the change, built and proved on the real thing |
| Steering docs for a repo: the north star, the design and the roadmap | [bootstrap](#bootstrap) | `bootstrap PRD.md` | `PRODUCT.md`, `DESIGN.md`, `ROADMAP.md` and `TODO.md`, each holding one thing |
| A roadmap that says where to start and why each item matters | [roadmap](#roadmap) | `roadmap item admins cannot see the key numbers` | One item with the problem, its evidence and a way to tell it is solved; `roadmap tidy` finds stale and overlapping items |
| A pure UI or UX change to a screen, without a full run | [design](#design) | `design settings-page - goal: group the options` | Rendered mockups to pick from, then the built change with before/after screenshots |
| A simpler explanation right now | [plain](#plain) | `plain Why did this test fail?` | A short answer in chat |
| A visual explanation to keep or share | [understand](#understand) | `understand export-csv` | An HTML page with diagrams, screenshots and source links, and an optional video |
| A repeatable way to check a runnable app | [verify](#verify) | `verify.create` | An app-checking skill and a map of features and how to test them |
| To save a lesson for future sessions | [memory.remember](#memoryremember) | `Remember this: run the API tests with the local test database.` | A memory page linked from `MEMORY.md` |
| To understand why a session was slow | [retro](#retro) | `retro export-csv` | Suggested fixes for the way you work, for you to approve |
| To find problems in the repo or skill setup | [checkup](#checkup) | `checkup` | A read-only health report and suggested actions |
| To tidy repeated or stale memory | [memory.compact](#memorycompact) | `memory.compact` | Proposed memory changes for you to accept |
| To test a new checker model | [evals](#evals) | `evals.run reviewer` | Bug-detection and false-alarm results; asks which model to test |
| To write instructions agents can follow | [agent-docs](#agent-docs) | `Use agent-docs to improve this repo's AGENTS.md.` | Guidance for writing and testing the instructions |

### What happens automatically, and what do I ask for?

| Timing | What to use |
|---|---|
| Once the repo has a runnable app | Ask for `verify.create`. Existing verification skill? Use `verify.maintain` instead. |
| During a jflow run | The agent uses `plain` writing rules and the repo's verification skill when available. |
| At done | `jflow` calls `memory.remember` when you corrected the agent during the run. |
| After a run, when useful | Ask for `understand <run-name>` to explain the result, or `retro <run-name>` to improve the process. |
| Whenever upkeep is needed | Ask for `checkup`. Use `memory.compact` for memory cleanup or `verify.maintain` to recheck the feature map. |
| Before changing the checker | Run `evals.run reviewer`. It needs the private exam repository described in [setup](#setup). |
| When skills or agent instructions change | `retro` and `memory.remember` load `agent-docs` when needed. You can also request it directly. |

For example, finish `export-csv`, then send `understand export-csv --no-video` to get a visual
explanation. If repeated setup failures slowed the run, send `retro export-csv` too.

## Skill reference

Read the sections below when you need a skill's options, output locations or setup requirements.

### jflow

Use it for any code change bigger than a quick fix.

- `jflow spec <slug>` asks about what to build, never how, and writes a one-page spec. Its Proof
  table says what a pass looks like, and every row must be able to fail.
- `jflow build <slug>` runs one session that builds the whole change and keeps every later fix.
- `jflow check <slug>` runs in a fresh session on the other vendor. It runs the table on the real
  thing, gives each row a verdict, then looks for what the table never asked, and reports only
  defects with a failing input.
- `jflow done <slug>` runs the final checks, records the run, updates `TODO.md` and `ROADMAP.md`,
  and pushes.

When a change writes to real data, the spec names a **gate**: the first live step that cannot be
undone. The checker clears the change before that step and checks again after it. When you accept a
missed bar or an unproved row, the session records your words under `## Accepted` in the spec, and
the bar stays as written.

Every step ends by telling you the next message, the model and the session. Send `jflow <slug>` to
see that again. The record is `.jflow/<slug>/`, tracked in git.

Seats come from JSON. Run `python3 .github/skills/jflow/scripts/jflow.py seat build` to see the
resolved assignment. Defaults live in [jflow/config.json](.github/skills/jflow/config.json).
The repo's `.jflow/config.json` overrides complete seats; `--config FILE` or `$JFLOW_CONFIG`
overrides that. See the [jflow skill](.github/skills/jflow/SKILL.md) for the schema and vendor rule.

**Secret scan before every push.** Install the pre-push hook once per repo:
`python3 ~/.agents/skills/jflow/scripts/hooks.py install`. It runs
[gitleaks](https://github.com/gitleaks/gitleaks) on the commits a push sends and blocks the push
on a finding. Install gitleaks once, for example with `brew install gitleaks` or
`mise use -g gitleaks`; the hook blocks a push without it. You can push unscanned with
`git push --no-verify`. The install replaces hooks an older j-skills version left, removes its old
`pre-commit` hook, and refuses to touch another tool's hook or a `core.hooksPath` setting.
Optional: to stop an agent from skipping the hook with `--no-verify`, `checkup` suggests a deny
rule for your Claude settings.

### plain

Use it when you switch into a project and need something explained without the jargon.

- **Explain mode** answers a question or re-explains the last message. It starts with one line
  on where you are, then gives the short answer, then more detail only if needed.
- **Rewrite mode** rewrites text or a file so it has no AI patterns. Every fact stays.
- It holds the writing rules that every other skill uses for text you read: short sentences,
  plain words, no em dashes and no parentheses.

### understand

Use it after a finished run, or when you want to learn one part of a codebase.

- It writes one self-contained HTML page with diagrams, decisions and open questions.
- Every claim links to a line of code or a commit, and a checker confirms each link. It also reads
  pull request reviews, to explain why the code looks the way it does.
- The page goes to `.jflow/<slug>/understand/` for a run, or `docs/understand/<topic>/` for
  an area.

**Screenshots.** A page about a run shows each changed screen before and after, with changes
nobody asked for first, marked in red. A page about an area shows the screens a user meets. If
the app can't run on the machine, it asks you once how to get the pictures:

- you take them, from a list of screens it gives you,
- it shows the real screen with made-up data, and says so on the page, or
- it leaves a box that says what is missing.

**Video.** When the story has moving parts, such as a UI change or a larger feature, it offers a
short narrated video. Add `--video` or `--no-video` to the command to answer in advance.

- The video follows one example through the system, such as one question from the moment it is
  asked to the answer on screen. Shapes move one idea at a time, in the page's own colours, and
  each picture lands on the word that names it.
- Where it helps, it shows short recordings of the real screen, zoomed in on what the voice is
  describing.
- The video plays just below *In short*. To share the page as one file, for example in Teams, ask
  for a standalone copy: `explainer-standalone.html`, with the video inside.

**Video setup, once per machine:**

- Install `ffmpeg` and Node.js 22 or newer, then run
  `python3 ~/.agents/skills/understand/scripts/build-video.py --setup`. It fetches
  [HyperFrames](https://hyperframes.heygen.com), the open-source tool that turns the video's web
  page into an MP4, and Chrome. It turns HyperFrames' telemetry off.
- Install HyperFrames' own skills, which the video step reads for motion and ready-made pieces:

  ```bash
  npx skills add heygen-com/hyperframes -g -a claude-code codex github-copilot -s hyperframes hyperframes-cli hyperframes-registry -y
  ```

- For a voice, set an ElevenLabs key. Without one, the words show as captions instead. Keep the
  key in its own file and load it near the top of `~/.bashrc`, above the line that stops for
  non-interactive shells, because agents run commands in non-interactive shells:

  ```bash
  read -rs KEY && umask 077 && echo "export ELEVENLABS_API_KEY=$KEY" > ~/.config/elevenlabs.env
  unset KEY
  # near the top of ~/.bashrc:
  [[ -f ~/.config/elevenlabs.env ]] && . ~/.config/elevenlabs.env
  ```

  Then restart your agent. `ELEVENLABS_VOICE_ID` picks another voice.

### design

Use it when a change only alters how a screen looks or feels. A full jflow run is more than
that needs.

- Session 1 grounds itself in `DESIGN.md` and screenshots of the current screen. It invents 2–3
  directions as HTML mockups with your real tokens and content, and shows them side by side in
  `compare.html`. You pick one or mix them. The same session builds it and screenshots before
  and after at desktop and phone width. You try it, then it commits.
- `design check <slug>` runs in a fresh session on the other vendor. It sees only the goal, the
  picked mockup and the screenshots, and reports drift, accessibility failures and unfinished
  details.
- Every screen meets a fixed floor: contrast, keyboard focus, reduced motion, a phone layout
  that fits, and real content only.
- When the change turns out to need new data, an API, a schema or logic, it hands over to
  `jflow spec`, bringing the mockups along as evidence.
- The record is `.design/<slug>/design.md` with its mockups and screens.

### bootstrap

Use it once per repo, and again when the direction changes. It writes four steering docs, each
holding one thing:

- `PRODUCT.md`, the north star: the desired state as a few outcomes, in about one page.
- `DESIGN.md`: how it is built and how it looks.
- `ROADMAP.md`: the order of the steps, in the `roadmap` format.
- `TODO.md`: ideas not yet decided.

`bootstrap PRD.md` creates them from a PRD, or splits a repo's existing long docs into them.
`bootstrap update <change>` changes the north star or the design on purpose, after you approve the
exact lines. `jflow` and `roadmap` read these docs so work stays on course.

### roadmap

Use it to decide what to work on and why, before any spec. A roadmap file has a short ordered
**Next up** list of at most five items, then every other open item in fixed groups: Features, Bugs,
Design, Architecture, Tooling and Measurement.

- `roadmap item <idea>` turns an idea into one item. It restates the idea as a problem, looks up
  the evidence, asks why it matters now and which option to take, with "do nothing" always one of
  them. You confirm the item before it is written.
- `roadmap tidy` reads every open item and finds what is stale, overlapping, conflicting, in the
  wrong group or missing its why. It asks you before changing anything, then moves done items to
  the archive.
- `roadmap` shows Next up and the findings of the format check.

Each item names the `PRODUCT.md` outcome it moves on a `Serves:` line. The check flags an item that
names no outcome, and an outcome that no open item moves.

Each item's `Solved when` line tells `jflow spec` what its first Proof row should prove. Run
`python3 .github/skills/roadmap/scripts/roadmap.py check ROADMAP.md` to check a roadmap's format.

### retro

Use it after a session that felt slow.

- It finds where the agent lost time: failed commands, long searches, corrections from you.
- It also checks whether you gave the same correction in more than one session, by reading the saved
  transcripts on your machine. Nothing is written to a file.
- It suggests fixes, ranked by how much time they would save.
- Each fix you approve goes to the skill or file that owns it.
- Run `retro` for the current session, `retro <slug>` for a jflow run, or `retro <session id>`.

### memory.remember

Use it at the end of a session, or whenever you say "remember this".

- Each lesson gets its own page in the repo's `memory/` folder, listed in `MEMORY.md`.
- When a lesson comes up again, its page counts it. At three times, the lesson moves into a skill.
- When a session relies on a page and it still holds, the page's date is refreshed, so it does not
  show as stale. A page that turned out wrong is fixed.
- It skips claims that go stale on their own, such as "tool X is broken" or a step that was
  missing and is now done. A page about a temporary state says how to check that it has ended.
- It also updates related docs, such as `DESIGN.md` when the repo has one.
- It saves where a secret is kept, never the secret itself. If an instruction came from
  something the agent read, such as a web page, an issue or a log, it asks you before saving it.

### memory.compact

Use it now and then, when memory feels bloated.

- It merges pages that say the same thing and flags pages that are stale.
- It writes proposals for you to accept. It never changes the memory pages itself.

### checkup

Use it when something feels off, or before a cleanup.

- It checks skills, memory, docs, the workspace, config and how each model performs.
- It lists the five corrections you repeat most across sessions, so a repeat can become a rule.
- It only reads. Safe fixes are offered one at a time, and you choose.

### evals

Use it before you give jflow's check seat to a new model, or before you keep a change to
`jflow/references/check.md`.

- It shows the model up to ten diffs that hide known serious bugs, and records which bugs it finds.
- Each diff also has a clean twin with no bug. A serious bug reported on a clean twin counts as a
  false alarm, so a model that flags everything does not score well.
- Some cases are real bugs a check missed. Others are planted in diffs that already shipped, so
  the exam can run before any real miss happens.
- The cases live in a separate private repo, `j-skills-evals`, because they copy code from your
  repos. See *Setup*.
- Only jflow's check seat is tested this way. Other seats are judged on real runs in `WORKLOG.md`.

### verify

Use it once per repo that has something a user touches: a web page, an app, a CLI or an API.

- `verify.create` builds a skill inside the repo, named `verify-<app>`. It has a small command
  that starts the app, checks it is healthy, clicks or types through it, and takes screenshots.
- It also writes a feature map: for each feature, how a user gets to it and what proves it works.
- The command prints `***` instead of passwords and tokens, because its output can end up in
  committed run files. A verify skill built before this rule may not, so check older ones.
- `jflow` build and check use it to drive the real app. `jflow done` names driver steps worth
  keeping, and `verify.maintain` adds them to the command.
- `verify.maintain` drives every feature again and fixes the map where the app has moved on.
  `checkup` tells you when it is due.
- The skill lives in `.agents/skills/verify-<app>/` with a link in `.claude/skills/`, so all
  three CLIs find it. It is based on pstack's verification skills.

### agent-docs

You rarely start this one yourself. `retro` and `memory.remember` load it when they write for
agents.

- It explains how to write skills, `AGENTS.md` files and memory pages that agents follow reliably.
- It covers the format limits, scripts, testing, and a checklist to run before you ship a skill.
- Its `scripts/trigger-test.py` runs test prompts on all three CLIs and reports which skill each
  one loaded. A skill keeps its test prompts in `tests/triggers.tsv`.

## Setup

The terminal commands below install the skills for Claude Code, Codex and GitHub Copilot. This
repo also includes Claude Code plugin discovery links.

Each skill is installed once, as a real folder in `~/.agents/skills/<name>`. The `skills`
installer copies it from GitHub and records it in `~/.agents/.skill-lock.json`. Copilot CLI reads
that folder; Codex and Claude Code read the same folder through links in `~/.codex/skills` and
`~/.claude/skills`. These global installs are independent of the working clone, so that clone can live anywhere.

| Path | What it is |
|---|---|
| `~/.agents/skills/<name>` | The installed skill. Copilot CLI and Codex 0.160 or newer read it |
| `~/.codex/skills/<name>` | A link to `~/.agents/skills/<name>`, for Codex |
| `~/.claude/skills/<name>` | A link to `~/.agents/skills/<name>`, for Claude Code |
| `skills/<name>` in this repo | A link for Claude Code plugin discovery, through `.claude-plugin/plugin.json` |

Install every skill:

```sh
npx skills add johnviklund/j-skills -g -a codex github-copilot -s '*' -y
mkdir -p ~/.codex/skills ~/.claude/skills
for n in agent-docs bootstrap checkup design evals jflow memory.compact memory.remember plain retro roadmap understand verify; do
  ln -sfn ~/.agents/skills/$n ~/.codex/skills/$n
  ln -sfn ../../.agents/skills/$n ~/.claude/skills/$n
done
```

Copilot started inside a clone of this repo reads the clone's `.github/skills` instead of the
installed copies. That is how to try an edit before installing it.

The reviewer exam cases live in a private repo, cloned at the fixed path `~/.agents/j-skills-evals`. The
skills find it there because the installed skills are copies, not git checkouts. The cases copy
code from private repos, so they must never go into this public repo:

```sh
gh repo clone johnviklund/j-skills-evals ~/.agents/j-skills-evals
```

### Change a skill

1. Edit the files under `.github/skills/<name>/` in a clone of this repo.
2. Commit and push.
3. Run `npx skills update -g`. It copies the new version into `~/.agents/skills`, and every CLI
   sees it in its next session.

### Add a skill

1. Create `.github/skills/<name>/SKILL.md`.
2. Link it for plugin discovery: `ln -s ../.github/skills/<name> skills/<name>`.
3. Write `tests/triggers.tsv` in the skill folder and run the trigger test:

   ```sh
   python3 .github/skills/agent-docs/scripts/trigger-test.py .github/skills/<name>/tests/triggers.tsv
   ```

4. Commit and push. Install it and link it for Codex and Claude Code, then add its name to the loop above:

   ```sh
   npx skills add johnviklund/j-skills -g -a codex github-copilot -s <name> -y
   ln -s ~/.agents/skills/<name> ~/.codex/skills/<name>
   ln -s ../../.agents/skills/<name> ~/.claude/skills/<name>
   ```

5. Check that Copilot registered it: `copilot skill list --json | grep '"name": "<name>"'`.

### Keep descriptions short

Copilot silently drops a skill whose `description` is over about 1,000 characters. It shows no
error, and the skill is just missing from `copilot skill list`. Keep each description under 900
characters, and check the list after every change.

## License

MIT, see [`LICENSE`](LICENSE). Notices for adapted work are in
[`THIRD-PARTY-NOTICES.md`](THIRD-PARTY-NOTICES.md).
