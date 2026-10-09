Command: workflow review run-sizing
Created: 2026-10-10
Base:    38dea5df6e9017b0ef36d863fa457ab53206defd
Inputs:  .workflow/run-sizing/patch_plan.md @ e1bc18b8792c33efbb8c8930b3914c8c012e4f28
Status:  complete

## Scope and checks
- Patch range: `e1bc18b..38dea5d`; C1-T1 is `36b844d`, C1-T2 is `69370a6`.
- `python3 -m unittest discover -s .github/skills/workflow/scripts/tests -v`: 31 tests pass, exit 0.
- AST comparison against `e1bc18b`: all 37 assertions in 30 existing tests are unchanged; one boundary test is added.
- `git diff 36b844d..69370a6 -- .github/skills/workflow/scripts/tests`: empty. The document fix leaves tests untouched.
- `git diff --numstat 1dfb679..HEAD -- . ':(exclude).workflow'`: +27/-5 code, +51/-2 tests; net +71 excluding Markdown/text.
- Added escape-hatch scan: no hits. No touched file exceeds 1,000 lines.
- Repository scan excluding `.git`, `.workflow`, `understand`, Markdown/text and bytecode: no `.workflow/` references.
- Input freshness: all changes to the patch's named files are its two ticket commits. No new production file or guard.

## Independent mutation
Temporary detached worktree: `/private/tmp/j-skills-run-sizing-c2` at `38dea5d`; removed after restoring and checking it clean.
At `.github/skills/workflow/scripts/check-run.py:300`, change `len(accepts) <= ACCEPT_MAX` to `< ACCEPT_MAX`.
`python3 -m unittest discover -s .github/skills/workflow/scripts/tests -k six_acceptance -v` fails, exit 1.
The assertion sees `T1: 6 acceptance lines; a ticket has 1-6` and `1 errors`, instead of `· 0 errors`.
Restore the source; `-k Sizing -v` passes all four tests, exit 0. This includes seven-line rejection.

## Session trace
Read execute in full, wrap's counting and cleanup steps, and all session references in workflow/checkup.
- Execute: `references/phase-3-execute.md:67` explicitly puts normal and patch sessions in plan.md; lines 68–70 preserve entries and numbering.
- Wrap: `references/wrap.md:139` counts that ledger before step 9a removes it; line 141 explicitly includes patch sessions.
- Consumer: `references/learning-worklog.md:106` records the count; checkup reads the Run line at `SKILL.md:206`.
- Manual trace: initial execution adds Session 1 to plan.md; patch cycle 1 adds Session 2 there; replacement patch cycle 2 adds Session 3 there.
- Replacing patch_plan.md removes none of those entries. Wrap counts 3 before cleanup. This is a document walkthrough, not three live runs.
- The actual run's plan.md has Session 1 for T1–T3 and Session 2 for C1-T1/C1-T2: count 2.
- Both patch Verify phrases occur exactly once. Ticket status and commit records remain in the active plan.

No new finding was confirmed. Prior findings are resolved in review.md.
