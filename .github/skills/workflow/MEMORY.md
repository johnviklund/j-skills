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
  canonical clone. The canonical, push-able clone lives at
  `~/Work/j-skills` (see root `README.md`, "Setup"). A
  workflow run that executes entirely inside the disconnected snapshot has no commits, no diffs,
  and no `Base` shas — every phase that assumes Git must fall back to file-based verification and
  say so explicitly. Before committing/pushing any workflow-skill change, confirm which copy is
  actually being edited (`git -C <dir> rev-parse --is-inside-work-tree`); if it's the snapshot,
  sync the diff into `~/Work/j-skills/.github/skills/workflow/` and commit
  there, not in the snapshot.
- **Supersedes:** —
- **Superseded by:** —
- **Last confirmed:** 2026-08-26
- **Source:** `workflow realign` run — drafted in the disconnected snapshot, reconciled into the
  real clone at wrap+commit time
