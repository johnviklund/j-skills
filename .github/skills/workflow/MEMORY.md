# Memory

Active, bounded memory for this repo. Read at session startup. Not a changelog (see
`WORKLOG.md`) and not a product/design ledger (see `PRODUCT.md`/`DESIGN.md` if this repo grows
them) — entries here are environment facts, gotchas, preferences, and open gaps that fit nowhere
else.

### A Copilot-loaded skill folder can be a disconnected snapshot, not this repo
- **Topic:** Environment — Copilot plugin working copy vs. the real clone
- **Status:** current
- **Decision:** Copilot CLI can load this skill's content from a path like
  `~/.agents/skills/workflow` that has **no `.git` at all** — a plugin-install snapshot, not the
  canonical clone. Since 2026-10-05 that is by design: `npx skills` installs copies there, and
  any clone of `johnviklund/j-skills` is the push-able source (see root `README.md`, "Setup"). A
  workflow run that executes entirely inside the disconnected snapshot has no commits, no diffs,
  and no `Base` shas — every phase that assumes Git must fall back to file-based verification and
  say so explicitly. Before committing/pushing any workflow-skill change, confirm which copy is
  actually being edited (`git -C <dir> rev-parse --is-inside-work-tree`); if it's the snapshot,
  sync the diff into a clone's `.github/skills/workflow/`, commit and push there, then run
  `npx skills update -g`; never edit the snapshot.
- **Supersedes:** —
- **Superseded by:** —
- **Last confirmed:** 2026-08-26
- **Source:** `workflow realign` run — drafted in the disconnected snapshot, reconciled into the
  real clone at wrap+commit time

### A new guard needs one test per key it matches on
- **Topic:** Review practice — mutation-checking checker conditions
- **Status:** promoted to `references/tests.md`, `references/phase-4-review.md` and `references/phase-3-execute.md` by guard-keys (2026-10-18); trial closed in `SKILL-IMPACT_ARCHIVE.md`. Kept as the why.
- **Decision:** When a checker condition matches on an ID, a date, a lane or a kind, add one case in which only that key differs. When a review finds one untested key, list every key the guard matches on and mutate each. Measure doc growth in words, not lines, because unwrapping text meets a line cap. When a check parses a field another check already parses, reuse that pattern, and test one case per real form found in the corpus (a `fullmatch` on `done @ <sha>` missed the six plans that add a note after the sha).
- **Supersedes:** —
- **Superseded by:** —
- **Last confirmed:** 2026-10-23
- **Source:** run-ratio-and-retire C1-1 (run gate matcher narrower than the corpus), lean-runs C1-1 (lane gate), growth-ratchets C1-1 (ticket key), C2-1 (waiver kind), C1-2 (line cap met by unwrapping); guard-keys P3-1 (a doc ticket's Verify greps one phrase per rule, so grep every phrase that carries the rule, one key per grep)
