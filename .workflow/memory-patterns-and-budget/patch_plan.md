Command: workflow review memory-patterns-and-budget · patch cycle 1
Created: 2026-10-26 · claude-opus-5-5
Base:    d0066ee
Inputs:  .workflow/memory-patterns-and-budget/review.md @ d0066ee
Status:  complete

## Execution state
Current: C1-T1 done; ready for cross-vendor review cycle 2.
C1-T1 @ fec0e26
writer: GPT-6.1 Sol · high, inherited runtime; routing recommends medium for this fix.
Baseline: patch Verify prints 0 and exits 1; no AGENTS.md or build/lint block.
Checks: local content/size checks, licence-rule desk check, check-run.py and git diff --check pass.
Checks: full patch Verify exits 0 after push and global refresh; both installed-copy diffs exit 0.
Uncommitted: none after the execution-record commit.
Pending decision: none.

## Tickets

### C1-T1 — the cost test gives a low-value operating rule a home
Delivers: B4 · Blocked by: none · Lane: logic
Fixes: C1-1 (P1)
Budget: code +0 · tests +0 · why: one sentence in memory.remember/SKILL.md
Seam: `skills/memory.remember/SKILL.md` `## The AGENTS.md cost test` (:145-152)
Change: after "leaving at most a one-line pointer in `AGENTS.md`." add one sentence, for example "A rule this test keeps out of `AGENTS.md` counts as fitting nowhere else for the admission test's item 2." Touch no other line.
Red: no test file exists for doc text; the Verify run before the edit (grep prints 0, exit 1) is the red step, recorded in the receipt.
Accept:
- [x] The cost test says a rule it keeps out of `AGENTS.md` `counts as fitting nowhere else` for admission item 2 → 1 match (B4)
- [x] `receipts/c1-t1-cost-test-desk-check.md`: the `THIRD-PARTY-NOTICES.md` licence rule under the old text → `no destination`; under the new text → `routed to a memory page` (B4)
- [x] The fix commit holds `memory.remember/SKILL.md` only; `wc -c` ≤ 27,720; SKILL-IMPACT row 13 already covers it, no new row (B6)
- [x] After the push, `npx skills update -g` has run and both installed copies match the repo → `diff -q` exit 0
Verify: `R=skills/memory.remember/SKILL.md; grep -c 'counts as fitting nowhere else' $R; test $(wc -c < $R) -le 27720 && test -f .workflow/memory-patterns-and-budget/receipts/c1-t1-cost-test-desk-check.md && diff -q ~/.agents/skills/memory.remember/SKILL.md $R && diff -q ~/.agents/skills/memory.compact/SKILL.md skills/memory.compact/SKILL.md` (pre: grep 0; receipt missing; installed copies differ; exit 1)
Skills: skills/agent-docs/SKILL.md · skills/plain/SKILL.md
Status: done @ fec0e26
Writer: GPT-6.1 Sol
