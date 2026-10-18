Command: workflow plan growth-ratchets
Created: 2026-10-18
Base:    d62b5d0
Inputs:  .workflow/growth-ratchets/brainstorm.md @ 1971256
Status:  complete

Docs read: none in scope (j-skills has no PRODUCT.md or DESIGN.md)
Size: code 746 · tests 368 · ratio 0.49 · largest touched check-run.py 746, test_check_run.py 368 · over 1,000: none
Decisions: 1a (tickets approved) · 2a (a budget waiver prints a note with net and budget)

## Execution state
Current: T1, T2 and patch C1-T1 done; review cycle 2 next.
T1 @ 1a65a10
T2 @ 9974505
writer: GPT-6.1 Sol
Session 1: T1
Session 2: T2
Session 3: C1-T1
Baseline: session 1 had 38 passing tests; session 2 had 42. T2 fixes both WORKLOG errors; the existing slop-guards size warning remains.
Checks approved: existing unittest suite, check-run.py, git diff --check; no repo AGENTS.md.
Contract: GROWTH_SINCE = 2026-10-19; older plans retain their rules.
Uncommitted: none after this handoff commit.
Pending decision: none.

## Findings
| # | What is true | What it changes |
|---|---|---|
| F1 | The skill lives at `.github/skills/workflow/`; `~/.claude/skills/workflow` now links to the `~/.agents/skills/workflow` copy, not the clone | Every Verify uses the repo path; Claude sessions see the edits only after `npx skills update -g` |
| F2 | `check_overrun` (`check-run.py:395`) counts tests and code as added lines only; `deviated()` (`:379`) skips the whole check when any `## Deviations` line names the ticket ID (`:347`) | T1 adds tests net and keyed waivers inside `check_overrun`, and keeps the any-mention skip only for plans created before `GROWTH_SINCE` |
| F3 | Both ratio and budget messages say "log the reason under `## Deviations`" (`:411`, `:417`); `tests.md:80` says "explain exceptions under `## Deviations`" | T1 rewrites both messages to name the waiver keys, old runs included: a keyed line also names the ID, so old runs still skip |
| F4 | B5 says a budget waiver prints no warning; D2 says every waiver prints a warning with its numbers | T1 prints a budget waiver as a `note` with net and budget (Decision 2) |
| F5 | The test helper `check()` commits ticket files on an empty base, so a ticket commit can never delete lines | T1 adds a seed-files argument to `check()`; the B1 and B2 shapes need deletions |
| F6 | Reuse: `Doc.section("Deviations")` (`:125`) and `slop_gated(since)` (`:144`) exist; no waiver parser exists | T1 reuses both; one new small parser for `Ratio waived:` / `Budget waived:` lines |
| F7 | `check_worklog` (`:576`) reads `<repo>/WORKLOG.md`. A trial copy at the root makes `--all` report 0 errors for lean-runs and run-sizing (both entries carry Seats: and Skills:) | D5 holds: `git mv` alone delivers B7, no code change |
| F8 | `phase-2-plan.md:29` says "≥ 50 test lines over 1.5× code"; it becomes untrue after T1 | T2 rewrites it to name tests net |
| F9 | With a pathspec on the skill folder, `git diff --numstat` shows the moved WORKLOG.md as −76 lines | B8's net count excludes `**/WORKLOG.md` by glob, so the move cannot pay for doc growth |
| F10 | This plan is created 2026-10-18: lean-gated, not growth-gated. T1's own commit meets the added-lines 1.5× rule | T1 Budget keeps tests at most 1.5× code |

## Tickets

