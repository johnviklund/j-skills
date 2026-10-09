Command: workflow plan run-sizing
Created: 2026-10-10
Base:    1dfb679
Inputs:  .workflow/run-sizing/brainstorm.md @ 0ba7236
Status: done

Docs read: none in scope (no PRODUCT.md, no DESIGN.md)
Size: code 675 · tests 236 · ratio 0.35 · largest touched check-run.py 675 · over 1,000: none
Decisions: 1a (ticket list approved as drafted)

## Findings
| # | What is true | What it changes |
|---|---|---|
| F1 | Today's `check-run.py` caps a ticket at 4 acceptance lines (`ACCEPT_MAX`, check-run.py:49) and checks this plan. B1–B7 need 7 lines. | The check-run work is two tickets, T1 and T2, although T2's code Budget is under 40. Nothing else forces a split. |
| F2 | `field(t, "Budget")` (check-run.py:186) returns `code +20 · tests +30`; the lookahead stops only at `· Word:`. | Reuse: T1 reads the code Budget with `code\s*\+(\d+)` on that value. No new parser. |
| F3 | `Doc.slop_gated()` (check-run.py:131) compares the header's `Created:` date with `SLOP_SINCE`. A re-review keeps `Created:`. | Reuse: T2 gives it a date argument for the new `SIZING_SINCE = "2026-10-10"` instead of copying it. |
| F4 | `check_review` already builds the sorted cycle list (check-run.py:428). | Reuse: T2 checks every cycle ≥ 3 in that list for its `Cycle N approved by human:` line. |
| F5 | Notes go through `rep.note` and do not count in `0 errors · 0 warnings`; the existing clean tests assert that string. | B3's note keeps the 24 existing tests passing. The 2-ticket fixture stays under the 4-ticket warn. |
| F6 | No median helper exists in the repo (searched `median`). | T1 uses the stdlib `statistics.median`, printed with `:g` so 30.0 prints `30`. |
| F7 | README.md:14 says review runs "at most three patch cycles"; README.md:11 and :41 say "at most eight small tickets". The brief names only MAINTAINING.md. | T2 updates the review row to two cycles. T3 updates both plan rows to "usually 2–5 tickets, at most eight". |
| F8 | Wrap step 8 (wrap.md:136) writes the WORKLOG entry before step 9a strips `## Execution state` from plan.md. | Step 8 can count the `Session N:` lines there for the `Run:` line's `sessions`. |
| F9 | ROUTING.md:58–59 holds the per-ticket stop; ROUTING.md:5 says only the human edits it. ROUTING-NOTES.md:11 also lists `Run:` fields and is human-only. | D3 approves the ROUTING.md edit. ROUTING-NOTES.md stays untouched; see TODO impacts. |
| F10 | `ticket per session` wraps across phase-3-execute.md:64–65, so `grep 'one ticket per session'` finds 0 today. | T3 checks `ticket per session` (pre: 1) for the old rule's removal. |
| F11 | The check-run docstring (line 10) says `1-4 acceptance lines`; the `ACCEPT_MAX` comment cites `*Small*`. | T1 updates both to 1-6 and *Right-sized*. |

## Tickets

### T1 — check-run sizes plans: median code Budget, 6 acceptance lines
Delivers: B1, B2, B3, B4 · Blocked by: none · Lane: logic · Budget: code +20 · tests +45
Seam: `check-run.py` run as a subprocess by `scripts/tests/test_check_run.py`, new class `SizingTests`
Accept:
- [x] plan.md, 4 logic tickets, code Budgets +20 +30 +30 +50 → warn `median code Budget 30 over 4 tickets` naming `merge` (B1)
- [x] the same plan with code Budgets +60 +80 +80 +120 → no warn line containing `median code Budget` (B2)
- [x] that +60 … +120 plan → note `median code Budget 80 over 4 tickets` (B3)
- [x] a ticket with 7 acceptance lines → ERROR `7 acceptance lines; a ticket has 1-6` (B4)
Verify: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests -k Sizing` (pre: Ran 0 tests, OK)
Skills: none · Status: done @ 1d56b03
Writer: Opus 5.5

### T2 — a third review cycle needs the human's approval; review allows two
Delivers: B5, B6, B7, B10 · Blocked by: none · Lane: logic · Budget: code +12 · tests +35
Seam: `check-run.py` subprocess, new class `CycleTests`; phase-4-review.md, MAINTAINING.md, README.md by grep
Accept:
- [x] review.md Created 2026-10-10 with `## Cycle 3 findings` and no approval line → ERROR naming `Cycle 3 approved by human:` (B5)
- [x] the same review.md plus `Cycle 3 approved by human: 2026-10-10` → no Cycle 3 ERROR (B6)
- [x] the same review.md Created 2026-10-09 → no Cycle 3 ERROR (B7)
- [x] phase-4-review.md: `one fix ticket with two commits`, `Red: <sha>`, `**Cycle bound — two.**`, `A P0 always escalates` all present; MAINTAINING.md, README.md say two cycles (B10)
Verify: `S=.github/skills/workflow; python3 -m unittest discover -s $S/scripts/tests -k Cycle; grep -oE 'one fix ticket with two commits|Red: <sha>|\*\*Cycle bound — two\.\*\*|A P0 always escalates' $S/references/phase-4-review.md | sort -u | wc -l; grep -c 'at most two cycles' $S/MAINTAINING.md; grep -c 'at most two patch cycles' $S/README.md; grep -ciE 'three (patch )?cycles|Cycle bound — three' $S/references/phase-4-review.md $S/MAINTAINING.md $S/README.md` → OK · 4 · 1 · 1 · 0 · 0 · 0 (pre: Ran 0 tests, OK · 0 · 0 · 0 · 1 · 1 · 1)
Skills: none · Status: done @ d3ce44c
Writer: Opus 5.5

