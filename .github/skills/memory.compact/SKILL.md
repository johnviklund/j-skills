---
name: memory.compact
description: >
  Compact and reconcile the repo's memory pages (memory/<slug>.md, indexed by
  MEMORY.md): merge pages that make the same claim, split legacy inline
  MEMORY.md entries into pages, and identify stale, superseded, archive-only,
  doctrine-misfiled, and skill-promotion-candidate pages (Occurrences 3+),
  producing a proposed index and page set. Reads done .workflow/<slug>/ runs
  and existing skill frontmatter as context. Run manually when memory feels
  bloated or keeps re-explaining the same principle. Recommends a cross-family
  critic for major passes. Never overwrites MEMORY.md, memory/, DESIGN.md, or
  any SKILL.md directly — writes proposals.
---

# memory.compact — Manual Memory Compaction

Reduce memory to its essential active pages without losing audit trail or searchable history.

## Memory Layers

- **Active memory:** `memory/<slug>.md` pages, indexed by `MEMORY.md` (one line per page: slug,
  claim, occurrences, last confirmed). Read at session startup via the index; a page is opened
  when its line matches the situation. Layer of **last resort** — environment facts, durable user
  preferences, repo-specific gotchas/workarounds, temporary in-flight state, and open gaps: things
  a future session needs that fit nowhere else. Bounded and compact. **Not** a product/architecture
  ledger, design ledger, operating-rules doc, or how-to principle store — those belong to the owners
  below. Compaction should actively move misfiled doctrine out, not just tidy it in place.
- **Page shape** (every page, no exceptions): `# <claim>` · `Applies when:` · `Root cause:` ·
  `Fix:` · `Evidence:` (one entry per occurrence — run slug or sha) · `Occurrences: N · Last
  confirmed: <date> · Status: active | superseded by <slug> | retired` · `Enforced by: judgement |
  pending — <TODO line> | <check>` (absent on legacy pages = unclassified) · optional `Promoted to: <skill>`.
- **Product doctrine:** `PRODUCT.md`, when the repo has one. Checked for pages that are really
  product shape, vocabulary, or workflow doctrine misfiled in memory. **Do not edit `PRODUCT.md`
  during a compaction** — flag the page as doctrine-misfiled and propose relocating it, since
  canonical product/design docs are changed only on explicit human approval.
- **Agent operating contract:** `AGENTS.md`, checked for rules already promoted out of memory.
- **Operator reference:** `README.md`, checked for workflow/setup/output guidance already promoted
  out of memory.
- **Archive memory:** `MEMORY_ARCHIVE.md`, searched by memory workflows but not loaded by default.
  Store superseded pages, long evidence, historical baselines, and superseded decisions here.
- **Reusable principle:** a skill under `.github/skills/<name>/SKILL.md` (repo-local) or the
  shared `j-skills` repo's `.github/skills/<name>/SKILL.md` (available from every repo).
  Checked for pages already promoted (`Promoted to:`), and for pages that are candidates
  (`Occurrences: 3` or more, reusable beyond one feature, stripped of schema-specific detail).
- **Design doctrine:** `DESIGN.md`, when the repo has one. Checked for duplicated UI/design-system
  prose that should live there instead of in a page.
- **Run records:** `.workflow/<slug>/` folders, kept by the `workflow` skill after wrap (`Status:
  done`). Read-only evidence: a done run's `review.md`/`learnings.md` can confirm or contradict a
  page, and a page's `Evidence` entries should resolve to a run slug or a sha.
- **Session breadcrumbs:** `~/.ai-memory/<repo-id>/sessions.log`, deterministic hook output. Use
  as evidence, not as durable memory.

## When to Use

Run `/compact` when:
- Memory feels bloated or hard to scan
- The index is over the **~40-page / ~40 KB soft ceiling** (a strong trigger — the goal of the
  pass is to get it back under)