### T1 — check-run ratios tests net and honours only keyed waivers
Delivers: B1, B2, B3, B4, B5, B6 · Blocked by: none · Lane: logic
Budget: code +35 · tests +50 · why: a seed-files argument on the `check()` helper for deleted lines
Seam: `check-run.py` run as a subprocess on fixture runs (`scripts/tests/test_check_run.py`, `check()`)
Accept:
- [x] Plan created 2026-10-19, logic ticket: tests +201 −305 with code +89 −313; tests +252 −128 with code +134; tests net +90 with code +60; tests net +49 with code 0 → `0 errors` each (B1, B2)
- [x] Created 2026-10-19, tests +130 −10, code +60 → ERROR containing `T1: tests net +120 over 1.5× code +60 (allowed 90)` (B2)
- [x] Over-ratio ticket with `- Ratio waived: T1 — fixture rewrite` under `## Deviations` → `0 errors`, one warn containing `tests net +120` and `allowed 90` (B3)
- [x] Over-ratio ticket whose Deviations hold only `- T1 proof: receipts/t1.txt`, then only `- Ratio waived: T1 —` → the ratio ERROR stands in each (B3, B4)
- [x] Net over 2× Budget: `- Budget waived: T1 — reason` → no warn, one note containing the net and budget; a bare `- T1 note` line → the overrun warn (B5)
- [x] Plan created 2026-10-18, tests +130 code +60 → ERROR containing `tests +130 over 1.5× code +60`; a bare `- T1 note` Deviations line → `0 errors` (B6)
Verify: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests -k growth` (pre: NO TESTS RAN)
Skills: none
Status: done @ 1a65a10
Writer: GPT-6.1 Sol

### T2 — docs name tests net and the waiver keys; WORKLOG.md moves to the root
Delivers: B7, B8 · Blocked by: T1 · Lane: mechanical
Seam: the workflow docs, `check-run.py --all` in j-skills, `git diff --numstat`
Accept:
- [x] `grep -c 'Ratio waived: T'` in `references/tests.md` and `references/phase-3-execute.md` → 1 each; `grep -c 'tests net'` in `references/phase-2-plan.md` → 1 (B8)
- [x] `explain exceptions under` and `log the reason under` across the skill folder's `*.md` and `*.py`, SKILL-IMPACT.md excluded → 0 occurrences (B8)
- [x] Net lines of `README.md` and the skill folder's `*.md` since d62b5d0, excluding `**/SKILL-IMPACT.md` and `**/WORKLOG.md` → net ≤ 0 (B8)
- [x] `ls WORKLOG.md` → present; `.github/skills/workflow/WORKLOG.md` → absent; `git log --follow WORKLOG.md` → shows the lean-runs entry commit 5d5eba7 (B7)
- [x] `check-run.py --all` → 0 lines containing `has no entry` (B7)
Verify: `W=.github/skills/workflow; grep -c 'Ratio waived: T' $W/references/tests.md $W/references/phase-3-execute.md; grep -c 'tests net' $W/references/phase-2-plan.md; grep -rhoE --include='*.md' --include='*.py' --exclude=SKILL-IMPACT.md 'explain exceptions under|log the reason under' $W | wc -l; git diff --numstat d62b5d0 -- README.md ":(glob)$W/**/*.md" ':(exclude,glob)**/SKILL-IMPACT.md' ':(exclude,glob)**/WORKLOG.md' | awk '{n+=$1-$2} END {print "net", n+0}'; ls WORKLOG.md $W/WORKLOG.md 2>&1; python3 $W/scripts/check-run.py --all | grep -c 'has no entry'` (pre: 0 · 0 · 0 · 3 · net 0 · root WORKLOG.md missing, skill copy present · 2)
Skills: none
Status: done @ 9974505
Writer: GPT-6.1 Sol

## Coverage
- Outcome: the ratio flags bloat but not rewrites or moves → T1 (B1, B2); waivers only by keyed line, printed with numbers → T1 (B3–B5); `--all` reports no worklog error → T2 (B7)
- B1 → T1 · B2 → T1 · B3 → T1 · B4 → T1 · B5 → T1 · B6 → T1 · B7 → T2 · B8 → T1 (messages), T2
- Out of scope: run-level ratio gate → untouched · mechanical-lane ratio gate → untouched · simplify pass and wrap retiring → untouched · skill folder MEMORY.md and SKILL-IMPACT.md stay put · cx-intelligence → untouched · human-approved waivers → untouched

## Risks
- T1 is the risk: the old any-mention skip must still hold for plans created before 2026-10-19, or every done run's check changes. B6 and the existing `deviation=True` tests guard it.
- Moving WORKLOG.md drops it from the installed skill copies; nothing in the skill reads it there (F7).
- Not taken: printing a budget waiver as a warning (D2 literal); it would make a waived overrun look like an unwaived one.

## TODO impacts
- The `check_worklog` root WORKLOG.md item → completed by T2.
- The ratio and waiver items the brief seeds from → completed by T1, if TODO.md lists them; wrap confirms.

## Product doc impacts
- No PRODUCT.md, DESIGN.md or ROADMAP.md at the repo root: no changes.
