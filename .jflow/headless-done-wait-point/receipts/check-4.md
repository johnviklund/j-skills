# check-4 @ 0de041566c30f6a341e14ae018a07ead145f6153 · GPT-6.2 Sol · high

| # | Verdict | Evidence |
|---|---|---|
| 1 | PROVED | `python3 .jflow/headless-done-wait-point/drive.py 1` → edits shows both proposed lines, then done in the builder session |
| 2 | PROVED | `python3 .jflow/headless-done-wait-point/drive.py 2` → approach, gate, done and edits typed. Cap, BLOCKED, edge-only and build omit wait_point |
| 3 | BROKEN | defects 1 and 2 |
| 4 | PROVED | `python3 .jflow/headless-done-wait-point/drive.py 4` → stub gh routes edits to the human, then done in the builder session |
| 5 | PROVED | `rg -n -e 'Proposed edits' -e 'Yes: edits' -e wait_point .github/skills/jflow/{SKILL.md,references/done.md}` → steps 3 to 8 wait, since `next` waits for `Yes: edits`. |
| 6 | PROVED | `python3 -m unittest discover -s .github/skills/jflow/scripts/tests -p test_validate.py` → 14 tests OK, including historical output and byte caps |

## Defects

- 1. [use] jflow.py `next_step`. After re-spec and re-proof, the builder commits a cleanup of the obsolete proposal and approval, then commits a fresh proposal with the same edits. `next` returns `done`. The new proposal needs its own `edits` stop. Evidence: run, `python3 .jflow/headless-done-wait-point/drive.py repost-after-cleanup` → Reposted proposal returned done with wait_point=None
- 2. [use] jflow.py `next_step`. After re-spec and re-proof, the builder rewrites the proposal by removing a `TODO.md` edit and its stale approval, keeping the `PRODUCT.md` edit. `next` returns `done` instead of asking for approval of the remaining edit. Evidence: run, `python3 .jflow/headless-done-wait-point/drive.py trim-after-respec` → Shortened proposal returned done with wait_point=None

## Maybes

- <none>