- You suspect two pages make the same claim, or pages contradict each other
- After a major architecture change that invalidated multiple pages
- `MEMORY.md` still holds legacy inline entries (v1 `### Topic` blocks) that need splitting into pages
- Pages have long evidence blocks, old baselines, or historical material that should move to
  `MEMORY_ARCHIVE.md`
- A page has reached `Occurrences: 3` and hasn't been promoted
- Periodically, when you feel like it (no fixed cadence)

## Workflow

### 1. Read inputs

Read all of these before starting analysis:

- **`MEMORY.md`** — the index. Every line must resolve to a page; note legacy inline entries.
- **`memory/*.md`** — every page. Parse the shape fields; note pages missing fields.
- **`MEMORY_ARCHIVE.md`** — cold-storage input when present. Search it for duplicates, superseded
  context, and a suitable destination section for archive-only material. Do not treat the whole
  archive as active context.
- **Run records** (read-only context): `.workflow/*/` folders with `Status: done` — scan
  `review.md` and `learnings.md` for content that contradicts or confirms a page, and check that
  page `Evidence` entries resolve to a run slug or a sha in `git log`.
- **CE artifact directories** where the repo uses that convention (read-only context):
  `docs/brainstorms/`, `docs/plans/`, `docs/solutions/`.
- **`AGENTS.md`** — check for pages already promoted.
- **`README.md`** — check for operator-facing pages already promoted.
- **Existing skill frontmatter** — the `name` + `description` of every skill under
  `.github/skills/*/SKILL.md` and the shared `j-skills` repo's `.github/skills/*/SKILL.md`.
  Use this to spot pages whose principle already belongs in one of them, and to avoid proposing a
  new skill that duplicates an existing one.
- **Installed plugin skill names** — `ls ~/.copilot/installed-plugins/*/*/skills/` and
  `~/.codex/skills/`. Cross-check every repo-local skill folder's name against this list; a
  repo-local skill sharing a name with an installed plugin's skill silently shadows it and is a
  bug. Flag any match as a naming-collision candidate (see step 3).
- **`DESIGN.md`** — when the repo has one, check for pages duplicating design-system decisions that
  already live there.

### 2. Cross-family critic recommendation

Ask the user:
> **"What model family was used for the most recent `/remember` extract? A different-family review is recommended for major compactions. Continue with the current model for a proposal-only pass? [y/N]"**

- If same family or unsure: warn that cross-family review is better for major compactions, but
  allow a degraded proposal-only pass for solo-dev cleanup.
- If different family: proceed normally.
- Do not block lightweight proposal generation solely because the model family is unknown.

### 3. Analyze pages

For each page (and each legacy inline entry), classify as:

- **Active** — `Status: active`, `Last confirmed` within 90 days, no contradicting evidence in
  run records, CE artifacts, or codebase.
- **Legacy inline** — a v1 `### Topic` entry still inside `MEMORY.md`. Convert to a page: Topic →
  claim/slug, Decision → Fix, Source → Evidence, `Last confirmed` carried over, `Occurrences: 1`
  unless the entry itself records repeats.
- **Stale** — active but `Last confirmed` > 90 days ago. Flag for re-confirmation or supersession.
- **Superseded** — `Status: superseded by <slug>`. Keep the chain intact; move the page to the
  archive when it no longer shapes normal work, and drop its index line.
- **Same-claim duplicate** — two pages whose claims are the same lesson. Merge into one page: union
  the `Evidence` entries, `Occurrences` = their count, latest `Last confirmed`, the sharper `Fix`.
- **Malformed** — a page missing shape fields, or whose `Occurrences` doesn't equal its `Evidence`
  count, or whose `Evidence` entries don't resolve. Propose the corrected page.
- **Archive-only** — useful for search, audit, or historical reconstruction but not
  behavior-shaping enough for startup context. Move to `MEMORY_ARCHIVE.proposed.md`.
- **Contradicted** — a done run, CE artifact, or the code conflicts with the page. Flag with the
  specific run slug / artifact reference.
