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
- **Decision:** When a checker condition matches on an ID, a date, a lane or a kind, add one case in which only that key differs. When a review finds one untested key, list every key the guard matches on and mutate each. A line or size window the guard reads (`lines[:12]`) is a key: add a case just past it and mutate its edges. Measure doc growth in words, not lines, because unwrapping text meets a line cap. When a check parses a field another check already parses, reuse that pattern, and test one case per real form found in the corpus (a `fullmatch` on `done @ <sha>` missed the six plans that add a note after the sha). A new gate placed beside an existing one gets a desk check on the class it targets, run on a case the gate must refuse.
- **Supersedes:** —
- **Superseded by:** —
- **Last confirmed:** 2026-10-28
- **Source:** run-ratio-and-retire C1-1 (run gate matcher narrower than the corpus), lean-runs C1-1 (lane gate), growth-ratchets C1-1 (ticket key), C2-1 (waiver kind), C1-2 (line cap met by unwrapping); guard-keys P3-1 (a doc ticket's Verify greps one phrase per rule, so grep every phrase that carries the rule, one key per grep); memory-patterns-and-budget C1-2 (Verify greps left out the deciding words of two rules), C1-1 (a new cost-test gate had no desk check on operating rules, so a failing rule had no destination); lean-skill-hubs C1-1 (the ledger's 12-line contents window was the one mutation the writer's sweep missed)

### After moving text, grep every relative pointer in the moved and kept files
- **Topic:** Review practice: doc moves
- **Status:** current
- **Decision:** A sentence ledger proves no sentence was lost, not that "above", "below", "step N" or "this file" still point at the right place. In the ticket that moves text, grep those words in every moved and kept file and read each hit in place; also grep each renamed heading and file name.
- **Supersedes:** -
- **Superseded by:** -
- **Last confirmed:** 2026-10-28
- **Source:** lean-skill-hubs C1-2 (five stale pointers left by the moves, found in review)
