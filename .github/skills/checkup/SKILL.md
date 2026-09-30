---
name: checkup
description: >
  Read-only health report for the current repo and the user's skill wiring. Use when asked to
  check, audit, clean up, or tune the workspace -- phrases like
  "checkup", "workspace health", "are my skills in check", "is memory compacted",
  "AGENTS/PRODUCT/DESIGN stale", "skill collisions", or "Codex parity". Checks skill hygiene
  (name collisions, folder-vs-frontmatter name, description length, Codex symlink parity, drift),
  memory hygiene (MEMORY.md index vs memory/ pages, staleness, proposals), doc freshness,
  workspace cleanliness (stalled or parked .workflow runs, tracked junk, unpushed work), config
  health, and seat/skill performance (trial-run numbers from WORKLOG.md per model per seat and
  per skill change, plus the reviewer exam set).
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

## The check battery

Run the sections in order. For each finding pick a severity: **✅ OK**, **⚠️ warn** (worth a look,
not blocking), **🔴 action** (should be fixed). Collect evidence with commands like the following;
adapt paths to what actually exists.

### 1. Skill hygiene

Discover the three skill locations first:

```sh
ls .github/skills/ 2>/dev/null                                   # repo-local skills (this repo)
ls ~/.copilot/installed-plugins/*/*/skills/ \
   ~/.copilot/installed-plugins/_direct/*/skills/ 2>/dev/null    # Copilot plugin/global skills
ls ~/.codex/skills/ 2>/dev/null                                  # Codex skills (symlinks + real dirs)
```

Then check:

- **Name collision with an installed plugin/global skill.** For every repo-local `.github/skills/<name>`,
  is there also a *different* skill named `<name>` installed elsewhere -- a Copilot plugin/global skill,
  or a `~/.codex/skills/<name>` entry? **Ignore a `~/.codex/skills/<name>` that is a symlink pointing
  back to this same repo skill** -- that is intended cross-CLI parity wiring, not a collision (a naive
  name-match false-positives on every skill you've wired into Codex). For genuine matches, **diff the
  `SKILL.md`:** identical content = benign self-publish (note it); **different content = 🔴 harmful
  shadow** (a repo skill hiding a different, often richer, plugin skill). Fix by renaming the repo-local
  one to a repo-specific prefix (e.g. `cx-<name>`) and updating references -- never silently keep the shadow.
- **Folder name ≠ frontmatter `name`.** For each `.github/skills/<dir>/SKILL.md`, confirm `name:`
  matches `<dir>`. A mismatch breaks discovery.
- **Description length.** Flag any skill whose frontmatter `description` exceeds ~900 characters. This
  limit is **confirmed for the Copilot *plugin-install* path** -- the loader silently drops an
  over-length skill (installs with no error, omits it). So it is **🔴 for any skill published/installed
  as a plugin** (it looks installed but isn't; verify `copilot skill list --json | grep '"name": "<skill>"'`).
  For a **repo-local-only** skill loaded directly from `.github/skills/`, discovery tolerates longer
  descriptions -- treat over-length as **⚠️ portability debt** (trim before it is ever published), not a
  hard failure. When unsure, check whether a matching installed plugin or a `copilot-plugins/` packaging
  dir exists.
- **Codex parity.** Codex only loads from `~/.codex/skills/` -- it does not scan a repo's
  `.github/skills/`. For each repo-local skill meant to be available in Codex, confirm a
  `~/.codex/skills/<name>` entry exists and resolves. Missing ones are ⚠️ (Copilot-only until linked).
- **Broken Codex symlinks.** Dangling links whose target no longer exists:
  `find ~/.codex/skills -maxdepth 1 -type l ! -exec test -e {} \; -print`. Each is 🔴.
- **Self-publish drift.** For a skill packaged as its own plugin (e.g. a `.github/copilot-plugins/<name>/`
  whose `skills/<name>` symlinks back to `.github/skills/<name>`), confirm it is still a symlink (single
  source) and that the installed snapshot matches the repo source. A materialized copy or a stale
  installed snapshot is ⚠️ drift.

### 2. Memory hygiene

```sh
wc -lc MEMORY.md 2>/dev/null; ls memory/*.md 2>/dev/null | wc -l
grep -L '^Occurrences:' memory/*.md 2>/dev/null                      # pages missing the standard footer
ls -d MEMORY.proposed.md memory.proposed MEMORY_ARCHIVE.proposed.md skill-promotion-candidates.proposed.md 2>/dev/null
```

- **Index ↔ pages.** Every `memory/<slug>.md` has a line in `MEMORY.md` and every index line
  resolves to a page; an orphan either way is ⚠️. Inline entries still in `MEMORY.md` (v1 shape)
  are ⚠️ "not yet split into pages -- `memory.compact`".
- **Page shape.** A page missing `Applies when` / `Root cause` / `Fix` / `Occurrences` is ⚠️ --
  it can't be matched on repeat.
- **Promotion signal.** A page with `Occurrences: 3` or more and no `Promoted to:` line is ⚠️ --
  skill candidate (`memory.remember`), human decides.
- **Size pressure.** > ~40 pages or `MEMORY.md` > ~40 KB: recommend `memory.compact` (do not
  compact here).
- **Stale pages.** `Last confirmed:` > 90 days before today.
- **Superseded still active.** A page with `Status: superseded` still indexed as active belongs
  in `MEMORY_ARCHIVE.md` / out of the index.
- **Leftover proposals.** A lingering `MEMORY.proposed.md` / `memory.proposed/` (or archive/skill-promotion proposal)
  means a compaction was generated but never accepted or discarded -- ⚠️, recommend review/`mv` or delete.

### 3. Doc freshness & consistency

- **Canonical docs present.** Note which of `AGENTS.md`, `README.md`, `PRODUCT.md`, `DESIGN.md`,
  `PRD.md`, `MEMORY.md`, `MEMORY_ARCHIVE.md` exist; a repo that has some but is missing an expected
  one is worth a note, not an error.
- **Dead skill references.** Skill names referenced in `AGENTS.md`/README that no longer resolve to a
  real skill (e.g. renamed but the reference wasn't updated). **Scope this to actual skill references** --
  backticked names in the skills-list sentence, or tokens matched against the real skill inventory --
  **not every prefix-shaped token.** Doc *paths* and identifiers often share a skill's prefix (e.g. a
  `cx-agentic-intelligence-poc/` docs folder vs. `cx-*` skills) and will false-positive a naive `grep`.
  🔴 only when a name genuinely referenced *as a skill* exists nowhere (repo-local, plugin, or Codex).
- **Prose-doc staleness (heuristic).** Compare each canonical doc's last commit date against recent
  activity in the area it governs (e.g. `DESIGN.md` vs. churn under `web-ui/`):
  `git log -1 --format=%cs -- DESIGN.md` and `git log --since=... --oneline -- web-ui | wc -l`.
  If a doc is untouched while its area changed a lot, say "worth a human skim" -- never assert it's wrong.
- **Broken internal links.** Doc references to repo paths that don't exist are ⚠️.

### 4. Workspace cleanliness

```sh
for d in .workflow/*/; do printf '%s ' "$d"; grep -m1 '^Status:' "$d/brainstorm.md" 2>/dev/null; done   # runs + status
ls .workflow/*.md 2>/dev/null                                             # v1 flat scratch (needs migration)
git check-ignore -q .workflow && echo 'IGNORED'                           # runs must be tracked
git status --porcelain 2>/dev/null                                        # uncommitted work
git log @{u}.. --oneline 2>/dev/null                                      # unpushed commits
git ls-files | grep -Ei '(^|/)\.DS_Store$|(^|/)\.env$|/node_modules/|/\.venv|\.pyc$' 2>/dev/null
```

- **Runs.** List every `.workflow/<slug>/` with its status. A `drafting`/`complete` run with no
  commit touching it in ~14 days is ⚠️ "stalled -- park it or finish it". A `parked` run older
  than ~90 days is ⚠️ "still wanted?". `done` runs are ✅, counted not listed. A run folder
  missing `brainstorm.md`, or a `done` run still holding `patch_plan.md`/an
  `## Execution state` block, is ⚠️ (wrap didn't archive properly). A ticket `awaiting-human`
  for more than ~7 days is ⚠️ "operator step pending — run it or park the run".
- **Review deferrals.** `TODO.md`'s `## Review deferrals` lines older than ~90 days are ⚠️ "still
  wanted? fold into a run or archive"; more than ~20 open is ⚠️ "triage before the next brainstorm".
- **v1 leftovers.** Flat `.workflow/*.md` files are ⚠️ "migrate into `.workflow/<slug>/`" (see the
  workflow README); a gitignored `.workflow/` is 🔴 -- runs are the repo's history.
- **One home per idea.** A `TODO.md` item naming the same thing as a parked run is ⚠️ -- archive
  the TODO line with a pointer to the run.
- **Tracked junk / secrets.** A committed `.DS_Store`, `.env`, virtualenv, build output, or `.pyc`
  is 🔴 (secrets) or ⚠️ (junk). A tracked `.env` is always 🔴 -- flag loudly.
- **Uncommitted or unpushed work.** If the repo treats push as its archive/safety net, unpushed
  commits or a dirty tree are ⚠️ worth surfacing.

### 5. Config health

- **`.gitignore` coverage.** Confirm it ignores the usual junk (`.DS_Store`, `.env`, venvs, build
  output). Missing common entries are ⚠️.
- **Light secret sniff.** Only flag obvious committed credential files or `.env`; do not attempt a
  deep secret scan (too noisy) -- point at a dedicated tool if the user wants depth.

### 6. Seat & skill performance, reviewer exam set

Models earn seats on **trial runs**, not exams: every `workflow wrap` appends a `WORKLOG.md`
entry with a `Run:` line (tickets · review cycles · deviations · findings overturned) and a
`Seats:` line (model per phase). Checkup turns those into a per-seat comparison and
*detects the need* to promote, demote, or run the one exam. It never edits `ROUTING.md`.

```sh
grep -nE '^\s*- (Run|Seats):' WORKLOG.md 2>/dev/null | tail -30        # recent run evidence
ls evals/strict-reviewer/code-review-*.md 2>/dev/null | wc -l          # reviewer exam cases (cap 8)
grep -rl '\.workflow/' evals/ 2>/dev/null                              # cases pointing at deleted scratch
tail -20 evals/strict-reviewer/RESULTS.md 2>/dev/null                  # last recall checks
```

- **Per-seat table.** From the last ~10 entries, group by seat → model and average cycles,
  deviations, and (for the reviewer) overturned findings. Read the incumbent per seat from the
  `workflow` skill's `ROUTING.md`. Print the table; it *is* the evaluation.
- **Pending skill proposals.** `find . ~/.agents -name 'SKILL.md.proposed' 2>/dev/null` and any
  `SKILL-IMPACT.md` row with outcome `proposed`: ⚠️ "awaiting your accept/reject — `mv` to accept,
  delete and mark `rejected` to decline". Never accept or reject on the human's behalf.
- **Skill trials.** Entries also carry `Skills: <skill>@<sha>`. For each `trialing` line in the
  skills repo's `SKILL-IMPACT.md`, compare `Run:` numbers for entries at the new sha against the
  entries before it: once the trial count is reached, ⚠️ "trial complete -- better / worse / no
  signal, N runs"; worse means recommend reverting. Never edit the skill. Compare only like with
  like: v2.02 entries count checklist steps (≤12), v2.1 entries count tickets (≤8), so across that
  boundary compare review cycles and deviations only.
- **Trial in progress.** A model on a seat with only one run: ✅ note "trial, 1 run -- needs one
  more before judging".
- **Promotion candidate.** A non-incumbent with ≥2 runs that ties or beats the incumbent on
  cycles and deviations: ⚠️ recommend the human promote it in `ROUTING.md` (quote the row).
- **Regression.** The incumbent's last 2–3 runs clearly worse than its earlier average, or a
  candidate worse than the incumbent: ⚠️ say so with the numbers; the decision is the human's.
- **Missing evidence.** Recent entries without `Run:`/`Seats:` lines: ⚠️ the wrap step is being
  skipped -- nothing can be judged until it isn't.
- **Stale routing.** `ROUTING.md`'s *Last verified* date > 90 days old, or a *Trial* entry with no
  run in the last ~10 entries: ⚠️ re-verify model IDs in the picker / clear or use the trial.
- **Reviewer exam set.** Cases referencing a `.workflow/` path are 🔴 (the scratch is gone; the case
  is worthless). More than 8 cases is ⚠️ (rolling cap; recommend a human prune). A case without
  an inlined diff or its P0/P1 lines is ⚠️. Zero cases is ✅ -- the set only grows on genuine
  misses, and an empty set means none were recorded, not that the asset is failing.
- **Unchecked reviewer.** The strict-reviewer model in `ROUTING.md` has no passing entry in
  `evals/strict-reviewer/RESULTS.md` and the set has ≥3 usable cases: ⚠️ recommend
  `evals.run reviewer`. No other seat is examined -- do not recommend exams for them.

## Output format

Print a compact, scannable report grouped by the six sections, each finding one line with its
severity, the evidence, and the fix. Close with a **prioritized action list** (🔴 first) and, if the
user opted into fixes, offer the safe ones one at a time.

```text
## Workspace checkup — <repo> (<date>)

### Skills        ✅/⚠️/🔴  <one line per finding + fix>
### Memory        ...
### Docs          ...
### Workspace     ...
### Config        ...
### Seats         ...

### Recommended next
1. 🔴 <highest-value fix> — <how>
2. ⚠️ <next> — <how / delegate to memory.compact / evals.run reviewer / edit ROUTING.md>
...
```

If nothing is wrong, say so plainly ("✅ Workspace is healthy — nothing to act on") instead of
manufacturing findings.

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
- `evals.run reviewer` — owns the one exam (reviewer recall on ≤8 diffs); checkup only audits
  that set and flags an unchecked reviewer.

Keep this skill's `description` under ~900 characters (it enforces that rule on others -- it must
pass its own check).
