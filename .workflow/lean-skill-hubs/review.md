Command: workflow review lean-skill-hubs
Created: 2026-10-28
Base:    c4aa5a7
Inputs:  .workflow/lean-skill-hubs/plan.md @ 2bc4427
Status:  complete

## Coverage
- [x] T1 — 2/2: `test_sentence_ledger` 3 OK; whole-file mutation sweep 12 mutations, 11 killed (C1-1)
- [x] T2 — 2/2: 19,132 bytes ≤ 19,200 · `## Repeats escalate to enforcement` 1 · ledger moved 44 · duplicate 20 · unaccounted 0 · three refs linked
- [x] T3 — 2/2: 14,422 ≤ 14,500 · `## Memory Layers` is a 2-line pointer naming `memory.remember` · ledger duplicate 22 · unaccounted 0
- [x] T4 — 2/2: 11,494 ≤ 11,500 · `secret-scan.md` linked · ledger moved 6 · duplicate 5 · unaccounted 0 · workflow suite 81 OK
- [x] T5 — 3/3: 6,044 ≤ 8,000 · six refs linked · ledger moved 115 · duplicate 1 · unaccounted 0 · description 591 chars, all 7 quoted triggers · checkup suite 8 OK
- [x] T6 — 3/3: 11,984 ≤ 12,000 · frontmatter identical to `ed2c63b` · `<skill>/video.md|in video.md` 0 hits · build-video.py:158 names `references/video.md` · ledger unaccounted 0
- [x] T7 — 2/2: 2,914 ≤ 3,500 · ledger moved 138 · unaccounted 0 · `SKILL-IMPACT.md` 5 rows dated 2026-10-28, new row names six skills, `trialing`
- [x] T8 — 2/2: re-ran `diff -rq -x __pycache__` for the seven skills against `~/.agents/skills/` → all identical; agent-docs `git diff --quiet ed2c63b` → 0
- [x] Dup rows read one by one (48 rows across five `notes/dups-*.txt`): each removed rule's meaning survives at its kept path. The workflow invariants now held only by `ROUTING.md` are D2's approved trim
- [x] B1–B7 delivered (B1 caps as raised by decisions 1a and 4 in plan F3, F5) · Outcome observed on `wc -c` and installed copies, manual, no verify skill · out of scope untouched (design, evals, plain, retro, agent-docs: no diff)
- [x] .workflow/ dependency check: the only hits are the workflow skill's own tests, pre-existing
- [x] Escape-hatch scan 0 · no new dependencies · `check-run.py --all` ERROR 0
Size: +2 code · +0 tests · ratio 0 · net +0 · over 1,000: none (skill `*.md` count as neither: +595 −597; run script `scripts/` 83 + tests 84, inside `.workflow/`)
Reachability: new refs each linked from their `SKILL.md` (ledger link check, all six skills) · `sentence-ledger.py` run by its tests and by T2–T7 verify · guards shown failing: M1–M11 of the sweep
Independence: cross-vendor (writer GPT-6.1 Sol, OpenAI · reviewer Opus 5.5, Anthropic)
Threats: none — the brief and the diff add no boundary; `npx skills update -g` was the approved operator step

## Cycle 1 findings

### P1 — The ledger's 12-line contents window is untested
- Evidence: B3 "one over ~100 lines opens with a contents list" · `sentence-ledger.py:73` `lines[:12]` → `lines` keeps `test_sentence_ledger` green (M12 of the sweep, throwaway copy in `/tmp`). A 101-line reference whose `Contents` sits on line 50 passes
- Disposition: fix now
- Resolved: —

### P3 — Five stale pointers left by the moves
- Evidence: (a) `memory.remember/references/promote-to-skill.md:5` "see the naming-collision rule in step 2": the rule is now in the same file (line 14) · (b) `memory.remember/references/limits.md:21` "The repeat rule above": no repeat rule above it in `limits.md`; it is `SKILL.md` *Repeats escalate to enforcement* · (c) `checkup/SKILL.md:56` "commands like the following": the commands moved to `references/` · (d) `workflow/SKILL.md:184` "`status` and `next` need only this file and `ROUTING.md`": status's line format moved to `references/worktrees.md` · (e) `workflow/references/phase-3-execute.md:29` moved bullet repeats step 4 "**Commit** the ticket" (`:52`) and the hub's "kept forever", sitting under the readiness checks
- Disposition: fix now — the human's standing preference: small fixes now, not deferred (memory `do-not-defer-to-todo`)
- Resolved: —

## Pre-existing / environmental
- `workflow/SKILL.md:184` already left out `references/worktrees.md` before this run, though the hub's *Checkout* line requires it for status

## Cycle 1 verdict
Fix two tickets, then re-review: 1 P1 (missing assertion in the run's own script) and 1 P3 bundle of five one-line text fixes. Every skill change is otherwise sound: every removed sentence is accounted for, all caps met, suites and installed copies match.
