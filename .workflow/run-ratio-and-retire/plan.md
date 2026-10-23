Command: workflow plan run-ratio-and-retire
Created: 2026-10-23 · Claude Opus 5.5
Base:    cafdfaa
Inputs:  .workflow/run-ratio-and-retire/brainstorm.md @ 43e006b
Status:  drafting

Docs read: none in scope (workflow and checkup skills only; no PRODUCT.md or DESIGN.md)
Size: code 785 · tests 502 · ratio 0.64 · largest touched check-run.py 785, test_check_run.py 502, checkup/SKILL.md 320 (doc) · over 1,000: none
Decisions: pending — 1 (B7 data source), 2 (absolute ratio trigger), ticket list

## Execution state
<filled by execute>

## Findings
| # | What is true | What it changes |
|---|---|---|
| F1 | cx-intelligence WORKLOG: 0 of 13 `Run:` lines carry net code or tests (j-skills: 2 of 7) | D6's "sum the Run: lines" has no data in the repo B7 names; T2 takes the numbers from git numstat over the range the existing *Code growth* bullet uses (Decision 1) |
| F2 | cx-intelligence tests ÷ code depends on what counts as code: 0.10 over all tracked text (102k / 1.05M, SQL, HTML, JSON data), about 0.29 over source languages; the brief's 64.2k / 83.6k is not reproducible | a `> 1.0` trigger never fires there; T2 reports the ratio and triggers on the trend only (Decision 2) |
| F3 | cx-intelligence `50ef5321^..a5f0f341` (since 2026-10-17, the 10th-newest WORKLOG entry): net tests +3535, net code +2885 | B7's trend arm fires on real data; T2's literal |
| F4 | Replaying P1 with check-run's `RECEIPTS` (run `scripts/` count as code) instead of excluding all of `.workflow/`: variant A still flags only `live-run-guardrails`, tests +679, code added +442 | T1 reuses `RECEIPTS`; B8 holds |
| F5 | Reuse: `check_overrun` (check-run.py:389) and `note_net_growth` (check-run.py:577) hold the same numstat loop | T1 extracts one `growth(repo, a, b)` helper; the run gate is its third caller |
| F6 | Reuse: `waiver(doc, kind, tid)` (check-run.py:370) already matches `Ratio waived: run — <reason>` with `tid="run"` | T1 reuses it; no new parser |
| F7 | Six tests assert the ticket-ratio ERROR (`test_growth_net_ratio`, `test_growth_ratio_waivers`, `test_ratio_ignores_bare_deviations_on_old_plans`, `test_committed_test_ratio`, `test_overrun_tests_over_ratio_is_an_error`, `test_overrun_old_plan_still_checks_ratio`) | T1 turns them into warn cases and merges the duplicates; the assertion changes are planned deviations, counted before and after |
| F8 | Ticket-ratio text: tests.md:80-81, phase-3-execute.md:98-100, phase-2-plan.md:32, check-run.py docstring line 15; phase-4-review.md has none | T2 edits all four and adds the run waiver to phase-4-review.md (D2: the reviewer judges it) |
| F9 | Range choice: plan.md Base .. the latest `done @` sha (P1), not HEAD; HEAD would add patch fixes and other runs' commits | T1 uses the P1 range |

## Tickets

### T1 — check-run judges test growth once per run
Delivers: B1, B2, B3, B4, B5, B8 · Blocked by: none · Lane: logic
Budget: code +45 · tests +30
Seam: `check-run.py` run as a subprocess on fixture runs (`test_check_run.py` `check()`); `growth()` extracted from the two numstat loops (F5); replay script in the run's `scripts/`
Accept:
- [ ] both tickets done, tests net +151, code added +100, no run waiver → ERROR line contains `run: tests net +151 over 1.5× code added +100 (allowed 150)` (B1)
- [ ] same run plus `Ratio waived: run — fixture rewrite` under `## Deviations` → warn repeats `+151` and `fixture rewrite`; output has `0 errors` (B2)
- [ ] tests net +150 with code added +100, and tests net +99 with code added +0 → no line contains `run: tests net` (B3)
- [ ] logic and contract ticket, tests net +76, code +50, no waiver → warn `T1: tests net +76 over 1.5× code +50`; output has `0 errors` (B4)
- [ ] B1's run with T2 `Status: todo` → no line contains `run: tests net` (B5)
- [ ] `receipts/t1-replay.txt`, the new gate over P1's 26 runs → 1 flagged: `live-run-guardrails` tests +679 · code added +442 (B8)
Verify: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests -k ratio` and `receipts/t1-replay.txt` (pre: 7 passed · no receipt)
Skills: none
Status: todo

### T2 — docs state the run rule; checkup reports test growth
Delivers: B6, B7 · Blocked by: T1 · Lane: logic
Budget: code +0 · tests +0
Seam: `grep` over the workflow `references/`, `MAINTAINING.md`, `check-run.py` and `checkup/SKILL.md`; checkup §6 commands run on cx-intelligence
Accept:
- [ ] `grep -c 'Ratio waived: run'` over tests.md, phase-2-plan.md, phase-3-execute.md, phase-4-review.md → ≥ 1 in each file (B6)
- [ ] `grep -rnE 'Ratio waived: T#|error above 1\.5'` over workflow `references/`, `MAINTAINING.md`, `scripts/check-run.py` → no output (B6)
- [ ] `grep -c 'Test growth' .github/skills/checkup/SKILL.md` → 1; that bullet contains `workflow improve tests - goal: fewer tests, same coverage` (B7)
- [ ] `receipts/t2-checkup-cx.md`, §6 test-growth commands on cx-intelligence `50ef5321^..a5f0f341` → net tests +3535 · net code +2885 · ⚠️ with that recommendation (B7)
Verify: `grep -c 'Ratio waived: run' .github/skills/workflow/references/{tests,phase-2-plan,phase-3-execute,phase-4-review}.md; grep -rnE 'Ratio waived: T#|error above 1\.5' .github/skills/workflow/references .github/skills/workflow/MAINTAINING.md .github/skills/workflow/scripts/check-run.py; grep -c 'Test growth' .github/skills/checkup/SKILL.md` (pre: 0 · 0 · 0 · 0 · 3 hits · 0)
Skills: .github/skills/agent-docs/SKILL.md
Status: todo

## Coverage
- Outcome → T1 (the gate fires once per run, on check-run's output) and T2 (checkup's test-growth line on cx-intelligence)
- B1, B2, B3, B4, B5, B8 → T1 · B6, B7 → T2
- Out of scope: wrap step 5b → untouched · suite runtime in checkup → untouched · mechanical-lane ratio → untouched · per-ticket Budget overrun rule → untouched · cx-intelligence and agent-cv → read only

## Risks
T1 is the risk: it rewrites six existing ratio tests, and a lost assertion would hide a regression; review counts assertions before and after.
A run whose tickets land out of order: the latest `done @` is picked by commit count, as P1 did.
Not taken: gating on net code (P1 variant B), which flags refactor runs.

## TODO impacts
none (the brief names no TODO item)

## Product doc impacts
- PRODUCT.md, DESIGN.md: not present
- workflow `ROADMAP.md` row 3 ("gate the run, keep the per-ticket ratio as a warning") → delivered by this run; wrap updates the row
