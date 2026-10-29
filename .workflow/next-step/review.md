Command: workflow review next-step
Created: 2026-10-29 · Claude Opus 5.5
Base:    1aa0b47
Inputs:  .workflow/next-step/plan.md @ 19533a5
Status:  complete

Scope: the five ticket commits 904f083, 70fefa2, 17c8020, 53d959c, a354025. The outside commits a8d8097, 588bf2d and 94fd7d7 are not this run's work.

## Coverage
- [x] T1 — acceptance 5/5 tested and passing; ROUTING.md 5,453 B ≤ 5,500
- [ ] T2 — 3/3 pass, but the receipt line fails on the backticked form (C1-2)
- [x] T3 — 3/3 tested and passing
- [ ] T4 — 5/5 pass, but the tests encode C1-1 (test_next_step.py:197) and cover parked with no plan only (C1-5)
- [x] T5 — 3/3: `--key` test passes; greps 1 · 1 · 2 · 0 · 1; SKILL.md 10,915 B < 11,191; no `**▶ Next:` left
- [ ] B1, B2, B5, B6, B7, B8 delivered · B3 broken by C1-2 · B4 by C1-1 · Outcome observed via `python3 skills/workflow/scripts/next-step.py next-step --json` on this run (phase `review`, Opus 5.5 · xhigh · large), manual, no verify skill · out of scope untouched: the ticket commits add no unattended mode, `decisions.md`, conductor, harness IDs or `.claude-plugin` change (the root ROADMAP.md hits are outside commit a8d8097)
- [x] .workflow/ dependency check: the hits are run-folder paths next-step.py builds (:139-167), which is its job (Outcome, D1), as run-worktree.py:66 does; the test hit is a fixture path
Size: +259 code · +310 tests · ratio 1.20 · net +559 · over 1,000: none (check-run.py 830 lines)
Reachability: next-step.py ← SKILL.md:125, worktrees.md:27, checkup report.md:70 · `ticket_fixes` ← check-run.py:298, next-step.py:126 · `review_findings` ← check-run.py:562, next-step.py:168 · guards shown failing: 67 of 78 mutations killed; 3 equivalent; 8 survive (C1-3)
Independence: cross-vendor (writer GPT-6.1 Sol, OpenAI · reviewer Claude Opus 5.5, Anthropic)
Threats: run-folder Markdown and ROUTING.md, written by anyone who can commit to the repo or push a `run/*` branch. The script only reads files under `.workflow/<slug>/` and runs git read commands with list arguments; review `Base` passes `git_has` before `git diff` (next-step.py:174). It writes and logs nothing beyond stdout and stderr. Ticket titles go into `blocker.action` and the card as data; `command` is always `workflow <phase> <slug>` with the slug checked at next-step.py:217, a guard no test covers (C1-3). Fails open: a failing `git diff` reads as "unchanged" and routes to wrap, only after `git_has` passed. Worst case: a misleading card, not a command.
Escape hatches: 1 hit, next-step.py:144 `lambda doc: any(`, a false positive of the `: any` pattern. Tests: workflow 99 OK, checkup 8 OK, exit 0. Assertions in tests the run did not create: test_check_run.py 74 → 77, test_run_worktree.py 148 → 148. check-run: 0 errors.

## Cycle 1 findings
### P1 — An open fix-now finding from an earlier cycle routes to wrap
- Evidence: SKILL.md state table ("`review.md` with no open finding … → wrap"); phase-4-review.md: "a finding still open keeps its section", "stays open until a later cycle stamps it". next-step.py:169-172 reads only the latest cycle; check-run.py:569-582 (`check_review`) reads every cycle. Input: cycle 1 `### P1`, `fix now`, `Resolved: —`; empty cycle 2 findings and verdict; no later commit → `phase: wrap`, "The review has no open finding", `blocker: null`, while check-run notes "1 open `fix now` finding". test_next_step.py:197 asserts that wrap. This is the cycle-bound escalation state, so F19's blocker cannot fire for a reopened finding.
- Waste: next-step.py:170-172 is a second copy of check-run's open-fix test (`value.startswith("fix now")` plus a Resolved sha). The copies already disagree.
- Remedy: one predicate in check-run.py (for example `review_findings` marks each finding `open`) that `check_review` and next-step both call, over every cycle. The third case at test_next_step.py:197 then expects a blocker naming `C1-1`.
- Disposition: fix now
- Resolved: —

