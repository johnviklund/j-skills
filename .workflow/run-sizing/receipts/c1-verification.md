Command: workflow review run-sizing
Created: 2026-10-10
Base:    e1bc18b8792c33efbb8c8930b3914c8c012e4f28
Inputs:  .workflow/run-sizing/plan.md @ 1dfb679
Status:  complete

## Acceptance and regression
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s .github/skills/workflow/scripts/tests -v`: 30 tests pass, exit 0.
- T2's literal Verify command: 3 tests pass; phrase counts 4, 1, 1; old-rule counts 0, 0, 0.
- T3's literal Verify command: counts 4, 0, 4, 0, 1, 2, 1, 1, 1, 1, 1, 0, 2, matching the plan.
- Direct subprocess probes use the existing `plan`, `sized`, and `check` fixtures in `scripts/tests/test_check_run.py`.
- Six acceptance lines: 0 errors, 0 warnings. Seven: `T1: 7 acceptance lines; a ticket has 1-6`, 1 error.
- Budgets 20, 30, 30, 50: median 30, 1 merge warning. Budgets 60, 80, 80, 120: median 80, 0 warnings.
- AST assertion counts by existing test method: 24 methods, 28 assertions before and after; none changed.
- `git diff --numstat 1dfb679..e1bc18b -- . ':(exclude).workflow'`: code +27/-5, tests +47/-2; net +67 excluding markdown.
- Largest touched file: `check-run.py`, 697 lines. No touched file exceeds 1,000 lines.
- Escape-hatch scan of added lines: 0. Tracked source scan for `.workflow/`, excluding markdown, text, run folders, and understand output: 0.
- `git diff --check`: exit 0. Git history on named skill files contains only T1, T2, and T3 commits after the plan Base.

## Mutation checks
Temporary detached worktree: `/private/tmp/j-skills-run-sizing-review`, based on e1bc18b. No mutation is committed; each is restored afterward.

1. In `scripts/check-run.py:465`, replace `and not any(` with `and any(` in the cycle approval guard.
   Run `python3 -m unittest discover -s .github/skills/workflow/scripts/tests -k Cycle` from that worktree.
   Result: 3 tests run, 2 fail, exit 1. Both approved and unapproved cases detect the inversion.
2. At line 300, replace `ACCEPT_MIN <= len(accepts) <= ACCEPT_MAX` with `ACCEPT_MIN <= len(accepts) < ACCEPT_MAX`.
   Run the full suite from that worktree. Result: 30 tests pass, exit 0.
   Drive `plan(accept='a → b' + '\n- [ ] a → b' * 5)` through `check` with `BRIEF`.
   Result: `T1: 6 acceptance lines; a ticket has 1-6`, 1 error. This violates B4 while every test stays green.

## Session-count trace
The executor selects the active plan at `references/phase-3-execute.md:10` and records its session at line 67.
The wrap counter at `references/wrap.md:140` reads only the original plan.

| Input | Required total | Current wrap total |
|---|---|---|
| plan Session 1: T1; patch plan Session 1: C1-T1 | 2 | 1 |
| plan Session 1: T1; patch cycle 1 and patch cycle 2 each use another session | 3 | 1 |

These are document-instruction traces, not claims of having run separate executor sessions.
Keeping the ledger in the original plan avoids losing records when review replaces the patch plan or wrap deletes it.

## Patch Verify baselines
- `python3 -m unittest discover -s .github/skills/workflow/scripts/tests -k six_acceptance`: Ran 0 tests, OK.
- Neither `Session ledger: plan.md` in the execute reference nor `includes patch sessions` in the wrap reference exists.
