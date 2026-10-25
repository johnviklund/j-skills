Command: workflow review checkup-next-actions
Created: 2026-10-25 · Claude Opus 5.5
Base:    659d054
Inputs:  .workflow/checkup-next-actions/plan.md @ ce84693
Status:  complete

Scope: the whole run, `080ecdf..659d054`. The plan's Base moved with each replan, and T1 @ bc2a0e2 sits before it.

## Coverage
- [x] T1: acceptance 6/6, greps rerun and passing (SKILL.md 23,217 B, under 23,646)
- [x] T3: acceptance 3/3 passing
- [x] T4: acceptance 4/4 passing
- [x] T5: acceptance 2/2, per receipts/t5-verification.md and the dry run in t2-fixture-verification-2.md
- [x] T6: acceptance 4/4 passing
- [ ] T2: clauses 1, 2 and 4 pass; clause 3 fails (C1-1); clause 5 never ran (C1-2); clause 6 holds for the one session run
- [ ] B1, B2, B5, B6, B7, B8 delivered (B5 in text only, no live candidate, F6) · B3 and B4 not delivered · Outcome observed on the fixture report (receipts/t2-fixture-checkup-2.md) by hand, no verify skill · out of scope untouched: ROUTING.md, the checks, the allow-list and cx-intelligence have no diff
- [x] .workflow/ dependency check: no hit outside `.workflow/`
Size: +0 code · +0 tests · ratio n/a · net +0 (docs +101 / −30; make-fixture.sh +40 lives in the run folder) · over 1,000: none
Reachability: report.md ← checkup SKILL.md:53 · make-fixture.sh ← T2 handoff · guards shown failing: T6 and T4 greps both drop to 0 when "drop the vendor" and "never a seat name" are inverted in a throwaway worktree
Independence: cross-vendor (writer GPT-6.1 Sol, OpenAI · reviewer Claude Opus 5.5, Anthropic)
Threats: shell execution and file writes in make-fixture.sh, a local script. Only the agent runs it, on synthetic text. It writes only `/tmp/checkup-fixture` and deletes that folder only when it is a real folder holding `.fixture-marker` (make-fixture.sh:5-9), so it fails closed. It logs nothing secret. Worst case: it deletes a fixture another local user built. The paid T2 sessions allowed Bash, so "Write disallowed" did not make them read-only. The receipts compare fixture HEAD and status before and after, and that check caught nothing.
Escape hatches: none in the diff. Tests: workflow scripts 49/49 pass (`python3 -m unittest`). check-run: 0 errors, 2 warnings, both about plan budget.

## Cycle 1 findings
### P1 — C1-1 The card's model lines are wrong in the final report (B3)
- Evidence: T2 clause 3 · receipts/t2-fixture-checkup-2.md: `Model: claude-opus-5.5 · medium · standard`, `Fallback: claude-opus-5.5 · medium`. The required lines are `Sonnet 5.5 · medium` and `GPT-6 Sol · medium`. The session made 5 tool calls and never read ROUTING.md's tables, and it named the wrong row ("brainstorm", not TODO intake).
- Design flaw: report.md:70-75 asks the agent to look values up in two tables of another file while it writes the report. Four attempts failed this line four different ways: the cx run gave no card, the retry gave seat names, fixture 1 gave a vendor and the wrong fallback effort, fixture 2 gave the running model's id. Each text fix (T4, T6) passed its grep and the next run failed a new way. The greps prove that the words exist, not that the agent follows them.
- Remedy: a small script prints the `Model:` and `Fallback:` lines for a command from ROUTING.md, and the card copies its output. This is the pattern the uncommitted `config-scan.py` uses. It needs its own tests, so it is run-sized.
- Disposition: defer, TODO.md at wrap. Approved by human: 2026-10-25 (replan 3, 3a: "a failure goes to wrap")
- Resolved: —

### P1 — C1-2 No proof that a copied prompt works in a fresh session (B4)
- Evidence: T2 clause 5 · receipts/t2-fresh-session.md does not exist. The session waited on clause 3. The prompt it would run is in the fixture-2 receipt.
- Disposition: defer, wrap records the proof gap. Approved by human: 2026-10-25 (replan 3, 3a)
- Resolved: —

### P3 — C1-3 §Action cards states the grouping rule twice
- Evidence: report.md:34-36 keeps the old "earns a row" and "one row" text, which the 2026-10-21 trial still judges. report.md:45 repeats the rule for cards. Wrap can cut line 45's first sentence and keep its example.
- Disposition: defer (P3)
- Resolved: —

### P3 — C1-4 The fixture writes `Base: none`, which check-run flags
- Evidence: make-fixture.sh:22-23. The final report spent Question 2 of 5 on it. This is fixture noise, not a checkup defect.
- Disposition: defer (P3)
- Resolved: —

### P3 — C1-5 The final report states a consequence before the question is answered
- Evidence: in receipts/t2-fixture-checkup-2.md the Docs line says "so Claude Code may not see the verify skill. See Question 1." This breaks report.md:17-18. It is the same class as C1-1: the rule text exists and the run did not follow it.
- Disposition: defer (P3)
- Resolved: —

### P3 — C1-6 Four trialing SKILL-IMPACT rows for one run
- Evidence: SKILL-IMPACT.md:13-16. Their judges name the cx retry and the fixture proof, and both have ended. Wrap settles them as one row.
- Disposition: defer (P3)
- Resolved: —

## Pre-existing / environmental
- P2: workflow SKILL.md:54 finds live runs with `grep 'Status: \(drafting\|complete\)'`. Six briefs, this one included, write `Status:  complete` with two spaces, so `workflow status` misses them. check-run splits on whitespace and is unaffected. Defer, TODO.md at wrap.
- The working tree holds uncommitted checkup work from another session: config-scan.py, its tests, SKILL.md:205-211, a SKILL-IMPACT row and THIRD-PARTY-NOTICES.md. It is not part of this run and was not reviewed.

## Cycle 1 verdict
Ship to wrap. The text changes do what their tickets say, and the doc-only diff is small and reachable. The run's Outcome holds except for the model lines (C1-1), and the fresh-session proof never ran (C1-2). The human approved both P1 deferrals in replan 3. Wrap records the proof gap, adds C1-1's script and the live-run grep to TODO.md, and settles the trial rows.
