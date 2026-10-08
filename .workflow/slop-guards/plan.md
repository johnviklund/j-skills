Command: workflow plan slop-guards
Created: 2026-10-08
Base:    85b5b9e
Inputs:  .workflow/slop-guards/brainstorm.md @ 8fa6782
Status:  complete

Docs read: none in scope (PRODUCT.md and DESIGN.md absent)
Size: code 2,113 · tests 24 · ratio 0.01 · largest touched check-run.py 563, SKILL.md 173, wrap.md 170 · over 1,000: none
## Execution state
## Findings
| # | What is true | What it changes |
|---|---|---|
| F1 | `## Deviations` lives in plan.md (phase-3-execute.md:81); the execute report is chat only | B3/B4 "stated reason" = a `## Deviations` line naming the ticket id |
| F2 | An operator ticket commits twice: handoff, then receipt at `done @` (phase-3-execute.md:65) | A ticket's diff = previous `done @` sha in the same file (else `Base`) `..` its own `done @` sha |
| F3 | `*.md`/`*.txt` are receipts (SKILL.md receipt rule) | Numstat counts non-receipt files only. Test file = a `tests/`, `test/`, `__tests__/` folder, or `test_*`, `*_test.*`, `*.test.*`, `*.spec.*` |
| F4 | check-run has no date gate; cx-intelligence `self-service-gaps` (done) has review.md and wrap.md `Created: 2026-10-08`; its plan's `Created:` has text after the date | New checks fire only when the artifact's first `Created:` date ≥ `SLOP_SINCE = 2026-10-09` (human, decision 1a) |
| F5 | D3 thresholds need one home | Constants at the top of check-run.py; docs quote each once. 1,000-line file has no check: plan and review `Size:` lines only |
| F6 | Execute prescribes a dry-run for every operator ticket (phase-3-execute.md:65); "Extra tests are welcome" wraps lines 80-81 | T3 scales that paragraph to `Risk:`; T7 greps `tests are welcome` |
| F7 | Wrap re-entry re-checks "no code since reviewed Base" (wrap.md:24); check-run quotes steps 9a/9b | Retire is step 5b (no renumbering); T5 exempts the Retire sha ticked in `## Steps`. Retire only deletes; a deletion needing an edit becomes a TODO line |
| F8 | Review's `.workflow/` grep is already repo-wide (phase-4-review.md:88) | B10 adds it to `check-run.py --all` (`checkup` runs it), test files only. The new test file must not hold the string `.workflow/` (T5 line 3) |
| F9 | Python 3.9.6, no pytest, no AGENTS.md; check-run is stdlib-only | `unittest` in `scripts/tests/test_check_run.py`, temp git repos, check-run as a subprocess. Execute baseline: that suite plus `check-run.py --all` |
| F10 | Reuse: `field()` already parses `Budget: code +40 · tests +60` whole; `git_out()` runs git | T1-T5 reuse both; no new parser, no git wrapper |
| F11 | Byte budgets (MAINTAINING.md ~10 KB): SKILL.md 10,273; phase-2-plan 9,472; phase-4-review 9,382; edits add ~1-1.7 KB each | Accepted over budget (human, decision 3a); T8's row notes it |
| F12 | D3's 3× rule ERRORs on +1 code / +4 tests | B4 ERROR also needs ≥ 50 test lines added (human, decision 2a) |

## Tickets

