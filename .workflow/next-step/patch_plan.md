Command: workflow review next-step · patch cycle 2
Created: 2026-10-29 · Claude Opus 5.5
Base:    688e443
Inputs:  .workflow/next-step/review.md @ 0dc90ce
Status:  complete

Cycle 3 approved by human (1a). C2-T2 runs first: it pins check-run's open-finding note before C2-T1 changes `review_findings`, which that note reads. C2-T1 is a behavioural fix in two commits: the reproducing test, seen failing and committed alone (`Red: <sha>`), then the fix, which leaves every test file untouched. C2-T2 is test-only.

## Execution state
Current: C2-T1 next · writer: GPT-6.1 Sol · baseline: workflow 107, checkup 8 passed
C2-T2 @ 5c5e306 · final workflow 108, checkup 8 passed · receipts/c2-t2-verification.md

## Tickets

### C2-T1 — The blocker names the open finding after a fold
Delivers: B4 · Blocked by: C2-T2 · Lane: logic
Fixes: C2-1 (P1)
Budget: code +4 · tests +14
Seam: `next-step.py <slug> --json` on a fixture `review.md` with a `## Resolved` table; `review_findings` (check-run.py:532-548)
Change: `review_findings` collects the ids in the first cell of each `## Resolved` row (`C<n>-<m>`) and numbers each cycle's `###` sections with that cycle's ids not in the set, in order. Sites: `grep -n 'review_findings' .github/skills/workflow/scripts/*.py` gives check-run.py:569, whose `check_review` labels findings by title and never reads the id, and next-step.py:167-169, the only id reader.
Accept:
- [ ] Resolved rows C1-1, C2-1; one open `fix now` finding in each of cycles 2 and 3 → blocker `["C2-2", "C3-1"]`, Why `Patch cycle 3 · fix C2-2, C3-1` (B4)
- [ ] `## Resolved` row C2-2 only; `## Cycle 2 findings` holds two open `fix now` findings → blocker findings `["C2-1", "C2-3"]` (B4)
- [ ] the run-worktrees review at 68cbf30, read in a throwaway worktree → `blocker.action` is `Resolve C2-2, C3-1 before continuing.`; test_check_run.py passes unchanged (B4)
Verify: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests -p test_next_step.py && git worktree add -q --detach /tmp/c2-t1-rw 68cbf30 && python3 .github/skills/workflow/scripts/next-step.py run-worktrees --repo /tmp/c2-t1-rw --json | grep -c 'Resolve C2-2, C3-1'; git worktree remove --force /tmp/c2-t1-rw` (pre: 24 OK · grep 0, the card says `Resolve C2-1, C3-1`)
Skills: none
Status: todo

### C2-T2 — Wrap's open-finding note in check-run has a failing test
Delivers: B4 · Blocked by: none · Lane: logic
Fixes: C2-2 (P1)
Budget: code +0 · tests +12
Seam: test_check_run.py `ReviewTests` through `check()` and `review()`; check-run.py unchanged
Change: one case. A live run whose `review.md` holds a cycle 1 `### P1 — Open` with `- Disposition: fix now` gives the open note while `- Resolved: —`, and the closed note once `- Resolved: @ {base}`.
Accept:
- [x] `Resolved: —` → check-run prints ``1 open `fix now` finding(s)``; `Resolved: @ {base}` → it prints ``no open `fix now` finding`` and no ``open `fix now` finding(s)`` (B4)
- [x] the `if open_finding(f):` line in `check_review`, changed to `if not open_finding(f):` and to `if False:`, each alone in a throwaway copy, turns test_check_run.py red, 2 of 2; the commit changes no line of check-run.py (B4)
Verify: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests -p test_check_run.py` (pre: 50 OK; both mutations survive)
Skills: none
Status: done @ 5c5e306
Writer: GPT-6.1 Sol
