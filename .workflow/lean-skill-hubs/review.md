Command: workflow review lean-skill-hubs
Created: 2026-10-28
Base:    f80148f
Inputs:  .workflow/lean-skill-hubs/plan.md @ 2bc4427 · .workflow/lean-skill-hubs/patch_plan.md @ c4aa5a7
Status:  complete

## Coverage
- [x] T1 — 2/2: `test_sentence_ledger` 3 OK; whole-file mutation sweep 12 mutations, all killed after C1-T1 (M12 was C1-1)
- [x] T2 — 2/2: 19,132 bytes ≤ 19,200 · `## Repeats escalate to enforcement` 1 · ledger moved 42 · duplicate 22 · unaccounted 0 · three refs linked
- [x] T3 — 2/2: 14,422 ≤ 14,500 · `## Memory Layers` is a 2-line pointer naming `memory.remember` · ledger duplicate 22 · unaccounted 0
- [x] T4 — 2/2: 11,499 ≤ 11,500 · `secret-scan.md` linked · ledger moved 5 · duplicate 7 · unaccounted 0 · workflow suite 81 OK
- [x] T5 — 3/3: 6,058 ≤ 8,000 · six refs linked · ledger moved 115 · duplicate 2 · unaccounted 0 · description 591 chars, all 7 quoted triggers · checkup suite 8 OK
- [x] T6 — 3/3: 11,984 ≤ 12,000 · frontmatter identical to `ed2c63b` · `<skill>/video.md|in video.md` 0 hits · build-video.py:158 names `references/video.md` · ledger unaccounted 0
- [x] T7 — 2/2: 2,914 ≤ 3,500 · ledger moved 138 · unaccounted 0 · `SKILL-IMPACT.md` 5 rows dated 2026-10-28, new row names six skills, `trialing`
- [x] T8 — 2/2: `diff -rq -x __pycache__` for the seven skills against `~/.agents/skills/` re-run at f80148f → all identical; agent-docs `git diff --quiet ed2c63b` → 0
- [x] C1-T1 — 2/2: new case at `test_sentence_ledger.py:73-76` passes; in a throwaway worktree `lines[:12]`→`lines`, `[:12]`→`[:13]` and `> 100`→`> 101` each turn the suite red · `sentence-ledger.py` untouched in `c4aa5a7..HEAD`
- [x] C1-T2 — 2/2: the five phrases 0 hits each · ledgers for all six skills unaccounted 0, exit 0 · hub 11,499 bytes · each reworded line has its `notes/dups-*.txt` row
- [x] C1-2 class swept: every `above/below/following/step N/this file` pointer in the 14 new or moved reference files and the changed `SKILL.md` files, plus every moved heading name, read in place. All resolve. `video.md:103` "`SKILL.md` step 3" names the procedure step, which links to `pictures.md`. `promote-to-skill.md:3` "during step 1" matches `memory.remember/SKILL.md:163`
- [x] Dup rows read one by one (55 rows across five `notes/dups-*.txt`: the 5 C1-T2 added this cycle, the rest in cycle 1): each removed rule's meaning survives at its kept path. The workflow invariants now held only by `ROUTING.md` are D2's approved trim
- [x] B1–B7 delivered (B1 caps as raised by decisions 1a and 4 in plan F3, F5) · Outcome observed on `wc -c` and installed copies, manual, no verify skill · out of scope untouched (design, evals, plain, retro, agent-docs: no diff)
- [x] .workflow/ dependency check: the only hit is `workflow/scripts/tests/test_run_worktree.py`, pre-existing
- [x] Escape-hatch scan 0 · no new dependencies · `check-run.py --all` ERROR 0
Size: +2 code · +0 tests · ratio 0 · net +0 · over 1,000: none (skill `*.md` count as neither: +597 −601; run script `scripts/` 83 + tests 88, inside `.workflow/`)
Reachability: new refs each linked from their `SKILL.md` (ledger link check, all six skills) · `sentence-ledger.py` run by its tests and by T2–T7 verify · guards shown failing: M1–M12 of the sweep
Independence: cross-vendor (writer GPT-6.1 Sol, OpenAI · reviewer Opus 5.5, Anthropic)
Threats: none — the brief and the diff add no boundary; `npx skills update -g` was the approved operator step

## Resolved
| Finding | Sev | Title | Disposition | Resolved |
|---|---|---|---|---|
| C1-1 | P1 | The ledger's 12-line contents window is untested | fix now | @ 2f648a8 (cycle 2) |
| C1-2 | P3 | Five stale pointers left by the moves | fix now | @ be06046 (cycle 2) |

## Cycle 2 findings
None. Scope: fix diff `c4aa5a7..f80148f` plus the C1-1 and C1-2 classes. The only code outside
`.workflow/` the run changed is `build-video.py` (+2 −2, cycle 1). Workflow 81 OK · checkup 8 OK ·
ledger 3 OK at f80148f.

## Pre-existing / environmental
- none open; the `workflow/SKILL.md:184` omission noted in cycle 1 was fixed by C1-T2 (d)

## Cycle 2 verdict
Ship as-is. Both cycle-1 findings are fixed and stamped. C1-1's mutation now fails, and so do its
two boundary neighbours. No other pointer of C1-2's class is stale. Suites, ledgers, byte caps and
installed copies all match.
