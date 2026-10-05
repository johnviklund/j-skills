---
name: memory.remember
description: >
  Capture durable learnings, new feature behavior, and operating rules from the
  current session, then write them directly into the current repo's memory
  pages (memory/<slug>.md, indexed by MEMORY.md) and related repo-local docs in
  one pass — a repeat bumps an existing page's occurrence count instead of
  adding a line; a repeated mechanical mistake becomes a guardrail ticket, and
  3 occurrences of a judgement call promote it into a skill (logged in
  SKILL-IMPACT.md and trialed); DESIGN.md is refined in place when present.
  Use when the user says "remember this", "save this for later", "update
  memory", "curate learnings", or asks to record a new workflow, repo rule,
  design decision, or important lesson — including at the end of a
  brainstorm/plan/execute/review workflow pass.
---

# memory.remember

Persist the parts of this session that future sessions should not have to rediscover, while keeping repo startup memory small.

## Scope

This is a global skill, available from any repo via both Codex CLI and Copilot CLI — not tied to one project or product line.

Default target:
- the repo in the current working directory

Also update the shared `j-skills` repo when the learning changes:
- a shared skill itself (this one, `memory.compact`, or any other skill living in `j-skills`)
- a cross-repo convention or workflow step that applies beyond the current repo

## Memory Layers

Treat repo memory as separate layers with different owners:

- **Agent operating contract:** `AGENTS.md`, read by agents during startup. Use it for stable repo operating rules, command contracts agents must follow, and high-risk gotchas that prevent repeated mistakes.
- **Operator reference:** `README.md`, read by humans and agents when workflow/setup/output shape matters. Use it for setup, command examples, workflow descriptions, output structure, and troubleshooting.
- **Active memory:** `memory/<slug>.md` pages, indexed by `MEMORY.md` (which is read at session
  startup; a page is opened when its index line matches the situation). It is the layer of **last
  resort** — the place for things a future coding session needs but that fit **nowhere else**:
  model/agent-relevant facts, the working environment (OS, tools, paths, credential locations),
  durable user preferences, repo-specific gotchas and workarounds, temporary in-flight state
  ("X is suspended until repaired"), and known open gaps. It is **bounded and must stay compact**.
  It is **not** a product/architecture ledger (that is `PRODUCT.md`), a design ledger (`DESIGN.md`),
  an operating-rules doc (`AGENTS.md`), or a home for durable how-to principles (a skill). If a
  candidate fits one of those, it goes **there**, not here. A one-line pointer to a canonical owner
  is fine; duplicated doctrine is drift.
- **Archive memory:** `MEMORY_ARCHIVE.md`, searched on demand. Use it for superseded decisions, stale baselines, source-list history, long explanations, and evidence-heavy details that should not load by default.
- **Detailed solution notes:** `docs/solutions/`, used for postmortems, durable patterns, implementation reasoning, and evidence-heavy write-ups that need more detail than startup memory.
- **Reusable principle:** a **skill** under `.github/skills/<name>/SKILL.md` (repo-local) or the shared `j-skills` repo's `.github/skills/<name>/SKILL.md` (available from every repo). Use it for a transferable "how to design/review/build X" practice that has proven itself beyond this one feature or schema — not a repo-specific decision or gotcha. This is the layer active `MEMORY.md` should hand off to instead of accumulating principle prose indefinitely.
- **Design doctrine:** `DESIGN.md`, when the repo has one. Use it for durable UI/design-system decisions — a new component convention, token usage, or layout pattern. Unlike every other layer here, it is a living reference doc, not an append-only log: refine the relevant section in place rather than tacking on a dated entry.
- **Session breadcrumbs:** `~/.ai-memory/<repo-id>/sessions.log`, written by hooks. Use it as deterministic recent-session evidence only.

Repo-local durable memory lives in the repo. Do not use `~/.codex/memories/` as the source of truth for repo memory.

## Memory schema — pages, not entries

`MEMORY.md` is the **index**: one line per page, nothing else —
`- [<slug>](memory/<slug>.md) — <claim in one line> · occurrences N · <last confirmed>`.
Every durable lesson is a **page** at `memory/<slug>.md` (kebab-case slug from the claim), always
this shape:

```markdown
# <claim in one line>
Applies when: <the situation that should trigger recall>
Root cause: <why it happens — one or two lines>
Fix: <what to do — concrete, with paths or commands where they exist>
Evidence: <run slug or sha> · <run slug or sha>          ← one entry per occurrence
Occurrences: N · Last confirmed: YYYY-MM-DD · Status: active | superseded by <slug> | retired
Enforced by: judgement | pending — <TODO line> | <the check, type or structure, and its command>
Promoted to: <skill name>                                 ← only once promoted
```

