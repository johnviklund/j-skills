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
- **`understand`** — `understand <slug>` (after `workflow wrap`) or `understand <area>`: a
  human-friendly explainer as one self-contained HTML page — prose by the `plain` rules,
  hand-drawn inline SVG diagrams, before/after screenshots of every changed screen
  with unrequested UI changes flagged, decisions, open questions and
  risks, and for a run a what-changed summary. Every claim cites `file:line` or a commit, and a checker
  verifies each cite against git. Written to `.workflow/<slug>/understand/explainer.html` or
  `docs/understand/<topic>/explainer.html`. Inspired by [Karpathy on understanding LLM output](https://x.com/karpathy/status/2105819303471976479).
- **`plain`** is the single source of the plain-language rules, in `plain/rules.md`. Every
  skill that writes for a person points there. Typed or triggered on "in simple terms", "plain
  English" or "wait, what?", it explains the topic or the last message for someone who just
  switched into the project. On "remove AI patterns" or "unslop", it rewrites text or a file and
  keeps every fact. Rules adapted from `unslop` and from `understand`'s STE section.
- **`agent-docs`** is the reference for writing documents agents read: skills, `AGENTS.md`,
  `CLAUDE.md` and memory pages. It covers context pointers, the two loads, progressive
  disclosure, leading words and pruning, plus the j-skills conventions in `SKILL-MECHANICS.md`.
  Ported from [Matt Pocock's `writing-for-agents`](https://github.com/mattpocock/skills/tree/main/skills/productivity/writing-for-agents)
  (MIT, © 2026 Matt Pocock).

## How this repo is wired up

This repo is `johnviklund/j-skills`. The plugin manifest (`.claude-plugin/plugin.json`) is named
`j-skills`, and Codex prefixes skills with that name (`j-skills:workflow`). The repo was once
called `agent-skills`. GitHub redirects the old name, but use `j-skills` everywhere.

`.github/skills/` is the canonical source for the skill content. The clone lives at
`~/Work/j-skills`, and every consumer is a symlink straight to it. There are no copies, so there
is nothing to reinstall and nothing to drift:

| Where | Read by | Link |
|---|---|---|
| `~/.agents/skills/<name>` | Copilot CLI | → `~/Work/j-skills/.github/skills/<name>` |
| `~/.codex/skills/<name>` | Codex CLI, which does not read `~/.agents/skills/` | same target |
| `~/.claude/skills/<name>` | Claude Code | same target |
| `skills/<name>` in this repo | Claude Code plugin discovery | → `../.github/skills/<name>` |

Edit under `.github/skills/<name>/`, commit, push. All three CLIs see the change at once.
`~/.agents/skills/` can also hold skills from other sources, so it is not simply a clone of this
repo.

**Caveat:** a skill installer could replace one of these symlinks with a plain directory. If a
skill stops picking up edits, run `ls -la ~/.agents/skills/<name>`. If it is a directory again,
restore it with `ln -sfn ~/Work/j-skills/.github/skills/<name> ~/.agents/skills/<name>`, and the
same for `~/.codex/skills/<name>` and `~/.claude/skills/<name>`.

### External dependencies

`retro` invokes `writing-for-agents` from
[`mattpocock/skills`](https://github.com/mattpocock/skills/tree/main/skills/productivity/writing-for-agents).
It is not vendored here: the multi-source installer keeps it in `~/.agents/skills/writing-for-agents`
and updates it from upstream, so there is one copy and no name collision. Codex gets it through a
symlink: `ln -s ~/.agents/skills/writing-for-agents ~/.codex/skills/writing-for-agents`. Without
it, `retro` still runs and says the guide is missing.

### Updating a skill

1. Edit under `.github/skills/<name>/` in `~/Work/j-skills`. Any symlink path reaches the same
   files.
2. Commit and push. Both Codex and Copilot are live immediately; no reinstall needed (restart an
   already-open session to reload).
3. Verify: `readlink -f ~/.agents/skills/<name>`, `~/.codex/skills/<name>` and
   `~/.claude/skills/<name>` all point at `~/Work/j-skills/.github/skills/<name>`.

## Adding a new global skill

1. Add a new folder under `.github/skills/<name>/SKILL.md`.
2. Symlink it from `skills/<name>` at the repo root (`../.github/skills/<name>`) — this is only
   for Claude Code's plugin discovery (`.claude-plugin/plugin.json`), unrelated to the local dev
   setup below.
3. Commit and push.
4. Link it into all three CLIs so it is picked up at once:
   `ln -s ~/Work/j-skills/.github/skills/<name> ~/.agents/skills/<name>`, and the same into
   `~/.codex/skills/<name>` and `~/.claude/skills/<name>`.

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
