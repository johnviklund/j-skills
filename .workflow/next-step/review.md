Command: workflow review next-step
Created: 2026-10-29 · Claude Opus 5.5
Base:    e4d3a58
Inputs:  .workflow/next-step/plan.md @ 19533a5 · .workflow/next-step/patch_plan.md @ 688e443
Status:  complete

Scope, cycle 3: the fix diff 688e443..e4d3a58, which is C2-T2 5c5e306 and C2-T1 eac69f8 with its red commit 0a0f06d, plus each cycle 2 finding's class.
Cycle 3 approved by human: 2026-10-29 — option 1a, one more cycle fixing C2-1 and C2-2.

## Coverage
- [x] C2-T1 — acceptance 3/3 tested and passing; red 0a0f06d fails at its own commit (2 subtests: C2-1 for C2-2, C2-2 for C2-3); the fix eac69f8 touches only check-run.py and SKILL-IMPACT.md; run-worktrees @ 68cbf30 now gives `Resolve C2-2, C3-1 before continuing.`
- [x] C2-T2 — 2/2; 5c5e306 changes no line of check-run.py; `if not open_finding(f)` and `if False` at check-run.py:592 each turn test_check_run.py red
- [x] C2-1 class — next-step.py:169 is the only id reader; `check_review` labels findings by title. Every review.md version in git history, 54 blobs with 83 titles that name their own id: the new numbering matches 83 of 83, the old one missed 2 (run-worktrees @ b1cd333, c8a0440)
- [x] B1–B8 delivered · Outcome observed via `next-step.py --json` on this run and on run-worktrees @ 68cbf30, manual, no verify skill · out of scope untouched: the fix diff touches only check-run.py, test_check_run.py, test_next_step.py and SKILL-IMPACT.md
- [x] .workflow/ dependency check: the same hits as cycle 2, the run paths next-step.py builds and test fixtures
Size: +272 code · +407 tests · ratio 1.496 · net +668 · over 1,000: none (check-run.py 840 lines); the fix cycle alone is +4 code, +24 tests
Reachability: no new file; the Resolved-id set (check-run.py:534) ← `review_findings` ← check-run.py:572, next-step.py:167 · guards shown failing: 10 of 11 mutations on the fix diff killed (eight on the id numbering, `or []`, C2-2's two); dropping `if text.startswith("|")` survives (C3-1)
Independence: cross-vendor (writer GPT-6.1 Sol, OpenAI · reviewer Claude Opus 5.5, Anthropic)
Threats: unchanged from cycle 1. The fix reads the first cell of each `## Resolved` row as data, only to skip ids; it adds no input, write or command.
Escape hatches: 1 hit, the same `any(` false positive in next-step.py. Tests: workflow 109 OK, checkup 8 OK, exit 0. Assertions in tests the run did not create: test_check_run.py 77 → 79, test_run_worktree.py 148 → 148. check-run: 0 errors.

## Resolved
| Finding | Sev | Title | Disposition | Resolved |
|---|---|---|---|---|
| C1-1 | P1 | An open fix-now finding from an earlier cycle routes to wrap | fix now | @ e6a8e5d (cycle 2) |
| C1-2 | P1 | A receipt path in backticks never unblocks its operator ticket | fix now | @ f2bba2b (cycle 2) |
| C1-3 | P1 | Eight guards in the new next-step.py have no failing test | fix now | @ 0762b64 (cycle 2) |
| C1-4 | P2 | A P0 fix on the operator lane reports `approval: auto` | fix now | @ 6e87503 (cycle 2) |
| C1-5 | P2 | A run parked after planning resumes at `workflow plan` | fix now | @ 08048cb (cycle 2) |
| C1-6 | P3 | Three minor items | defer — stays in review.md; text in git at `ae08347` | settled (cycle 2) |
| C2-1 | P1 | The blocker names a resolved finding once earlier ones fold into `## Resolved` | fix now | @ eac69f8 (cycle 3) |
| C2-2 | P1 | Wrap's open-finding gate in check-run has no failing test | fix now | @ 5c5e306 (cycle 3) |
| C2-3 | P3 | Four minor items | defer — stays in review.md; text in git at `688e443` | settled (cycle 3) |

## Cycle 3 findings
### P1 — C3-1 · The fix's table-row filter has no failing test
- Evidence: C2-T1 added `if text.startswith("|")` to the Resolved-id set (check-run.py:534). Deleting it leaves both suites green (workflow 109 OK), yet next-step.py and check-run.py then crash with an IndexError on this run's own review.md: `Doc` keeps blank lines (check-run.py:120-121), and every real `## Resolved` table ends in one. The test's table runs straight into the next heading (test_next_step.py:270-272). A surviving mutation on a line the fix added; the class of C2-2.
- Remedy: end the test's table with a blank line, as real files do: `+ "\n"` after the rows at test_next_step.py:271. Tried in a throwaway worktree: the real code passes, the mutation fails both subtests. Test-only, one line.
- Disposition: fix now
- Resolved: —

### P3 — C3-2 · Two minor items
- A finding folded into `## Resolved` whose `###` section is left in place now shifts every later id in its cycle by one. The fold rule moves the text out, and 0 of 54 historical review.md versions hold both.
- SKILL-IMPACT.md:13 adds a sixth trialing row for this run; wrap folds them (C2-3's last item).
- Disposition: defer — stays in review.md
- Resolved: —

## Pre-existing / environmental
- The installed workflow skill this session loaded still carries an older next-step.py and check-run.py. It catches up only after `npx skills update -g` (AGENTS.md).

## Cycle 3 verdict
Both cycle 2 fixes work. C2-T1's red test fails at its own commit and passes after a fix that leaves the tests untouched. The run-worktrees review now names C2-2, C3-1, and the new numbering matches every id a reviewer wrote across this repo's 54 review.md versions. C2-T2's test turns both checker mutations red. One new P1 sits in the C2-1 fix: deleting its table-row filter keeps the suite green, yet crashes on every real review.md (C3-1). The code is right; only its test is missing. This is past the cycle bound, so C3-1 goes to the human: a fourth cycle or defer to `TODO.md`. C3-2 stays here.