- **Promoted** — page already promoted to `AGENTS.md`/`README.md` (or carries `Promoted to:`). If
  nothing beyond the pointer remains, archive it; a page with evidence stays as the why.
- **Retire** — `Enforced by:` names a check that exists, or `Status: retired`. Move to the archive
  proposal and drop the index line; the check is now the reminder.
- **Skill-promotion candidate** — `Occurrences: 3` or more, `Enforced by: judgement`, no `Promoted to:`, reusable beyond this
  one feature/schema, not already in an existing skill. Never below 3 — that stays a page. Name
  which existing skill it should extend, or, only if none fits, that a new one is warranted.
- **Skill-duplicated** — the page restates a principle an existing skill already covers. Collapse
  the `Fix` to a pointer, or archive.
- **Plugin-name collision** — separate from page analysis: any repo-local skill folder whose name
  matches an installed plugin's skill name. Always a bug; surface it and recommend a repo-specific
  prefix.
- **Design-duplicated** — restates a `DESIGN.md` section. Collapse to a pointer or archive; the
  durable version belongs in `DESIGN.md`, refined in place.
- **Doctrine-misfiled** — the page *is* product/architecture doctrine, a design decision, or a
  stable operating rule that belongs in `PRODUCT.md`, `DESIGN.md`, or `AGENTS.md`. Flag for
  **relocate-and-delete**: propose the destination and the text to move; the proposed memory keeps
  at most a one-line pointer. **Never edit `PRODUCT.md`/`DESIGN.md` yourself** during a compaction.

### 4. Rebuild the index

The proposed `MEMORY.md` is index lines only, sorted by `Occurrences` descending then slug —
the pages that recur most are the ones a fresh session should see first. Stale pages get a
`<!-- STALE: last confirmed YYYY-MM-DD -->` suffix on their index line; superseded and
archive-only pages are omitted from the index and written to the archive proposal with enough
claim text to remain searchable.

### 5. Cross-page consistency check

Look for:
- Two active pages on the same claim (missed duplicates)
- `superseded by` targets that don't exist
- Pages contradicted by current source code or a done run's `review.md` (if checkable)
- Pages at `Occurrences: 3`+ with no `Promoted to:` and no candidate proposal
- Duplicated or near-duplicated guidance across `README.md`, `AGENTS.md`, pages, the archive,
  existing skills, and `DESIGN.md`
- Anything in `MEMORY.md` that is not an index line
- Index lines whose count or date disagrees with the page

### 6. Produce output

The first run for a repo or major cleanup must be proposal-only. Write the proposed index to
**`MEMORY.proposed.md`** and the proposed page set to **`memory.proposed/`** (a full mirror of
`memory/` as it should be after the pass — every page, changed or not, so acceptance is a single
swap). When pages should move to the archive, also write **`MEMORY_ARCHIVE.proposed.md`**; if the
repo has no `MEMORY_ARCHIVE.md` yet, create the proposed archive in a compact topical format.

**NEVER overwrite `MEMORY.md`, `memory/`, `MEMORY_ARCHIVE.md`, `PRODUCT.md`, `DESIGN.md`, or any `SKILL.md` directly.**

The proposed index includes a summary block at the top, starting with the **source sha** the
proposal was computed from — acceptance is refused if memory moved after it:
```
<!-- Compaction summary:
     Source: <git sha of HEAD when the proposal was written>
     Input: N pages + L legacy inline entries (soft ceiling ~40 pages)
     Active: X | Stale: Y | Superseded: Z | Same-claim merges: W | Malformed fixed: F
     Contradicted: C | Skill-promotion candidates (Occurrences 3+): S
     Doctrine-misfiled (relocate-and-delete): D
     Cross-file overlaps: R README | A AGENTS | Pr PRODUCT | M archive | K skill | De design
     Net: N → M pages (under ceiling? yes/no)
-->
```
Each changed page in `memory.proposed/` carries a one-line HTML comment at the bottom saying
what was merged, converted, or corrected and why.

