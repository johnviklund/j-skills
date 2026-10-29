Command: workflow plan next-step
Created: 2026-10-29 · Opus 5.5
Base:    19533a5
Inputs:  .workflow/next-step/brainstorm.md @ 62e8c26
Status:  drafting

Docs read: none in scope (the repo has no PRODUCT.md or DESIGN.md)
Size: code 812 · tests 503 · ratio 0.62 · largest touched check-run.py 812 · over 1,000: none (new: next-step.py, test_next_step.py; skill `*.md` count as neither)
Decisions: pending round 1 (fix rows for mechanical and operator lanes · fix-ticket severity · checkup card lines)

## Execution state
<filled by execute>

## Findings
| # | What is true | What it changes |
|---|---|---|
| F1 | The skill lives in `.github/skills/workflow/`; `skills/workflow` is a symlink to it | Tickets name `.github/skills/workflow/…`; the brief's path works through the link |
| F2 | `run-worktree.py:10-11` already loads `check-run.py` with `importlib` | next-step.py copies those two lines (D1); reuse hit |
| F3 | check-run.py has `Doc` (:100), `parse_tickets` (:255), `field` (:273), `SHA`/`DASH`/`RECEIPTS` (:64-72), `git_out` (:673). It has no review parser: `check_review` parses findings inline (:540-583) | next-step reuses them; T4 extracts `review_findings(doc)` and `check_review` calls it, the 82 existing tests prove no change |
| F4 | No "code changed since X" helper; `growth()` (:413) nets lines, so a net-zero edit reads as unchanged | next-step filters `git diff --name-only <Base>..HEAD` by `RECEIPTS` (the receipt-rule diff) |
| F5 | Fix tickets give severity two ways: `Fixes: C1-1 (P1)` (lean-skill-hubs, memory-patterns-and-budget, run-worktrees) and `Delivers: C1-1, B5` (retire-date-gates, run-ratio-and-retire). Finding ids are positions in `review.md`, and settled sections fold into `## Resolved` | Decision 2 |
| F6 | ROUTING has fix rows for P0, logic and contract only; real fix tickets also use mechanical (lean-skill-hubs C1-T2, run-worktrees C6-T1) and operator (cx `c1-t3-handoff.md`) | Decision 1 |
| F7 | Nothing records a handoff's path in its ticket (D7's premise). Names vary: `t3-operator-handoff.md`, `t5-attempt2-operator-handoff.md`, `c1-t3-handoff.md`, `t7-friction-handoff.md` (cx-intelligence) | The blocker lists every `receipts/<id>-*handoff*.md` in name order; no new field |
| F8 | An awaiting-human ticket's receipt path is in its Verify, `receipt: receipts/<file>` (check-run :327); a present receipt resumes the ticket (phase-3-execute :61-62) | next-step routes that ticket to execute |
| F9 | ROUTING cells hold prose: plan effort "high; xhigh hardest cases", contract context "standard; large if …", operator seat "… (Heavy executor if …)", approvals as sentences | D2 format: effort ∈ medium·high·xhigh, context ∈ standard·large, approval ∈ auto·human, one seat per row; the prose moves to a Notes column |
| F10 | No ticket field marks a UI ticket | The UI row becomes a note; `approval` reports the lane's row, and execute still stops before a UI commit by its own rule |
| F11 | Fallback effort disagrees: ROUTING's reviewer chain says `Sonnet 5.5 · xhigh`; checkup report.md:72 says use the phase row's effort | A chain item is `Vendor · Model` (phase effort) or `Vendor · Model · effort`; with 3a checkup's sentence goes |
| F12 | Seat-table efforts repeat the phase table ("high (review: xhigh)", "xhigh (P0 fixes: high)") | The seat table keeps vendor, model, trial and chain; effort lives only in the phase table |
| F13 | checkup report.md:70-80 maps commands to phase rows and copies Model and Fallback by hand: TODO C1-1, wrong four times | Decision 3 |
| F14 | The card's command "carries the CLI's own skill prefix" (SKILL.md:19-20) | `--prefix` adds it to the card's command; JSON `command` stays bare (D6) |
| F15 | ROUTING Modes: wrap follows review in the same session | Wrap's card has `reset: false`; every other card `true` |
| F16 | SKILL.md's states also include drafting artifacts (resume that phase), parked runs (listed by `status`) and done runs | T4 covers them |
| F17 | SKILL.md is 11,191 B (budget ~10 KB, already over); ROUTING.md is 5,407 B (budget 5.5 KB) | T5 drops the card template from SKILL.md; T1 keeps ROUTING.md ≤ 5,500 B |
| F18 | `test_check_run.py`'s harness (:66-101) is check-run specific, and tests.md forbids a test importing a test | test_next_step.py has its own small temp-repo harness and an inline fixture routing table, so a ROUTING edit never breaks B1-B6 tests; one test parses the real file |
| F19 | Escalations (review cycle bound, wrap contradictions) wait for a chat answer, so they already end on the Decisions list with no card (SKILL.md:120-121) | Only the cycle-bound state shows in files: open fix-now findings and no current-cycle patch plan → a blocker (T4) |
