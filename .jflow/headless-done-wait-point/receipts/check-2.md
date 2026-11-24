# check-2 @ f42dfb265f3bc88c13256007b1a56a2a6310e14a · GPT-6.2 Sol · high

| # | Verdict | Evidence |
|---|---|---|
| 1 | BROKEN | defect 1 |
| 2 | PROVED | `python3 .jflow/headless-done-wait-point/drive.py 2` → approach, gate, done and edits typed. Cap, BLOCKED, edge-only and build omit wait_point |
| 3 | BROKEN | defect 2 |
| 4 | PROVED | `python3 .jflow/headless-done-wait-point/drive.py 4` → stub gh routes edits to the human, then done in the builder session |
| 5 | PROVED | `grep -n -e 'Proposed edits' -e 'Yes: edits' -e wait_point .github/skills/jflow/{SKILL.md,references/done.md}` → steps 3 to 8 wait, since `next` waits for `Yes: edits`. |
| 6 | PROVED | `python3 -m unittest discover -s .github/skills/jflow/scripts/tests -p test_validate.py` → 14 tests OK, including historical output and byte caps |

## Defects

- 1. [use] jflow.py next_step: After a re-spec, replace the proposal under its existing heading, keep the PRODUCT.md edit, and revise the TODO.md edit. The blocker omits the retained edit. It should show both edits for approval. Evidence: run, `python3 .jflow/headless-done-wait-point/drive.py retain-edit-after-respec` → Revised blocker shows - TODO.md: keep the demo item and mark it finished
- 2. [use] jflow.py next_step: After a re-spec, copy an old proposal bullet under `## Deferred` to explain why it remains open. The old proposal triggers an edits stop. The run should go to done until the builder posts a new proposal. Evidence: run, `python3 .jflow/headless-done-wait-point/drive.py repeat-old-edit-in-note` → Deferred note returned human with wait_point=edits

## Maybes

- <none>
