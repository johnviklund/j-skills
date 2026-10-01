# Worklog

A bounded, rolling, git-pointing index of what was built or changed in this repo, newest first.
Not a source of truth and not an archive — canonical docs and the git history own
that; entries only point at commits. Cap: keep roughly the 15 most recent entries; delete the
oldest when appending would exceed that.

## 2026-10-01 · docs refresh, MIT license, workflow v2.1.1 context budget · Sonnet 5.5
- READMEs brought in line with the real wiring (direct symlinks into both CLIs, `j-skills` plugin
  name, lowercase paths, memory pages); MIT `LICENSE` added; the roadmap emptied (no
  planned work).
- v2.1.1 cut per-run grounding cost: tiered reads, short `wrap.md` for done runs, `review.md`
  `## Resolved` table, one-line TODO intake, `TODO_ARCHIVE.md`/`ROADMAP_ARCHIVE.md` convention with
  size flags, `ROUTING.md` split into card rows and `ROUTING-NOTES.md`. Trialing (see `SKILL-IMPACT.md`).
- Commits: 04fee86 e6cd6a0 090536f

## 2026-09-30 · routing to GPT-6.1 Sol / Opus 5.5 / Sonnet 5.5; card and model-naming fixes · Opus 5.5
- `ROUTING.md` restricted to the four models in use and `medium`–`xhigh` effort; GPT-6.1 Sol runs every
  execute lane, Opus 5.5 plan and review, Sonnet 5.5 brainstorm and wrap. Plugin manifest renamed
  to `j-skills` (Codex shows `j-skills:workflow`).
- No closing card on turns that wait for an in-chat answer; the writer's model is read from the
  harness or config and recorded as the model name only.
- Commits: b057e73 a3dbc08 df073d6 6c8098a 676e751 c82ccf3

## 2026-09-30 · workflow v2.1 released · Opus 5.5
- Spec phase retired; brainstorm is a grill ending in a brief with behaviours and test seams; plan
  writes ≤8 tracer-bullet tickets with literal acceptance lines; operator tickets for live steps;
  review checks the outcome on the surface users reach. Amended after a history review of real runs.
- Commits: f2507d0
- Why: v2.02 runs showed severity bars that couldn't escalate outcome failures and no lane for live
  steps (`archive/review-v2.1-2026-09-28.md`).

## 2026-08-26 · `workflow realign` command specified, planned, executed, reviewed · Sonnet 5
- Added `references/realign.md` (new `workflow realign` command: canonical-doc drift check against
  code, per-candidate human-approved rewrite) and wired it into `SKILL.md` (seat table, command
  index) and `ROUTING.md` (model/effort/approval mapping).
- Patch cycle 1 closed 4 findings: unblocked `realign`'s own resume path (P1, clean-worktree gate
  scoped outside `.workflow/`), separated the retained-stale artifact from the fresh-run path (P2,
  `realign-stale-<date>.md`), fixed a seat-table row that both asserted read-only and granted write
  authority (P2), and plained the `TODO.md` read-only wording (P3).
- Commits: 0008a14
- Review: ship as-is (cycle 2, clean — 0 P0/P1/P2, 3 P3s deferred) @ 0008a14
- Why: give the workflow a repeatable, reviewed way to catch canonical-doc drift instead of relying
  on ad hoc memory.remember passes to notice it.
