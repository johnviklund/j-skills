Command: workflow wrap run-worktrees
Created: 2026-10-28
Base:    0066b00
Inputs:  review.md @ 0066b00
Status:  done

## Outcome
Runs can now execute in their own git worktree (`.worktrees/<slug>` on `run/<slug>`), so two runs no longer mix uncommitted edits. `run-worktree.py` has `open`, `where`, `land` and `doctor`; every phase resolves its checkout from the slug; wrap lands the branch with a conflict pre-check and a push guard. A second clone rebuilds a worktree from `origin/run/<slug>`. Proved on scratch repos through the test harness; no live parallel run.

## Shipped
- T1 `81aa880` open and recover worktrees · T2 `c601aa0` land without disturbing the primary checkout
- T3 `7473b02` recognize run checkouts, diagnose orphans · T4 `27f1f39` route phases through worktrees (incl. `SKILL.md` live-run grep fix)
- T5 `b7d369a` parallel lifecycle proved on a scratch repo
- Patch cycles 1–6: `b890db3` `d75f8cd` `c65c961` `59bfc5c` `31b78b4` `b0b55af` `b1cd333` `00a4ae6` `bbaa7a1` `59e842b` `f61de07`

## Review
Cross-vendor (writer GPT-6.1 Sol, reviewer Opus 5.5). 7 cycles; ship as-is at `4b43be1`. 17 findings, all resolved or settled (P3s stay in `review.md`). 81/81 tests at wrap.

## Final checks
Suite 81/81 · shortcut grep clean · no product docs exist (PRODUCT.md, DESIGN.md) and workflow ROADMAP.md says nothing on worktrees · no verify skill.
Retired: none — the run replaced no existing code path.

## Learnings
7 lines routed: one eval case (`strict-reviewer/missed-shared-parser-swap-changes-section-end.md`, private repo, replaces the oldest) and six into `references/phase-4-review.md` and `references/tests.md` (`43ef539`, logged in `SKILL-IMPACT.md`).

## Deferred
None to `TODO.md`. The `SKILL.md:54` grep P2 was fixed in T4 and archived.

## Receipts and leftovers
`receipts/` (execution per cycle, mutation and dry-run output) · `notes/P1-nested-worktree.md` · `prototypes/P1-nested-worktree/` · `scripts/make-fixture.sh`, `scripts/mutate.py` (one-off, reviewed).
check-run warnings: plan 128 lines (budget 120); T2 and T3 test ratio (run-level ratio waived under Deviations).
