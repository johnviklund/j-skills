Command: workflow review next-step
Created: 2026-10-29 · Claude Opus 5.5
Base:    0dc90ce
Inputs:  .workflow/next-step/plan.md @ 19533a5 · .workflow/next-step/patch_plan.md @ 1aa0b47
Status:  complete

Scope, cycle 2: the fix diff 1aa0b47..0dc90ce, which is C1-T1 e6a8e5d, C1-T2 f2bba2b, C1-T3 0762b64, C1-T4 6e87503 and C1-T5 08048cb with their red commits, plus each cycle 1 finding's class. Cycle 1 reviewed the five ticket commits 904f083..a354025.

## Coverage
- [x] C1-T1 — acceptance 3/3 tested and passing; red 29100c5 fails at its own commit (wrap, not review); the fix leaves tests untouched; `grep -c Disposition next-step.py` → 0. Its check-run side has no test (C2-2), and its ids are positional (C2-1)
- [x] C1-T2 — 2/2; red 93339f6 fails (blocker T3, not null); the fix leaves tests untouched. `receipt:` sites: next-step.py:107 parses the path, check-run.py:337 only checks the word
- [x] C1-T3 — 2/2; the eight C1-3 mutations re-run alone in a throwaway worktree: 8 of 8 fail the suite; 0762b64 changes no line of next-step.py
- [x] C1-T4 — 2/2; red 98b36d0 fails (auto, not human; a missing `fix:operator` row exits 0); the fix leaves tests untouched
- [x] C1-T5 — 2/2; red 97427b2 fails (`workflow plan`, not execute or review); the fix leaves tests untouched; the existing parked case is unchanged
- [ ] B1–B8 delivered · the Outcome is false in one state: the blocker names a resolved finding after a fold (C2-1) · Outcome observed via `next-step.py --json` on this run (phase `review`) and on the run-worktrees review at 68cbf30 and af1d147, manual, no verify skill · out of scope untouched: the fix diff touches only check-run.py, next-step.py, test_next_step.py and SKILL-IMPACT.md
- [x] .workflow/ dependency check: the same hits as cycle 1, the run paths next-step.py builds (:140-166) and test fixtures
Size: +269 code · +383 tests · ratio 1.42 · net +641 · over 1,000: none (check-run.py 837 lines); the fix cycle alone is +22 code, +75 tests
Reachability: `open_finding` ← check-run.py:589, next-step.py:169 · `approval_key` ← next-step.py:185 · guards shown failing: 21 of 24 mutations killed, the eight C1-3 re-runs and 16 on the fix diff; `if open_finding(f)` at check-run.py:589 survives inverted and never-true (C2-2); the parked Why literal survives (C2-3)
Independence: cross-vendor (writer GPT-6.1 Sol, OpenAI · reviewer Claude Opus 5.5, Anthropic)
Threats: unchanged from cycle 1. The fix diff adds no input, write or command. A parked run now reads the same run files a complete run reads (next-step.py:142-143), and its `command` is still `workflow <phase> <slug>` (:194).
Escape hatches: 1 hit, the same `any(` false positive at next-step.py:145. Tests: workflow 107 OK, checkup 8 OK, exit 0. Assertions in tests the run did not create: test_check_run.py 77 → 77, test_run_worktree.py 148 → 148. check-run: 0 errors.

## Resolved
| Finding | Sev | Title | Disposition | Resolved |
|---|---|---|---|---|
| C1-1 | P1 | An open fix-now finding from an earlier cycle routes to wrap | fix now | @ e6a8e5d (cycle 2) |
| C1-2 | P1 | A receipt path in backticks never unblocks its operator ticket | fix now | @ f2bba2b (cycle 2) |
| C1-3 | P1 | Eight guards in the new next-step.py have no failing test | fix now | @ 0762b64 (cycle 2) |
| C1-4 | P2 | A P0 fix on the operator lane reports `approval: auto` | fix now | @ 6e87503 (cycle 2) |
| C1-5 | P2 | A run parked after planning resumes at `workflow plan` | fix now | @ 08048cb (cycle 2) |
| C1-6 | P3 | Three minor items | defer — stays in review.md; text in git at `ae08347` | settled (cycle 2) |

## Cycle 2 findings
### P1 — C2-1 · The blocker names a resolved finding once earlier ones fold into `## Resolved`
- Evidence: a regression from the C1-1 fix. next-step.py:169 now reads every cycle, and `review_findings` (check-run.py:532-548) numbers each cycle's `###` sections by position. Folding settled findings into `## Resolved` (phase-4-review.md, re-review) shifts the positions. Input: this repo's own run-worktrees review at 68cbf30, where C2-1 is stamped in `## Resolved` and C2-2 stays open → `blocker.action` "Resolve C2-1, C3-1 before continuing.", Why "Patch cycle 3 · fix C2-1, C3-1". C2-2 is the open one. The card and the `workflow status` line both ask for the wrong finding.
- Remedy: number a cycle's sections with the ids its `## Resolved` rows do not hold, or read an id at the start of the title (`### P2 — C2-2 · …`, as run-worktrees and checkup-next-actions write it), with a test for each.
- Disposition: fix now
- Resolved: —

### P1 — C2-2 · Wrap's open-finding gate in check-run has no failing test
- Evidence: C1-T1 moved `check_review` onto the shared predicate (check-run.py:589 `if open_finding(f):`), and wrap's precondition reads its note (wrap.md:20, "no open `fix now` finding"). The ticket's proof for that side was "test_check_run.py passes unchanged", but no test asserts the note. `if not open_finding(f)` and `if False` both leave test_check_run.py and test_next_step.py green; the first crashes on `sha.group(1)` for an open finding, the second reports "no open `fix now` finding" for every run. A surviving mutation on a line the fix changed.
- Remedy: one test_check_run.py case, about 10 lines: a cycle 1 `fix now` finding with `Resolved: —` gives "1 open `fix now` finding"; stamped `@ <sha>` gives "no open `fix now` finding".
- Disposition: fix now
- Resolved: —

### P3 — C2-3 · Four minor items
- A P0 patch ticket with no `Lane:` now crashes with an IndexError traceback (next-step.py:133, `lane.split()[0]`). Before C1-T4 it printed a `fix:P0` card. check-run.py:303-304 errors on the missing Lane first, so a committed patch plan cannot reach it, and a non-P0 ticket already crashed the same way (:129).
- No test covers the parked card's Why, "The run is parked." (next-step.py:196). Without it the card shows the pending step's Why.
- `check_review` still searches the Resolved line for a sha itself (check-run.py:587-588), next to `open_finding`, which runs the same search. One helper that returns the sha would serve both.
- SKILL-IMPACT.md:13-15 adds a trialing row for each of C1-T1, C1-T2 and C1-T3, so one unwrapped run has five rows. checkup-next-actions C1-6 was the same pattern. Wrap folds them into one.
- Disposition: defer — stays in review.md
- Resolved: —

## Pre-existing / environmental
- The installed workflow skill this session loaded still carries an older next-step.py and check-run.py. It catches up only after `npx skills update -g` (AGENTS.md).

## Cycle 2 verdict
The five cycle 1 fixes work. Each red test fails at its own commit and passes after a fix that leaves the tests untouched, and all eight C1-3 mutations now fail the suite. Two new P1s sit in the C1-1 fix. The blocker numbers finding ids by position, so it names a resolved finding once earlier ones fold into `## Resolved` (C2-1). The check-run side of the shared predicate, which wrap reads, has no test (C2-2). This is the cycle bound, so both go to the human as one decision: a third cycle, or defer to `TODO.md`. C2-3 stays here.