If skill-promotion candidates were found, also write **`skill-promotion-candidates.proposed.md`**
listing each candidate principle (stripped of schema-specific detail), the page it comes from,
which skill it should extend (or that a new skill is warranted), and the reminder that the
accepting edit gets a `SKILL-IMPACT.md` line and a trial, per `memory.remember`. Never edit a
`SKILL.md` from `/compact`.

Also write a short duplication report into the final user report, naming overlaps across
`README.md`, `AGENTS.md`, pages, the archive, existing skills, and `DESIGN.md`, and which layer
should own each.

### 7. Report to user

Print:
- Summary statistics (pages before/after, legacy entries converted, what was merged or archived)
- Index and page-set size reduction; archive size change
- Pages flagged as contradicted (with run slug / artifact references)
- Promotion candidates for `AGENTS.md`
- Skill-promotion candidates, with the target skill named (or "new skill warranted" only when the
  bar is genuinely cleared)
- Plugin-name collisions found, named explicitly
- Cross-file duplication report across README/AGENTS/pages/archive/skills/design
- Instruction: **"Review: `diff MEMORY.md MEMORY.proposed.md` and `diff -r memory memory.proposed`"**
- If archive changes were proposed: **"Review the archive diff: `diff MEMORY_ARCHIVE.md MEMORY_ARCHIVE.proposed.md`"**
- If skill-promotion candidates were found: **"Review the candidates: `cat skill-promotion-candidates.proposed.md`"**
- Instruction — **accept as one guarded sequence, never piecemeal** (print it filled in with the
  proposal's `Source:` sha):
  ```sh
  git diff --quiet <source-sha> HEAD -- MEMORY.md memory MEMORY_ARCHIVE.md \
    && git diff --quiet -- MEMORY.md memory MEMORY_ARCHIVE.md \
    || { echo "memory changed since the proposal — re-run memory.compact"; exit 1; }
  [ -f MEMORY_ARCHIVE.proposed.md ] && mv MEMORY_ARCHIVE.proposed.md MEMORY_ARCHIVE.md   # archive first: nothing is dropped before it lands
  git rm -rq memory && mv memory.proposed memory && mv MEMORY.proposed.md MEMORY.md
  git add MEMORY.md memory MEMORY_ARCHIVE.md && git commit -m "memory.compact: <N> → <M> pages"
  ```
  The stale check fails if `memory.remember` (or anyone) wrote a page after the proposal, or if
  the working tree is dirty; the fix is to re-run `/compact`, not to force it. The originals stay
  recoverable from git (`git checkout <source-sha> -- memory MEMORY.md`) until the commit is
  reverted or rewritten.

## Rules

- Run records and CE artifacts are **read-only input**. `/compact` may flag pages as contradicted
  by them, but never modifies, tags, or archives anything under `.workflow/` or `docs/`.
- Tombstone or archive, don't silently delete. Superseded pages stay in the archive with enough
  context to search; a page with evidence is never deleted, only moved.
- Never overwrite `MEMORY.md`, `memory/`, or `MEMORY_ARCHIVE.md`. Always write proposal files,
  stamped with the source sha; acceptance is the guarded sequence above and stops if memory moved.
- Never edit a `SKILL.md`, `PRODUCT.md`, or `DESIGN.md` directly from `/compact`. Skill, product,
  and design relocations (including doctrine-misfiled pages) are proposals for the user to apply.
- The compacted memory should end **under the ~40-page soft ceiling**; if it can't without losing
  genuinely current, admission-test-passing pages, say so and recommend redistribution rather than
  quietly leaving it oversized.
- Don't propose a skill for anything below `Occurrences: 3`; a single striking page is still just
  a good page.
- No state tracking. No cadence. No automatic triggering. This is a manual tool the user runs when
  they want to.
- Aggregates only. Never persist customer-level details.
