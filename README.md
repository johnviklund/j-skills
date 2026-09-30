# j-skills

Global, cross-repo agent skills — not tied to any single project. Reachable from every repo,
from both Codex CLI and GitHub Copilot CLI.

## Skills

- **`memory.remember`** — capture durable learnings from the current session and write them
  into the target repo's `MEMORY.md`/`AGENTS.md`/`README.md`, an existing or new skill, and
  `DESIGN.md` (when the repo has one), in one pass.
- **`memory.compact`** — manual, occasional cleanup of a repo's `MEMORY.md`: groups entries by
  topic, flags stale/duplicate/superseded entries and skill-promotion candidates, and writes
  proposal files for review. Never runs automatically.
- **`workflow`** — a personal four-phase solo-dev workflow (v2.1: brainstorm → plan → execute →
  review → wrap). The brainstorm is a grill ending in a brief with behaviours and test seams; the plan
  is ≤8 tracer-bullet tickets with literal acceptance lines; execute runs one ticket red → green
  (operator tickets for live steps the human runs); review checks the outcome on the surface users
  reach. Writer and reviewer sit with different vendors. This is the canonical source for that
  workflow — edit this skill directly when its shape changes.
- **`checkup`** — manual, read-first workspace health check (inspired by a `/checkup` command):
  audits skill hygiene (plugin name collisions, folder-vs-frontmatter name, description length,
  Codex symlink parity, self-publish drift), memory hygiene (MEMORY.md size/staleness/superseded,
  leftover proposals), doc freshness (canonical docs, dead skill references), workspace
  cleanliness (leftover `.workflow` scratch, tracked junk, unpushed work), config health, and
  eval-set health. Reports severity-ranked findings and prioritized fixes; delegates compaction
  to `memory.compact` and eval runs to `evals.run`; applies only opt-in, one-at-a-time safe fixes.
- **`evals`** — `evals.run reviewer [candidate model]` is a recall check for strict-reviewer
  candidates on ≤8 diffs with known P0/P1 findings deposited by `workflow`; `evals.list` shows the
  set's status. Every other seat is judged on trial runs recorded in `WORKLOG.md`, not exams.

## How this repo is wired up

**Both Codex CLI and Copilot CLI (and other agent CLIs) read the same shared directory:
`~/.agents/skills/`.** It's managed by a separate, multi-source skill installer that also pulls
third-party skills (e.g. `last30days` from someone else's repo) — its state lives in
`~/.agents/.skill-lock.json`. Because that directory is shared infrastructure for *any* skill
source, it is not simply `git clone`-able as this repo.

`.github/skills/` is still the canonical source for this repo's own skill content (`checkup`,
`evals`, `memory.compact`, `memory.remember`, `workflow`). **The clone lives at
`~/Documents/Projects/skills/agent-skills`** — inside a dedicated `~/Documents/Projects/skills/`
folder that also holds one flat convenience symlink per owned skill
(`~/Documents/Projects/skills/<name>` → `agent-skills/.github/skills/<name>`), so the skill
content is browsable at a short path without duplicating it.

`~/.agents/skills/<name>` is then itself a symlink to `~/Documents/Projects/skills/<name>` — one
per owned skill. This means both Codex and Copilot resolve straight through to the git clone with
**no separate per-tool install step, no reinstall, and no drift between copies**: edit under
`.github/skills/<name>/`, commit, push — done. (An older setup used per-tool Codex symlinks plus
a separately-installed Copilot plugin snapshot requiring reinstall after every change; that's
gone now in favor of the single shared directory both tools already read.)

**Caveat:** the multi-source skill installer that owns `~/.agents/skills/` could in principle
overwrite one of these symlinks with a fresh directory copy during some future "update" pass
across all installed skills. If a skill stops picking up edits, check
`ls -la ~/.agents/skills/<name>` — if it's a plain directory again instead of a symlink, re-run:
`ln -sf ~/Documents/Projects/skills/<name> ~/.agents/skills/<name>`.

### Updating a skill

1. Edit under `.github/skills/<name>/` in `~/Documents/Projects/skills/agent-skills` (or via
   either symlink path — same files).
2. Commit and push. Both Codex and Copilot are live immediately; no reinstall needed.
3. Verify: `readlink ~/.agents/skills/<name>` resolves through
   `~/Documents/Projects/skills/<name>` to `.github/skills/<name>`.

## Adding a new global skill

1. Add a new folder under `.github/skills/<name>/SKILL.md`.
2. Symlink it from `skills/<name>` at the repo root (`../.github/skills/<name>`) — this is only
   for Claude Code's plugin discovery (`.claude-plugin/plugin.json`), unrelated to the local dev
   setup below.
3. Commit and push.
4. Add the two local convenience symlinks so Codex/Copilot pick it up immediately:
   `ln -s agent-skills/.github/skills/<name> ~/Documents/Projects/skills/<name>` then
   `ln -s ~/Documents/Projects/skills/<name> ~/.agents/skills/<name>`.

**Known gotcha — Copilot's skill loader can silently drop a skill with a long `description`.**
Confirmed empirically (under the old `copilot plugin install` mechanism, since replaced by the
symlink setup above): a description field somewhere between ~1033 and ~1078 characters caused
Copilot to load successfully (no error) but silently omit that one skill from `copilot skill
list` — the skill name and content weren't the cause (tested independently), only description
length was. Not re-tested against the current `~/.agents/skills/` discovery path, but the safe
margin still applies: keep each skill's `description` under ~900 characters, and after adding or
editing a skill, verify it actually registered —
`copilot skill list --json | grep -A2 '"name": "<your-skill>"'` (current sources report as
`inherited` or `personal-agents`) — don't just trust a success message, since one could print
even when a skill was silently dropped.
