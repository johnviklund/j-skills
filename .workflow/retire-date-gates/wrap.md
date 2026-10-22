Command: workflow wrap retire-date-gates
Created: 2026-10-22
Base:    98b87f9
Inputs:  .workflow/retire-date-gates/review.md @ 98b87f9
Status:  done

# retire-date-gates — summary

**Outcome.** `check-run.py` applies one rule set to every run that is not done, whatever its `Created:` date. The four `*_SINCE` gates and their legacy branches are gone. Done runs keep header, sha and layout checks only. Parked runs are checked like live ones, except a brief still drafting. The docs no longer say earlier plans keep their rules.

**Shipped.**
- T1 one rule set for every run not yet done → fc99027
- T2 docs state the universal rules (no start dates) → 281f4a9
- C1-T1 done runs keep the dangling-sha walk (C1-1) → fbb1fdc
- C1-T2 parked drafts can be parked incomplete (C1-2) → 2aac08b

**Review.** Ship as-is after 2 cycles; cycle 1 had two P1s, both fixed with red tests first. 50 tests pass. Net code -9, tests +59.

**Deferred.** C1-3 (agent-docs sentence reads as a condition) and C2-1 (done-run sha walk repeats the live-run checks) stay in `review.md` as P3s. Nothing went to `TODO.md`.

**Product docs.** No PRODUCT.md or DESIGN.md. ROADMAP step 2 moved to `ROADMAP_ARCHIVE.md` (in `.github/skills/workflow/`).

**Feature map.** No verify skill. **Evals.** No cases deposited.

**Receipts.** `receipts/t1-verification.md`, `t2-verification.md`, `c1-verification.md`.

**Note for the human.** cx-intelligence parked runs `decision-model-evaluation` (4 errors) and `gpt6-classifier-cutover` (2 errors) now fail the limits; unparking either means a split or a `Split declined by human:` line.

Retired: none — the run removed only its own gate code; no other product file became obsolete.