### T3 — plan and execute rules, session counts, trial log
Delivers: B8, B9, B11, B12 · Blocked by: none · Lane: logic · Budget: code +0 · tests +0
Seam: the skill's markdown, observed by `grep`. Text: proposal C1, C2, C5 as amended by D1, D2, D4, D5, D8, D11; each phrase on one source line
Accept:
- [x] phase-2-plan.md: `**Right-sized.**`, `under about 40 code lines`, `8 is a ceiling`, `as a relation` all present; `five minutes` 0 (B8)
- [x] phase-3-execute.md: `same model and effort`, `after 3 tickets`, `Session N: T#`, `spend or a target depends on it` all present; `ticket per session` 0 (B9)
- [x] `up to 3 tickets per session`: ROUTING.md 1, README.md 2; `sessions` on the Run: line in learning-worklog.md, checkup; wrap.md `Session N:` 1 (B11)
- [x] SKILL-IMPACT.md: a `run-sizing` row with `loosens`; the Slop guards row has `lines per behaviour`; `lines per ticket fall` 0 (B12)
Verify: `S=.github/skills/workflow; R=$S/references; grep -oE '\*\*Right-sized\.\*\*|under about 40 code lines|8 is a ceiling|as a relation' $R/phase-2-plan.md | sort -u | wc -l; grep -c 'five minutes' $R/phase-2-plan.md; grep -oE 'same model and effort|after 3 tickets|Session N: T#|spend or a target depends on it' $R/phase-3-execute.md | sort -u | wc -l; grep -c 'ticket per session' $R/phase-3-execute.md; grep -c 'up to 3 tickets per session' $S/ROUTING.md $S/README.md; grep -c '<sessions> sessions' $R/learning-worklog.md; grep -c 'tickets · sessions · review cycles' .github/skills/checkup/SKILL.md; grep -c 'Session N:' $R/wrap.md; grep -c 'run-sizing.*loosens' $S/SKILL-IMPACT.md; grep -c 'Slop guards.*lines per behaviour' $S/SKILL-IMPACT.md; grep -c 'lines per ticket fall' $S/SKILL-IMPACT.md; grep -c 'usually 2–5 tickets, at most eight' $S/README.md` → 4 · 0 · 4 · 0 · 1, 2 · 1 · 1 · 1 · 1 · 1 · 0 · 2 (pre: 0 · 1 · 0 · 1 · 0, 0 · 0 · 0 · 0 · 0 · 0 · 1 · 0)
Skills: none · Status: done @ f3d885e
Writer: Opus 5.5

## Coverage
- Outcome → T1 (check-run warns on tiny tickets), T2 (errors on an unapproved third cycle), T3 (plan writes 2–5 tickets; execute runs up to 3 per session)
- B1, B2, B3, B4 → T1 · B5, B6, B7, B10 → T2 · B8, B9, B11, B12 → T3
- Out of scope: the cx-intelligence A3 advice → untouched · cross-vendor review, red before green, Risk classes, receipts, slop-guards checks → untouched · a context-meter stop → untouched · check-run enforcing `Red:` and auto-merging → untouched · `MAX_TICKETS` → stays 8

## Risks
- T3 carries the run's real product: rule prose in five files. Its greps prove the phrases exist, not that the rules read well. Review reads them in full.
- The median counts doc-only logic tickets at code +0. A skills repo with 4 or more of them gets the merge warning. D12 accepts this; the first such run judges it.
- Option not taken: one check-run ticket. F1's 4-line cap forces two.

## TODO impacts
none (no TODO.md). Optional, human-only: ROUTING-NOTES.md:11 lists the `Run:` fields without `sessions`.

## Product doc impacts
No PRODUCT.md, DESIGN.md or ROADMAP.md changes. README.md: the plan rows' "at most eight small tickets" becomes "usually 2–5 tickets, at most eight" (T3), and the review row says two cycles (T2).

## Deviations
- T3: the 3-ticket cap now also bounds runs of mechanical tickets, which rolled on without limit before (D1 names no exception). ROUTING.md *Modes* still says tickets of different lanes can share a session; D2 now needs the same effort, and only the human edits that line.
- C1-T2: ran in the same session as C1-T1 at the human's request, without a reset, although its lane (mechanical · medium) differs from C1-T1's (logic · high).
