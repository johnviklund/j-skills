# j-skills

Global, cross-repo agent skills — not tied to any single project. Reachable from every repo,
from both Codex CLI and GitHub Copilot CLI (and Claude Code, via the plugin manifest).

## Skills

- **`memory.remember`** — capture durable learnings from the current session as one page per
  lesson in the target repo's `memory/` (indexed by `MEMORY.md`); a repeat bumps the page's
  occurrence count, and three occurrences promote it into a skill. Also updates related
  repo docs and `DESIGN.md` (when the repo has one) in one pass.
- **`memory.compact`** — manual, occasional cleanup of a repo's memory pages: merges pages that
  make the same claim, splits legacy inline `MEMORY.md` entries into pages, flags
  stale/superseded pages and skill-promotion candidates, and writes proposal files for review.
  Never runs automatically.
- **`workflow`** — a personal solo-dev workflow of four phases and a wrap (v2.1: brainstorm →
  plan → execute → review → wrap). The brainstorm is a grill ending in a brief with behaviours and test seams; the plan
  is ≤8 tracer-bullet tickets with literal acceptance lines; execute runs one ticket red → green
  (operator tickets for live steps the human runs); review checks the outcome on the surface users
  reach. Writer and reviewer sit with different vendors (a same-vendor review is allowed but
  flagged as degraded). Seats map to models in `workflow/ROUTING.md`. This is the canonical
  source for that workflow — edit this skill directly when its shape changes.
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
- **`retro`** — `retro [slug | session id]`: a retrospective on one session or `.workflow` run.
  Finds where the agent lost time and proposes environment fixes (navigation pointers,
  guardrails, review rules, steering weight, tool economy, information access, skill friction),
  ranked, each routed to its owner (`memory.remember`, `workflow todo`, `checkup`, or you for
  global files). Adapted from [Matt Pocock's `retro`](https://github.com/mattpocock/skills/tree/main/skills/engineering/retro)
  (MIT, © 2026 Matt Pocock). Depends on his `writing-for-agents` skill, installed separately
  from upstream (see *External dependencies*).

## How this repo is wired up

This repo is `johnviklund/j-skills`. The plugin manifest (`.claude-plugin/plugin.json`) is named
`j-skills`, and Codex prefixes skills with that name (`j-skills:workflow`). The local clone's
folder is still called `agent-skills` (from before the rename) — paths below use that folder name.

`.github/skills/` is the canonical source for the skill content (`checkup`, `evals`,
`memory.compact`, `memory.remember`, `retro`, `workflow`). The clone lives at
`~/Documents/projects/skills/agent-skills`, and every consumer is a symlink straight to it — no
copies, no reinstall, no drift:

| Where | Read by | Link |
|---|---|---|
| `~/.agents/skills/<name>` | Copilot CLI | → `~/Documents/projects/skills/agent-skills/.github/skills/<name>` |
| `~/.codex/skills/<name>` | Codex CLI (it does not read `~/.agents/skills/`) | same target |
| `~/Documents/projects/skills/<name>` | convenience, for browsing | → `agent-skills/.github/skills/<name>` |
| `skills/<name>` in this repo | Claude Code plugin discovery | → `../.github/skills/<name>` |

Edit under `.github/skills/<name>/`, commit, push — both CLIs see the change immediately.
`~/.agents/skills/` is shared with a separate multi-source skill installer (state in
`~/.agents/.skill-lock.json`) that also manages third-party skills, so it is not simply a clone of
this repo.

**Caveat:** that installer could in principle replace one of these symlinks with a plain directory
during an "update all" pass. If a skill stops picking up edits, run `ls -la ~/.agents/skills/<name>`;
if it's a directory again, restore it with
`ln -sfn ~/Documents/projects/skills/agent-skills/.github/skills/<name> ~/.agents/skills/<name>`
(and the same for `~/.codex/skills/<name>`).

### External dependencies

`retro` invokes `writing-for-agents` from
[`mattpocock/skills`](https://github.com/mattpocock/skills/tree/main/skills/productivity/writing-for-agents).
It is not vendored here: the multi-source installer keeps it in `~/.agents/skills/writing-for-agents`
and updates it from upstream, so there is one copy and no name collision. Codex gets it through a
symlink: `ln -s ~/.agents/skills/writing-for-agents ~/.codex/skills/writing-for-agents`. Without
it, `retro` still runs and says the guide is missing.

### Updating a skill

1. Edit under `.github/skills/<name>/` in `~/Documents/projects/skills/agent-skills` (or via
   any symlink path — same files).
2. Commit and push. Both Codex and Copilot are live immediately; no reinstall needed (restart an
   already-open session to reload).
3. Verify: `readlink ~/.agents/skills/<name>` and `readlink ~/.codex/skills/<name>` point at
   `.github/skills/<name>` in the clone.

## Adding a new global skill

1. Add a new folder under `.github/skills/<name>/SKILL.md`.
2. Symlink it from `skills/<name>` at the repo root (`../.github/skills/<name>`) — this is only
   for Claude Code's plugin discovery (`.claude-plugin/plugin.json`), unrelated to the local dev
   setup below.
3. Commit and push.
4. Link it into both CLIs so it is picked up immediately:
   `ln -s ~/Documents/projects/skills/agent-skills/.github/skills/<name> ~/.agents/skills/<name>`
   and the same into `~/.codex/skills/<name>`.

**Known gotcha — Copilot's skill loader can silently drop a skill with a long `description`.**
Confirmed empirically (under an older `copilot plugin install` setup, since replaced by the
symlinks above): a description field somewhere between ~1033 and ~1078 characters caused
Copilot to load successfully (no error) but silently omit that one skill from `copilot skill
list` — the skill name and content weren't the cause (tested independently), only description
length was. Not re-tested against the current `~/.agents/skills/` discovery path, but the safe
margin still applies: keep each skill's `description` under ~900 characters, and after adding or
editing a skill, verify it actually registered —
`copilot skill list --json | grep -A2 '"name": "<your-skill>"'` (current sources report as
`inherited` or `personal-agents`) — don't just trust a success message, since one could print
even when a skill was silently dropped.

## License

MIT — see [`LICENSE`](LICENSE).