### T1 — Plans carry a line budget per ticket
Delivers: B1, B2, B7 · Blocked by: none · Lane: logic · Budget: code +50 · tests +100
Seam: `check-run.py --repo <tmp> <slug>` output on fixture runs in a temp git repo
- [ ] Fixture plan with a `Size:` line and `Budget:` on every ticket → summary `0 errors · 0 warnings` (B1)
- [ ] Logic ticket T2 with no `Budget:` → warn line containing `T2: no Budget:` (B2)
- [ ] An acceptance line of 41 words → warn line containing `T1: acceptance line has 41 words` (B7)
- [ ] The no-Budget fixture with plan `Created: 2026-10-08` → summary `0 errors · 0 warnings` (B2)
Verify: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests -k budget` (pre: new file)
Skills: none · Status: todo

### T2 — Ticket commits that overrun their budget get flagged
Delivers: B3, B4 · Blocked by: T1 · Lane: logic · Budget: code +50 · tests +100
Seam: `check-run.py --repo <tmp> <slug>` output on fixture runs with ticket commits
- [ ] `Budget: code +20 · tests +30`, commit net +101 lines, no Deviations line → warn containing `T1: net +101 lines, over 2× budget +50` (B3)
- [ ] Same commit plus a `## Deviations` line naming T1 → no line containing `over 2× budget` (B3)
- [ ] Logic ticket commit +12 code, +178 test lines, no Deviations line → ERROR containing `T1: tests +178 over 3× code +12` (B4)
- [ ] Same +12/+178 commit, plan `Created: 2026-10-08` → summary contains `0 errors` (B4)
Verify: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests -k overrun` (pre: new file)
Skills: none · Status: todo

### T3 — Operator tickets carry a risk class
Delivers: B5, B6, B13 · Blocked by: T2 · Lane: logic · Budget: code +25 · tests +60
Seam: check-run output on fixture runs; `phase-2-plan.md` and `phase-3-execute.md` text
- [ ] `Risk: cheap` operator ticket whose handoff commit adds `scripts/test_probe.py` → warn containing `T3: cheap operator ticket adds scripts/test_probe.py` (B5)
- [ ] Operator ticket with no `Risk:` → warn containing `T3: operator ticket has no Risk:` (B6)
- [ ] `grep -cE '^\| .(cheap|costly|irreversible). \||no stated ceiling' phase-2-plan.md` → 4 (B6)
- [ ] `grep -c '.Risk:. class' phase-3-execute.md` → 1 (B13)
Verify: `S=.github/skills/workflow; python3 -m unittest discover -s $S/scripts/tests -k operator; grep -cE '^\| .(cheap|costly|irreversible). \||no stated ceiling' $S/references/phase-2-plan.md; grep -c '.Risk:. class' $S/references/phase-3-execute.md` (pre: new file · 0 · 0)
Skills: none · Status: todo

### T4 — Review records size and checks for waste
Delivers: B8, B14 · Blocked by: T1 · Lane: logic · Budget: code +15 · tests +40
Seam: check-run output on a fixture `review.md`; `phase-4-review.md` text
- [ ] Complete review.md whose Coverage has no `Size:` line → ERROR containing `Coverage has no Size: line` (B8)
- [ ] Same review plus `Size: +40 code · +60 tests · ratio 1.5 · net +100 · over 1,000: none` → summary contains `0 errors` (B8)
- [ ] `grep -cE '\*\*(Same-run waste|Reachability|Verify the verification|Blind first)\.\*\*' phase-4-review.md` → 4 (B14)
- [ ] `grep -cE '^(Size|Reachability): |^\| \*\*P1\*\*.*same-run waste' phase-4-review.md` → 3 (B14)
Verify: `S=.github/skills/workflow; python3 -m unittest discover -s $S/scripts/tests -k review; grep -cE '\*\*(Same-run waste|Reachability|Verify the verification|Blind first)\.\*\*' $S/references/phase-4-review.md; grep -cE '^(Size|Reachability): |^\| \*\*P1\*\*.*same-run waste' $S/references/phase-4-review.md` (pre: new file · 0 · 0)
Skills: none · Status: todo

### T5 — Wrap retires what the run made obsolete
Delivers: B9, B10, B15 · Blocked by: T1 · Lane: logic · Budget: code +40 · tests +60
Seam: check-run output on fixture runs and repos, and on j-skills; `wrap.md` text
- [ ] Done wrap.md with no `Retired:` line → ERROR containing `wrap.md has no Retired: line` (B9)
- [ ] `--all` on a fixture repo whose `tests/test_x.py` opens `.workflow/x/data.json` → warn naming `tests/test_x.py` and `opens a .workflow/ path` (B10)
- [ ] `check-run.py --all` in j-skills → 0 lines containing `opens a .workflow/ path` (B10)
- [ ] `grep -cE 'nothing is deleted from the run folder|^5b\. \*\*Retire' wrap.md` → 2 (B15)
Verify: `S=.github/skills/workflow; python3 -m unittest discover -s $S/scripts/tests -k wrap; python3 $S/scripts/check-run.py --all | grep -c 'opens a .workflow/ path'; grep -cE 'nothing is deleted from the run folder|^5b\. \*\*Retire' $S/references/wrap.md` (pre: new file · 0 · 0)
Skills: none · Status: todo

### T6 — Hub and plan docs ask for the smallest diff and reuse
Delivers: B1, B11, B13 · Blocked by: none · Lane: mechanical · Budget: code +0 · tests +0
Seam: `SKILL.md` Ground rules and `references/phase-2-plan.md` text
- [ ] `grep -c '^- \*\*Simplicity\.\*\*' SKILL.md` → 1 (B11)
- [ ] `wc -l < SKILL.md` → at most 180 (B11)
- [ ] `grep -cE '^Size: |^Budget: code \+' phase-2-plan.md` → 2 (B1)
- [ ] `grep -cE '\*\*Reuse findings\.\*\*|two or more near-copies|at most ~25 words' phase-2-plan.md` → 3 (B13)
Verify: `S=.github/skills/workflow; grep -c '^- \*\*Simplicity\.\*\*' $S/SKILL.md; wc -l < $S/SKILL.md; grep -cE '^Size: |^Budget: code \+' $S/references/phase-2-plan.md; grep -cE '\*\*Reuse findings\.\*\*|two or more near-copies|at most ~25 words' $S/references/phase-2-plan.md` (pre: 0 · 173 · 0 · 0)
Skills: none · Status: todo

### T7 — Tests stay proportional to the code
Delivers: B12 · Blocked by: none · Lane: mechanical · Budget: code +0 · tests +0
Seam: `references/tests.md`; `references/phase-3-execute.md` text, whose `Noticed:` also names a helper written despite a reuse hit
- [ ] `grep -cE '^\*\*(Smallest seam|One concept per test|Parametrize variants|No test imports a test|Never assert source text|Prove it can fail|Test budget)\.\*\*' tests.md` → 7 (B12)
- [ ] `wc -l < tests.md` → between 60 and 75 (B12)
- [ ] `grep -c 'tests are welcome' phase-3-execute.md` → 0 (B12)
- [ ] `grep -cE '^   Mutation: |only when a mutation survives' phase-3-execute.md` → 2 (B12)
Verify: `S=.github/skills/workflow/references; grep -cE '^\*\*(Smallest seam|One concept per test|Parametrize variants|No test imports a test|Never assert source text|Prove it can fail|Test budget)\.\*\*' $S/tests.md; wc -l < $S/tests.md; grep -c 'tests are welcome' $S/phase-3-execute.md; grep -cE '^   Mutation: |only when a mutation survives' $S/phase-3-execute.md` (pre: 0 · 48 · 1 · 0)
Skills: none · Status: todo

### T8 — Credit the source and log the change
Delivers: B15 · Blocked by: T1, T2, T3, T4, T5, T6, T7 · Lane: mechanical · Budget: code +0 · tests +0
Seam: `THIRD-PARTY-NOTICES.md`, `SKILL-IMPACT.md`, MAINTAINING.md check-run row text
- [ ] `grep -c 'Copyright (c) 2025 Addy Osmani' THIRD-PARTY-NOTICES.md` → 1 (B15)
- [ ] `grep -c 'https://github.com/addyosmani/agent-skills' THIRD-PARTY-NOTICES.md` → 1 (B15)
- [ ] `grep -cF 'tests 98.7k / code 73.6k = 1.34' SKILL-IMPACT.md` → 1 (B15)
- [ ] `grep -cF 'operator prep 470-770 lines' SKILL-IMPACT.md` → 1 (B15)
Verify: `S=.github/skills/workflow; grep -c 'Copyright (c) 2025 Addy Osmani' THIRD-PARTY-NOTICES.md; grep -c 'https://github.com/addyosmani/agent-skills' THIRD-PARTY-NOTICES.md; grep -cF 'tests 98.7k / code 73.6k = 1.34' $S/SKILL-IMPACT.md; grep -cF 'operator prep 470-770 lines' $S/SKILL-IMPACT.md` (pre: 0 · 0 · 0 · 0)
Skills: none · Status: todo

## Coverage
- Outcome → T1, T2 (plan budgets checked), T4 (review `Size:`), T5 (wrap `Retired:`), T6, T7 (docs)
- B1 → T1, T6 · B2 → T1 · B3 → T2 · B4 → T2 · B5 → T3 · B6 → T3 · B7 → T1 · B8 → T4 · B9 → T5 · B10 → T5 · B11 → T6 · B12 → T7 · B13 → T3, T6 · B14 → T4 · B15 → T5, T8
- Out of scope: exam slop cases (seed T7), cx-intelligence cleanup runs, personas/ship/CI/hooks, per-repo threshold overrides → untouched

## Risks
T2 is riskiest: the ticket diff range (F2) assumes tickets commit in plan order; a squash or rebase skews it. A false ERROR blocks execute and wrap in every repo, so F4's gate matters. Not taken: a `check-run.py --size` mode printing the baseline; planners use the shell command in phase-2-plan.

## TODO impacts
none (the brief names no TODO item). Optional, same files: `checkup` could name the B10 pin warning in its report.

## Product doc impacts
PRODUCT.md, DESIGN.md: absent. workflow/ROADMAP.md: not opened by plan; wrap checks it. workflow/README.md: no changes.
