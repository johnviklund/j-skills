# jflow-next notes

Checks allowed: 5

- The human allows one more fix-and-check round after check-3, on 2026-11-09.
- At done, `summary` gave net code, tests and docs of +0: it found the done commit with
  `git log -S "Status: done"`, which also matched this spec's Goal 2 and row 2 text, and so ended
  the run at Base. The bug predates this run. The human chose option A on 2026-11-09: fix it here
  with `-G "^Status: done"`, which matches only the status line, and allow a fifth check.
  The test fixture spec now quotes `Status: done`. Three summary tests fail without the fix.
  `summary` for jflow-config, drive-py-at-done and receipt-evidence-cap is unchanged.

- A human stop returns `step: "human"`, as row 2's pass signal lists it, with `model`, `command`
  and `session` null. No seat belongs to a human.
- The cap applies before `fix`, and before `check` only when code changed since the newest receipt.
  A check after `Live done:` only reruns WAITING rows, so it never counts and is never capped.
  `done` and `live` are never capped.
- A check counts toward the cap when code changed since the receipt before it, or since `Base` for
  check-1. An unknown sha counts, as `changed()` already treats it in `summary`.
- `## Accepted` closes an item when the line starts with `Row N ·` or `Defect N ·`, ends with the
  sha of the check the verdict came from, and was committed in or after the commit that created
  that check's receipt. An uncommitted line counts as newer. A verdict whose evidence says
  `carried from check-N` came from check-N, followed back through earlier carries. Each of the
  five failing inputs from checks 1 to 3 breaks one of these parts: prose matching, an older
  acceptance, a new miss at the same sha, a carried miss, and an acceptance of other code. The
  test has one case for each, and fails with any one part removed.
- Creation, not last touch, orders the receipt, so re-editing a receipt keeps its acceptance.
- Defects marked `carried from check-N` stay open for `next`, unlike in `record`'s count, because a
  carried defect is still unfixed.
- `next` also takes `--config`, shared with `seat`, so both resolve the same seat.
- Row 1 replay: all 25 run commits of the three runs give the expected step, including the human
  stop from `3775002` through `1f0389c`.
