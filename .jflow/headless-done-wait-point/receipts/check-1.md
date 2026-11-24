# check-1 @ 8afa1381937ba8950a67680dbd7c889cc472dcf4 · GPT-6.2 Sol · high

| # | Verdict | Evidence |
|---|---|---|
| 1 | BROKEN | defect 1, defect 4 |
| 2 | PROVED | `python3 .jflow/headless-done-wait-point/drive.py 2` → approach, gate, done and edits typed. Cap, BLOCKED, edge-only and build omit wait_point |
| 3 | PROVED | `python3 .jflow/headless-done-wait-point/drive.py 3` → approvals are independent. Re-spec drops old edits and requires fresh approval for new edits |
| 4 | BROKEN | defect 2 |
| 5 | BROKEN | defect 3 |
| 6 | PROVED | `python3 -m unittest discover -s .github/skills/jflow/scripts/tests -p test_validate.py` → 14 tests OK, including historical output and byte caps |

## Defects

- 1. [use] jflow.py next_step: After a re-spec and clean check, replace the old proposal under its existing heading and remove its old approval. `next` returns `done`. It should show the new proposal and wait for approval. Evidence: run, `python3 .jflow/headless-done-wait-point/drive.py replace-after-respec` → Replacement after re-spec returned done with wait_point=None
- 2. [use] jflow.py next_step: A builder uses `jflow.py note` to post revised edits after the human chooses to change them. The blocker shows the original edits. It should show the revised proposal. Evidence: run, `python3 .jflow/headless-done-wait-point/drive.py github-replacement` → GitHub blocker shows - PRODUCT.md: mark the outcome reached, - TODO.md: remove the demo item
- 3. [use] references/done.md step 2: An unattended GitHub run follows the instruction to commit the proposed edits in `notes.md`. `next` rejects the branch. The instructions should use a notes comment in GitHub mode. Evidence: run, `python3 .jflow/headless-done-wait-point/drive.py github-done-instructions` → issue and pull request mode keeps no .jflow/ files on the branch: remove .jflow/42/notes.md
- 4. [edge] jflow.py next_step: Another invocation reads `next --json` after the builder writes `Yes: edits` but before committing it. `next` returns `done`. It should wait for the commit. Evidence: run, `python3 .jflow/headless-done-wait-point/drive.py uncommitted-approval` → Uncommitted approval returned done with wait_point=None

## Maybes

- <none>
