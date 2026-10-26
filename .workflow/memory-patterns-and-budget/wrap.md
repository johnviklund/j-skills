Command: workflow wrap memory-patterns-and-budget
Created: 2026-10-26
Base:    e4df252
Inputs:  review.md @ e4df252
Status:  done

## Summary
`memory.compact` now reads the last ~10 done runs' `learnings.md` and proposes a page when two runs share a cause and a fix. `memory.remember` asks whether removing a new `AGENTS.md` rule would cause a mistake; a no routes it to a memory page or skill reference, and an operating rule it rejects still gets a memory home. Doc-only run: checked by greps and desk checks on the real `learnings.md` files, not live runs.

## What shipped
- T1 → 94f353b: `memory.compact` proposes pages for repeated unpaged lessons.
- T2 → 43588b3: `memory.remember` AGENTS.md cost test and line-cap rule.
- C1-T1 → fec0e26: cost-rejected operating rules get a memory home (review C1-1, P1).
- Trial rows for both skills in `SKILL-IMPACT.md`; judge is the next 3 runs.

## Review
Ship as-is, 2 cycles, 0 open. Cycle 1: one P1 (fixed) and four P3s. Cycle 2: one more P3 (C2-1). Six P3s (C1-2..C1-5, C2-1, one unlisted) stay in `review.md`; no P2s, so nothing went to `TODO.md`.

## Learnings routed
- Desk-check and Verify-grep lessons → `.github/skills/workflow/MEMORY.md` ("A new guard needs one test per key").
- Missed P1 → exam case `missed-cost-test-leaves-operating-rule-homeless.md` in `j-skills-evals` (set stays at 10; oldest missed case dropped).

## Docs and cleanup
- Product docs: none exist in this repo. `TODO.md`: no impacts. Feature map: no verify skill.
Retired: none — doc-only run, nothing obsolete
- Receipts: `receipts/` (t1-compact-dry-run, t2-remember-desk-check, c1-t1-cost-test-desk-check). No stray files at the top level.
- Installed copies of both skills match the repo.
