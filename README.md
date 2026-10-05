# j-skills

Personal agent skills that work in every repo. Claude Code, Codex CLI and GitHub Copilot CLI all
read them from this one clone.

## Skills at a glance

| Skill | What it does | Start it with |
|---|---|---|
| [`plain`](#plain) | Explains something in simple terms, or rewrites text so it reads plainly | "in simple terms", "wait, what?", "remove AI patterns" |
| [`understand`](#understand) | Writes a cited HTML page that explains a finished run or a part of the code | `understand <slug>` or `understand <area>` |
| [`workflow`](#workflow) | Takes a coding task through brainstorm, plan, execute, review and wrap | `workflow <command>` |
| [`retro`](#retro) | Looks back at a session and suggests fixes so the next one goes faster | `retro` |
| [`memory.remember`](#memoryremember) | Saves lessons from the session into the repo's memory pages | "remember this" |
| [`memory.compact`](#memorycompact) | Cleans up memory pages that overlap or have gone stale | `memory.compact` |
| [`checkup`](#checkup) | Gives a health report on the repo and the skill setup | `checkup` |
| [`evals`](#evals) | Tests a model before it takes the reviewer seat | `evals.run reviewer <model>` |
| [`verify`](#verify) | Gives a repo a scripted way to drive its app, plus a map of its features | `verify.create`, `verify.maintain` |
| [`agent-docs`](#agent-docs) | Guides the writing and testing of skills, `AGENTS.md` and other docs agents read | other skills load it |

Codex shows each skill with the plugin name in front, for example `j-skills:workflow`.

## The skills

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
- When a run changed what users see, the page shows before and after screenshots. Changes nobody
  asked for come first, marked in red.
- Every claim links to a line of code or a commit, and a checker confirms each link.
- To explain why code looks the way it does, it also reads the review comments on the pull
  requests that shaped it.
- The page goes to `.workflow/<slug>/understand/` for a run, or `docs/understand/<topic>/` for
  an area.
- When the story moves, such as a UI change or a larger feature, it asks whether you also want a
  short animated video: shapes that move one idea at a time, as in 3Blue1Brown, drawn in the
  page's own colours and diagram style, each picture landing on the word that names it. It
  tells one of two stories: what a run built, or why, what and how of a feature. The video
  plays at the top of the page. Add `--video` or `--no-video` to the command to answer in
  advance.
- To share a page as one file, for example in Teams, ask for a standalone copy: the build
  writes `explainer-standalone.html` with a 720p video inside it, about 4 MB for two minutes.
- The video is narrated with ElevenLabs when `ELEVENLABS_API_KEY` is set. Without a key, the
  narration shows as captions on screen. Set `ELEVENLABS_VOICE_ID` to pick another voice.
- To set the key, keep it in its own file and load it near the top of `~/.bashrc`, above any
  line that stops for non-interactive shells. Agents run commands in non-interactive shells,
  so a key loaded below that line never reaches them:

  ```bash
  read -rs KEY && umask 077 && echo "export ELEVENLABS_API_KEY=$KEY" > ~/.config/elevenlabs.env
  unset KEY
  # near the top of ~/.bashrc:
  [[ -f ~/.config/elevenlabs.env ]] && . ~/.config/elevenlabs.env
  ```

  Then restart your agent so it picks up the key.
- Videos need `ffmpeg` and the cairo and pango libraries. Manim, the animation library, installs
  itself on first use into `~/.cache/j-skills/manim-venv`, after you agree.

### workflow

Use it for any coding task bigger than a quick fix.

| Step | What happens |
|---|---|
| Brainstorm | The agent asks questions until the task is clear, then writes a short brief. It builds quick throwaway sketches when trying beats asking |
| Plan | Up to eight small tickets, each with lines that say when it is done |
| Execute | One ticket at a time, test first. Steps only you can take become operator tickets |
| Review | Checks the result where users see it. A model from another vendor reviews the code |
| Wrap | Updates docs and memory, then closes the run |

Each step ends with a card that names the next command and the model to use. Before a step marks
its file complete, `workflow/scripts/check-run.py` checks the run folder's format, so mistakes
in headers, tickets or review notes are caught by a script.
`workflow/ROUTING.md` sets the models, and `workflow/README.md` has the full guide.

### retro

Use it after a session that felt slow.

- It finds where the agent lost time: failed commands, long searches, corrections from you.
- It suggests fixes, ranked by how much time they would save.
- Each fix you approve goes to the skill or file that owns it.
- Run `retro` for the current session, `retro <slug>` for a workflow run, or `retro <session id>`.

### memory.remember

Use it at the end of a session, or whenever you say "remember this".

- Each lesson gets its own page in the repo's `memory/` folder, listed in `MEMORY.md`.
- When a lesson comes up again, its page counts it. At three times, the lesson moves into a skill.
- It also updates related docs, such as `DESIGN.md` when the repo has one.

### memory.compact

Use it now and then, when memory feels bloated.

- It merges pages that say the same thing and flags pages that are stale.
- It writes proposals for you to accept. It never changes the memory pages itself.

### checkup

Use it when something feels off, or before a cleanup.

- It checks skills, memory, docs, the workspace, config and how each model performs.
- It only reads. Safe fixes are offered one at a time, and you choose.

### evals

Use it before you let a new model review code, or before you keep a change to the review rules.

- It shows the model up to ten diffs that hide known serious bugs, and records which bugs it finds.
- Each diff also has a clean twin with no bug. A serious bug reported on a clean twin counts as a
  false alarm, so a model that flags everything does not score well.
- Some cases are real bugs a review missed. Others are planted in diffs that already shipped, so
  the exam can run before any real miss happens.
- The cases live in a separate private repo, `j-skills-evals`, because they copy code from your
  repos. See *Setup*.
- Only the reviewer seat is tested this way. Other seats are judged on real runs in `WORKLOG.md`.

### verify

Use it once per repo that has something a user touches: a web page, an app, a CLI or an API.

- `verify.create` builds a skill inside the repo, named `verify-<app>`. It has a small command
  that starts the app, checks it is healthy, clicks or types through it, and takes screenshots.
- It also writes a feature map: for each feature, how a user gets to it and what proves it works.
- `workflow` uses it for before and after screenshots and to check the result in review. Wrap
  updates the map for the features a run changed.
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

Each skill is installed once, as a real folder in `~/.agents/skills/<name>`. The `skills`
installer copies it from GitHub and records it in `~/.agents/.skill-lock.json`. Copilot CLI reads
that folder; Codex reads the same folder through a link in `~/.codex/skills`. No CLI reads a
working clone, so a clone can live anywhere and be deleted safely.

| Path | What it is |
|---|---|
| `~/.agents/skills/<name>` | The installed skill. Copilot CLI and Codex 0.160 or newer read it |
| `~/.codex/skills/<name>` | A link to `~/.agents/skills/<name>`, for Codex |
| `skills/<name>` in this repo | A link for Claude Code plugin discovery, through `.claude-plugin/plugin.json` |

Install every skill:

```sh
npx skills add johnviklund/j-skills -g -a codex github-copilot -s '*' -y
for n in agent-docs checkup evals memory.compact memory.remember plain retro understand verify workflow; do
  ln -sfn ~/.agents/skills/$n ~/.codex/skills/$n
done
```

Copilot started inside a clone of this repo reads the clone's `.github/skills` instead of the
installed copies. That is how to try an edit before installing it.

The reviewer exam cases live in a private repo, cloned next to this one. They copy code from
private repos, so they must never go into this public repo:

```sh
gh repo clone johnviklund/j-skills-evals ../j-skills-evals
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

4. Commit and push. Install it and link it for Codex, then add its name to the loop above:

   ```sh
   npx skills add johnviklund/j-skills -g -a codex github-copilot -s <name> -y
   ln -s ~/.agents/skills/<name> ~/.codex/skills/<name>
   ```

5. Check that Copilot registered it: `copilot skill list --json | grep '"name": "<name>"'`.

### Keep descriptions short

Copilot silently drops a skill whose `description` is over about 1,000 characters. It shows no
error, and the skill is just missing from `copilot skill list`. Keep each description under 900
characters, and check the list after every change.

## License

MIT, see [`LICENSE`](LICENSE). Notices for adapted work are in
[`THIRD-PARTY-NOTICES.md`](THIRD-PARTY-NOTICES.md).
