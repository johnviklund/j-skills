---
name: checkup
description: >
  Read-only health report for the current repo and the user's skill wiring. Use when asked to
  check, audit, clean up, or tune the workspace -- phrases like
  "checkup", "workspace health", "are my skills in check", "is memory compacted",
  "AGENTS/PRODUCT/DESIGN stale", "skill collisions", or "Codex parity". Checks skill hygiene,
  memory hygiene, doc freshness, workspace cleanliness, config health, and seat/skill performance,
  plus the reviewer exam set.
  Reports severity-ranked findings and prioritized fixes; delegates to memory.compact and
  evals.run reviewer; applies only opt-in safe fixes.
---

# checkup

A manual, read-first workspace health check. It answers "is my workspace in good shape?" in one
pass: are my skills wired correctly and not colliding, is memory compacted, are the canonical docs
drifting, is there leftover scratch or junk, is my config sane, is each model still earning its seat.
Inspired by a `/checkup` command.

**It reports and recommends; it does not bulldoze.** Everything is read-only by default. The only
things it may change are a short allow-list of *trivially safe* fixes, offered **one at a time**
with explicit approval. Anything risky is proposed or delegated, never auto-applied.

## Invocation

Runs on `checkup` / `/checkup` (a bare `checkup` on its own line is enough). Try `/checkup` first;
if the leading slash is swallowed by the CLI, use the bare `checkup` form. Do not trigger on casual
mentions of "check" elsewhere in a message -- only the explicit prefixed form.

Optional scope words narrow the pass: `checkup skills`, `checkup memory`, `checkup docs`,
`checkup workspace`, `checkup config`, `checkup seats`. With no scope word, run all sections.

## Ground rules

- **Read-only by default.** Gather evidence, then report. Never edit `DESIGN.md`, `PRODUCT.md`, or
  any canonical doc as part of a checkup -- surface drift and let the human decide (this mirrors the
  repo rule that those docs are not edited without an explicit ask).
- **Delegate, don't reimplement.** When memory needs compaction, recommend `memory.compact`; when
  learnings need routing, recommend `memory.remember`; when a reviewer candidate needs its recall
  check, recommend `evals.run reviewer`. Do not re-do their work inside a checkup.
- **Opt-in safe fixes only, one at a time.** See *Safe-fix allow-list*. Ask before each; if the
  user declined the fix appetite, stay pure-report.
- **Honest heuristics.** Staleness of prose docs can't be proven mechanically. Say "worth a human
  skim" with the evidence (last-touched vs. related activity), never "this is wrong".
- **Manual, stateless.** No cadence, no auto-trigger, no state file. The user runs it when they want.
- **Portable.** Assume POSIX shell on macOS/Linux, run from the repo root (cwd). Skip a check
  gracefully (mark it `n/a`) when its inputs don't exist rather than erroring.
- **Writing.** Invoke `plain` once before writing the report; the report follows its Rules.
- **Report.** Before writing, read [references/report.md](references/report.md) for the report,
  questions and action cards. Done when the report follows that format.

## The check battery

Run the sections in order. For each finding pick a severity: **✅ OK**, **⚠️ warn** (worth a look,
not blocking), **🔴 action** (should be fixed). Collect evidence with commands like the following;
adapt paths to what actually exists.

Read each selected section before running its checks:

- `skills`: [Skill hygiene](references/skills.md).
- `memory`: [Memory hygiene](references/memory.md).
- `docs`: [Doc freshness & consistency](references/docs.md).
- `workspace`: [Workspace cleanliness](references/workspace.md).
- `config`: [Config health](references/config.md).
- `seats`: [Seat & skill performance, reviewer exam set](references/seats.md).

## Safe-fix allow-list (opt-in, one at a time)

Only these may be applied during a checkup, and only after the user approves each:

- Create a missing or repair a broken `~/.codex/skills/<name>` symlink for a repo-local skill.
- Remove a tracked `.DS_Store` (and add it to `.gitignore` if missing).
- Add obviously-missing `.gitignore` entries (`.DS_Store`, `.env`, venvs, build output).
- Delete a leftover `.proposed.md` **only** after confirming its content was already accepted/routed.

Everything else is **propose-only or delegate**: renaming a colliding skill, editing any canonical
doc, compacting memory (`memory.compact`), routing learnings (`memory.remember`), deleting
`.workflow` scratch (route first), editing `ROUTING.md`, pruning the reviewer exam set, running the
reviewer exam (`evals.run reviewer`), or removing anything that could carry unsaved value.

## Relationship to the other skills

- `memory.compact` — owns the actual MEMORY.md compaction proposal; checkup only *detects the need*.
- `memory.remember` — owns routing learnings; checkup only flags un-routed leftovers.
- `workflow` — owns the dev loop, writes the `Run:`/`Seats:` evidence at wrap, and owns
  `ROUTING.md`; checkup reads the evidence, flags leftover `.workflow` scratch and unpushed work,
  and recommends routing edits it never applies.
- `evals.run reviewer` — owns the one exam (reviewer recall and false alarms on ≤10 cases); checkup only audits
  that set and flags an unchecked reviewer.
- `retro` — owns the per-session look at friction (what one run or session cost); checkup owns the
  standing state of the workspace. A retro hands hygiene it notices to `checkup`.
- `verify` — builds (`verify.create`) and maintains (`verify.maintain`) the repo's verify skill and
  feature map; checkup only flags a missing skill, a broken symlink or a stale `Last maintained` stamp.
- `understand` — writes human-facing explainers (`.workflow/<slug>/understand/`,
  `docs/understand/<topic>/`); checkup treats them as tracked docs, not `.workflow` scratch.

Keep this skill's `description` under ~900 characters (it enforces that rule on others -- it must
pass its own check).