### P1 — A receipt path in backticks never unblocks its operator ticket
- Evidence: B3 ("Verify receipt present → phase execute, blocker null"). next-step.py:107 needs `receipts/` right after `receipt:`. check-run.py:337 accepts any `receipt:`, and the repo's own plans use both forms: `.workflow/checkup-next-actions/plan.md:101` has ``Verify: receipt: `receipts/t2-fixture-checkup-2.md` — …``. Repro: that Verify line with the file present → still `blocker` T2, so the card keeps asking the human for a receipt that exists.
- Remedy: allow an optional backtick before the path, plus one test case per real form (plain and backticked).
- Disposition: fix now
- Resolved: —

### P1 — Eight guards in the new next-step.py have no failing test
- Evidence: whole-file sweep, 78 mutations in a throwaway worktree, test_next_step.py and test_check_run.py; 67 killed, 3 equivalent, 8 survived:
  `reset yes/no` :89 (the wrap card prints `Reset: yes`, B6) · `blocker picks awaiting` :112 (`next(unfinished)` names a todo ticket blocked behind the awaiting one, B3) · `no ready raises` :113 (a fully blocked plan crashes with a traceback, B8) · `handoff glob id` :115 (every ticket's `*handoff*.md` lands in `blocker.action`) · `blocker why` :123 · `cycle from id` :131 (C2-T1 fixing C1-1 says "Patch cycle 1") · `slug check` :217 (the trust-boundary guard; `../x` passes) · `not a repo` :220.
- Remedy: test-only ticket, one assertion or case per guard in test_next_step.py.
- Disposition: fix now
- Resolved: —

### P2 — A P0 fix on the operator lane reports `approval: auto`
- Evidence: phase-4-review.md:164, "The lane decides seat and approval". next-step.py:129 takes the whole `fix:P0` row, so `Fixes: C1-1 (P0)` with `Lane: operator` gives Heavy executor and `approval: auto`, where `fix:operator` says `human`. B5 covers only a P0 logic fix. Execute's own operator rule still stops for the human, but a JSON consumer (D5) reads `auto` for a live write.
- Remedy: P0 keeps `fix:P0`'s seat and effort and takes approval from `fix:<lane>`; one test. Small.
- Disposition: fix now
- Resolved: —

### P2 — A run parked after planning resumes at `workflow plan`
- Evidence: phase-0-brainstorm.md:219-220, "Unpark with `workflow <phase> <slug>`", the phase it was parked at. next-step.py:194 prints `workflow plan <slug>` for every parked run. Repro: parked brief, plan with T1 done and T2 todo → `parked`, `workflow plan x`. The `workflow status` line copies it. T4's line covered only "brief parked, nothing else".
- Remedy: work out the step as if the brief were complete, then set `phase: parked` and keep that command. Small.
- Disposition: fix now
- Resolved: —

### P3 — Three minor items
- The patch-cycle card names only the first ticket's findings (next-step.py:131); phase-4-review.md:171 shows `Patch cycle 1 · fix C1-1, C1-2`.
- Redundant code, shown by equivalent mutants: next-step.py:100's `unfinished` filter (the loop picks only `todo` or `awaiting-human`) and :142's complete-only guard; the :144 lambda repeats :99-100's done test.
- A seat with no fallback cannot be written: `—` does not parse in Fallback chain (next-step.py:58), though `model_lines` prints `none` for an empty chain.
- Disposition: defer — stays in review.md
- Resolved: —

## Pre-existing / environmental
- The installed workflow skill this session loaded still carries the hand-written card template and an older next-step.py; it catches up only after `npx skills update -g` (AGENTS.md).

## Cycle 1 verdict
Fix before wrap: 3 P1 (C1-1, C1-2, C1-3) and 2 small P2 (C1-4, C1-5), one ticket each in `patch_plan.md`; the P3 bundle (C1-6) stays here. The design holds: one script, keyed tables, shared parsers, and the card and JSON agree on every state the tests cover. The defects sit where the script reads review and plan text more narrowly than check-run and the repo's own runs do.
