# Memory write limits

## The AGENTS.md cost test

Before any addition or promotion to `AGENTS.md`, ask: would removing this rule
cause a mistake on a typical task in this repo? If no, route it to a memory page that passes
the admission test or its owning skill reference, leaving at most a one-line pointer in `AGENTS.md`.
A rule this test keeps out of `AGENTS.md` counts as fitting nowhere else for the admission test's item 2.
With a stated line cap, if the file is within 10% of it or over it, the pass
names one existing line to remove or move and does so in the same pass. With no stated cap,
only the removal test runs. See `agent-docs` for Context load.

## Keeping memory bounded (cap + consolidate-before-add)

Memory has no automatic compaction, so this skill enforces the bound at write time (inspired by
bounded-memory designs like Hermes, where an over-limit write is refused until the agent consolidates):

- Treat roughly **~40 pages / a ~40 KB index** as a soft ceiling. Near or over it, **consolidate
  before adding**: merge overlapping pages into one (sum the evidence, keep the higher count), or
  route/drop stale ones, in the same pass — do not just add a page.
- The repeat rule in `SKILL.md` is the main lever: most "new" lessons are a fourth occurrence of an existing
  page, not a page.
- If consolidation can't get a genuinely new, test-passing page to fit under the ceiling, that is the
  signal to run `memory.compact` (or redistribute pages to their canonical owners) rather than let
  the folder grow.