`Enforced by:` is set when the page is classified (see *Repeats escalate to enforcement*); a
legacy page without it is unclassified. `Status: retired` means the enforcer now makes the
mistake impossible: the page leaves the index and moves to `MEMORY_ARCHIVE.md` as the why.

**A repeat is not a new page.** Before creating one, search existing pages by claim (`grep -il`
on the key nouns of `memory/*.md` and the index): a match means append an `Evidence` entry, bump
`Occurrences`, update `Last confirmed`, and refine the `Fix` if the new occurrence taught
something. The count is what makes promotion mechanical — so it must be honest:

- **One run, one occurrence.** An `Evidence` entry is a run slug (or a sha outside a run) and is
  **unique per page**: if the page already lists this run, do not append and do not bump. Routing
  the same run three times — mid-run, at wrap, after an interrupted wrap — leaves `Occurrences`
  exactly where one routing left it. `Occurrences` always equals the number of distinct entries.
- **Routed lines are marked, then skipped.** After routing a tagged line in
  `.workflow/<slug>/learnings.md`, append ` [routed → <destination> <YYYY-MM-DD>]` to that line in
  place; a line already carrying the mark is skipped on every later pass. The mark is the routing
  receipt and survives resets because it lives in the tracked run folder.
- **A promotion is applied once.** Before promoting at `Occurrences: 3`, check the page for
  `Promoted to:` and `SKILL-IMPACT.md` for a row on the same page: an existing `proposed` or
  `trialing` row means the promotion is pending or done — do not create a second. Legacy v1 inline entries still in
`MEMORY.md` (the old `### Topic` blocks) are read as pages-to-be; `memory.compact` splits them.

## Repeats escalate to enforcement

Assume the next agent sees only the files it opened, copies the nearest example, and takes the
shortest path that passes. A page or an `AGENTS.md` line works only when that agent reads it; a
check fires whether it was read or not. So a mistake that repeats earns enforcement, not more
prose.

**At the second occurrence** (or the first, when the fix is obvious), classify the page:

- **Mechanical** — a tool could detect it: a banned call, an import shape, a file location, a
  missing step, a state that should be unrepresentable. Pick the highest rung that works:
  1. **Structure** — one owner per piece of state, one supported way per task, internals hidden
     so the wrong import fails, one source of truth instead of hand-synced lists, and the old way
     deleted so no agent copies it.
  2. **Types** — the bad state cannot be written.
  3. **A check** (lint rule, CI job, hook, or a grep in the repo's lint command) whose error names
     the file, type or function to use instead. On a pattern already common, fail only on
     additions. Same command locally and in CI.
  4. **A test** of the behaviour — one that would fail if the code returned nothing.

  Write `workflow todo Guardrail: <rung> — <the check> · must fail on <Evidence sha> · memory/<slug>.md`
  and set `Enforced by: pending — <that TODO line>`. The ticket proves the check goes red on the
  real past mistake and green on HEAD; a check never seen failing proves nothing. When that run
  routes its learnings, set `Enforced by:` to the check and `Status: retired`.
- **Judgement** — no tool can decide it (cross-file consistency, naming fit, product tone). Set
  `Enforced by: judgement`. It stays a page the reviewer reaches, and only these pages are
  promoted to a skill at `Occurrences: 3`.

**A repeat on a page that already has an enforcer** means the enforcer is too narrow or unwired:
the fix is a new guardrail ticket to widen or wire it, never another occurrence of prose.
A mechanical page that reaches 3 still unenforced gets its guardrail ticket in this pass.

## The memory admission test

Before writing any page, run every candidate through this gate. It may stay in
active memory **only if all four are true**:

1. **Useful next session** — a future coding session would waste time or repeat a mistake without it.
2. **Fits nowhere else** — it is not product/architecture doctrine (`PRODUCT.md`), a design decision
   (`DESIGN.md`), an operating rule / command contract (`AGENTS.md`), or a transferable how-to
   principle (a skill). If it fits one of those, route it **there** and do not also keep it here.
3. **Concrete and repo-specific** — a gotcha, environment fact, preference, temporary state, or open
   gap — not a durable principle and not a design/product decision.
4. **Not already owned elsewhere** — if a canonical owner already states it, keep at most a one-line
   pointer, never a copy.

If a candidate fails the test, it does not "wait" in memory to be promoted later — that deferral is
exactly how memory drifts into a second product/design ledger. Route it to its real home in the
**same pass**, or drop it.

## Keeping memory bounded (cap + consolidate-before-add)

Memory has no automatic compaction, so this skill enforces the bound at write time (inspired by
bounded-memory designs like Hermes, where an over-limit write is refused until the agent consolidates):

- Treat roughly **~40 pages / a ~40 KB index** as a soft ceiling. Near or over it, **consolidate
  before adding**: merge overlapping pages into one (sum the evidence, keep the higher count), or
  route/drop stale ones, in the same pass — do not just add a page.
- The repeat rule above is the main lever: most "new" lessons are a fourth occurrence of an existing
  page, not a page.
- If consolidation can't get a genuinely new, test-passing page to fit under the ceiling, that is the
  signal to run `memory.compact` (or redistribute pages to their canonical owners) rather than let
  the folder grow.

## Workflow

When the user invokes `/remember`:

1. **Read context**
   - Read `MEMORY.md` (the index) and `AGENTS.md` in the current repo; open only the `memory/` pages whose index line plausibly matches a candidate.
   - Read the `name` + `description` frontmatter of every skill under `.github/skills/*/SKILL.md` (repo-local) and the shared `j-skills` repo's `.github/skills/*/SKILL.md` — just the frontmatter, not the full body — so you know what already exists before proposing a new skill or a new bullet in one.
   - **Also list every installed plugin's skill names** — e.g. `ls ~/.copilot/installed-plugins/*/*/skills/` and `~/.copilot/installed-plugins/_direct/*/skills/` (Copilot), and `ls ~/.codex/skills/` (Codex, which mirrors plugin-provided skills alongside repo-local symlinks). You need these names for one reason only: never propose a new repo-local skill whose name collides with one of them (see the naming-collision rule in step 2).
   - Check whether the repo has a `DESIGN.md` and, if this session was a `workflow` run, which `.workflow/<slug>/` folder it was (see step 3).
   - Read `~/.ai-memory/<repo-id>/sessions.log` for recent session entries (last 10). If it does not exist, skip it gracefully.
   - Read recent git history: `git log --oneline -20`.
   - Read `README.md` only if the learning changes operator-facing setup or features.
   - Read `MEMORY_ARCHIVE.md` only when needed to check likely duplicates, superseded context, or archive destinations.

2. **Classify the target layer before writing**
   - `AGENTS.md`: stable operating rules, command-contract requirements, agent workflow boundaries, repeated gotchas, and "never do X" guidance.
   - `README.md`: operator-facing setup, usage, workflow shape, output structure, and troubleshooting.
   - A `memory/` page: current behavior-shaping lessons that future sessions need but that are not yet stable enough or broad enough for AGENTS/README — as a new page, or an occurrence on an existing one.
   - `MEMORY_ARCHIVE.md`: history, evidence, old baselines, long explanations, and superseded decisions.
   - `docs/solutions/`: detailed postmortems, implementation patterns, and reusable technical explanations.
   - **A skill:** a transferable, schema-agnostic *principle* — "how to design/review/build X well" — that has proven itself across more than this one feature. This is the layer that keeps `MEMORY.md` from becoming an ever-growing pile of principle prose that nobody reads at startup. Apply the promotion bar before choosing this:
     - **Existing skill first.** If a skill already covers this domain (check the frontmatter you read in step 1), add or refine a bullet there instead of creating a new skill.
     - **New-skill bar.** Only create a new skill when the pattern (a) has recurred 3+ times — which now means a page with `Occurrences: 3` or more and `Enforced by: judgement`; a mechanical page gets a guardrail instead (see *Repeats escalate to enforcement*) — (b) is reusable beyond this one feature/schema, and (c) genuinely doesn't fit any existing skill's stated scope. One occurrence is a page, not a skill.
     - **Write it by `agent-docs`.** Invoke the `agent-docs` skill before writing or editing any skill, `AGENTS.md` or memory page. Text a person reads follows the Rules of the `plain` skill.
     - **Every skill edit is logged and trialed — and the log's `Mode:` line decides who applies it.** Read the first line of the skills repo's `SKILL-IMPACT.md`. `Mode: autonomous`: write the `SKILL.md` edit directly, in its own commit (never mixed with code, so it can be reverted alone), and add the row `<date> · <skill> · <what changed> · from: <memory page> · trial until: 3 runs · trialing`. The skills repo is public: write `from:` generically ("retro of a work run", "a user review"), never another repo's name, run slugs or data. `Mode: approve`: do not touch `SKILL.md`; write the full proposed file as `SKILL.md.proposed` beside it, add the same row with outcome `proposed`, and tell the human `accept: mv <path>/SKILL.md.proposed <path>/SKILL.md` (they flip the row to `trialing` on accepting). Either way the source page gets `Promoted to: <skill>` and stays as the why; `checkup seats` judges the change on the runs after it. Missing `Mode:` line = approve.
     - **Never collide with an installed plugin's skill name.** Before naming a new skill (or matching it against an "existing skill" to extend), check it against the plugin skill list you gathered in step 1. A repo-local skill folder that shares a name with an installed plugin's skill silently shadows that plugin's real skill in this repo — the plugin skill becomes permanently unreachable here, even though it looks installed. This is not a hypothetical: it has already happened (a repo-local `ce-debug` shadowed the `compound-engineering` plugin's real `ce-debug`, a completely different and more capable skill). If the name collides, pick a different, repo-specific prefix instead (e.g. `acme-` for an Acme repo) — never reuse a plugin's namespace for repo-local content, even if the plugin's naming convention looks like a natural fit.
     - **Strip before writing.** A skill entry is the principle only — no concrete schema, object/column/field names, file paths, or business logic. Those stay in the code and in `MEMORY.md`.
   - **`DESIGN.md`** (only if the repo has one): durable UI/design-system decisions. Refine the relevant section in place — it is a living doc, not an append-only log. If a change would contradict or majorly restructure an existing section, flag it instead of overwriting.
   - If the right owner already contains the lesson, update that owner instead of copying the same prose into active memory.

3. **Detect CE sessions and workflow scratch**
   - Check if any files under `docs/brainstorms/`, `docs/plans/`, or `docs/solutions/` were modified or created in this session.
   - If CE artifacts were touched, capture only session metadata and a short pointer to the durable CE note. Do not duplicate the full pattern write-up in active memory.
   - Separately, check for a `workflow` run folder, `.workflow/<slug>/` (tracked, kept after wrap as the run's record — not the CE `docs/plans/`/`docs/brainstorms/` convention). If its `learnings.md` exists, treat its `[durable→skill]` / `[durable→memory]` / `[durable→design]` / `[drop]` tagged lines as the primary candidate list for this pass — they've already been pre-classified by the session that wrote them — and use the run slug as the `Evidence` entry on every page it touches.

4. **Extract and reconcile in one pass**
   - Produce candidate pages in the page shape above.
   - Check each candidate against `AGENTS.md`, `README.md`, the `MEMORY.md` index and matching pages, `MEMORY_ARCHIVE.md`, existing skills, and `DESIGN.md` before writing.
   - Reconcile each candidate against its canonical owner:
     - **Repeat of an existing page:** if this run slug is not yet in `Evidence`, append it, bump `Occurrences`, update `Last confirmed`, refine `Fix` if warranted — no new page; if the slug is already there, only refine `Fix`. From the second occurrence, classify and escalate as in *Repeats escalate to enforcement*
     - **New page:** write `memory/<slug>.md` and add its index line to `MEMORY.md`
     - **Supersede existing:** set the old page `Status: superseded by <new-slug>`, drop it from the active index (keep the file for the chain, or move it to the archive)
     - **Archive-only:** write it to `MEMORY_ARCHIVE.md` instead of active memory
     - **Promote:** update `AGENTS.md` or `README.md`, then archive or omit the duplicate memory copy
     - **Promote to skill:** add the stripped principle to an existing skill, or create a new one only if it clears the new-skill bar above; log it in `SKILL-IMPACT.md`; mark the page `Promoted to:` — the page stays (it is the why and the evidence)
     - **Refine design doc:** update the relevant `DESIGN.md` section in place when the repo has one
     - **Conflict:** keep the active entry conservative and add a short conflict note only when the contradiction is real and cannot be resolved from the repo

5. **Keep active memory lean during the same pass**
   - Merge pages that make the same claim (sum evidence, keep the higher count).
   - Remove duplicated prose when the rule already lives in `AGENTS.md` or `README.md`, or the principle already lives in a skill.
   - Keep only short pointers in a page's `Fix` when `docs/solutions/` already contains the durable write-up.
   - Move superseded, stale, verbose, or low-frequency historical pages into `MEMORY_ARCHIVE.md` and drop their index lines.
   - If `MEMORY_ARCHIVE.md` does not exist yet, create it with a minimal archive header before moving entries.

6. **Write immediately**
   - Update every relevant repo-local file in the same pass:
     - `memory/<slug>.md` pages plus their `MEMORY.md` index lines for active durable lessons
     - `MEMORY_ARCHIVE.md` for cold history
     - `AGENTS.md` for operating rules
     - `README.md` only when the user-facing setup or workflow changed
     - the relevant skill's `SKILL.md` for any promoted principle (new or existing skill), plus its `SKILL-IMPACT.md` line, in their own commit
     - `DESIGN.md` for any refined design-system section, when the repo has one
   - Also update the shared `j-skills` repo when the change affects a shared skill or another cross-repo convention.

7. **Optional wrap-up, when finishing a workflow pass**
   - If `.workflow/<slug>/learnings.md` exists and every tagged line in it has now been routed, say so in one line (`routed N lines → M pages, K skill edits`) — the `workflow` wrap step owns the checks, commit, push, and archiving of the run folder. Never delete or empty anything under `.workflow/`; run folders are kept.
   - This step is optional and only relevant when the session was a `workflow` run; a plain "remember this" ask has no wrap-up to do.

## What to Save

Save to a `memory/` page only what passes the admission test above — typically:

- **Environment facts:** OS, language/runtime quirks, tool availability, key paths, where
  credentials live (never the credentials themselves).
- **Durable user preferences** about how to work in this repo.
- **Repo-specific gotchas and workarounds** — concrete traps with real names (a proc that behaves
  unexpectedly, a command that fails a certain way) that a fresh session would hit.
- **Temporary in-flight state** that changes: "X is suspended until repaired", "Y path is dormant
  until Z is enabled", "endpoint W still lacks guard V" (open gaps).
- **Tried-and-rejected dead ends**, so they are not relitigated.

Everything else routes to its owner in the same pass (do not stage it in memory):

- New feature behavior / product shape / vocabulary → `PRODUCT.md`.
- UI or design-system decisions → `DESIGN.md`.
- Stable operating rules, "never do X", command contracts, ports, write-scope → `AGENTS.md`.
- Transferable "how to design/review/build X" principles (3+ recurrences) → a skill.
- Long evidence / superseded history → `MEMORY_ARCHIVE.md` or `docs/`.

## What Not to Save

- Raw transcripts, case details, event IDs, names, or other PII
- One-off debugging noise
- Duplicate prose across files (route to one owner, keep at most a pointer)
- **Product, architecture, or design *doctrine*** — it belongs in `PRODUCT.md`/`DESIGN.md`, not memory
- **Durable how-to principles** — they belong in a skill, not another memory paragraph
- Speculative ideas that were not actually adopted
- Long CE pattern write-ups already captured under `docs/solutions/`
- Stable operator or agent rules already promoted to `README.md` or `AGENTS.md`
- A single occurrence dressed up as a skill — one instance is a page; `Occurrences: 3` earns a skill

## Rules

- Aggregates only. Never persist customer-level details.
- If nothing durable was learned, say so instead of forcing an update.
- Do not put operational rules in `SOUL.md`; keep identity there and operations in `AGENTS.md`.
- Do not treat memory as a changelog; write only the durable part that should survive. The
  session-level "what was built/changed" log is `WORKLOG.md` (owned by the `workflow` skill), not memory.
- Route product/architecture/design doctrine to `PRODUCT.md`/`DESIGN.md` and durable how-to
  principles to a skill in the **same pass**; never stage them in a page "to promote later".
- Keep memory bounded: near the ~40-page soft ceiling, consolidate or route before adding (see
  *Keeping memory bounded*), and recommend `memory.compact` when it won't fit.
- Do not use active `MEMORY.md` as an evidence warehouse. Move long explanations, superseded history, and low-frequency lookup material to `MEMORY_ARCHIVE.md`.
- Do not load `MEMORY_ARCHIVE.md` during normal extraction unless it is needed to reconcile or archive a specific candidate.
- Before adding active memory, check whether `AGENTS.md`, `README.md`, `MEMORY_ARCHIVE.md`, or an existing skill already owns the same lesson.
- Prefer one canonical owner over duplicated prose. Active memory may point to a canonical owner, but should not repeat it.
- Prefer extending an existing skill over creating a new one. A new skill needs 3+ recurrences, reusability beyond one feature, and a genuine scope gap — see the promotion bar above.
- Strip concrete schema, object/field names, and business logic out of anything written into a skill; skills hold principles, code and `MEMORY.md` hold specifics.
- `DESIGN.md` is refined in place, section by section — never append a dated log entry to it the way you would to a memory page.
- Never delete, empty, or rename anything under `.workflow/` — run folders are the repo's history; the `workflow` skill's wrap step archives them.
- When a shared skill itself changes (this one, `memory.compact`, or any other skill in `j-skills`), update that skill's own docs as part of the same remember pass.
- Every page uses the page shape; `MEMORY.md` holds index lines only. No flat bullets, no inline entries.
- Every `Evidence` entry names a run slug or commit, is unique per page, and `Occurrences` equals the number of entries; a routed learnings line carries its `[routed → …]` mark and is never routed again.
