# jflow-next notes

- A human stop returns `step: "human"`, as row 2's pass signal lists it, with `model`, `command`
  and `session` null. No seat belongs to a human.
- The cap applies before `fix`, and before `check` only when code changed since the newest receipt.
  A check after `Live done:` only reruns WAITING rows, so it never counts and is never capped.
  `done` and `live` are never capped.
- A check counts toward the cap when code changed since the receipt before it, or since `Base` for
  check-1. An unknown sha counts, as `changed()` already treats it in `summary`.
- `## Accepted` closes an item only when the line starts with `Row N ·` or `Defect N ·` and ends
  with the newest receipt's sha. Fix for check-1 defects 1 and 2: matching the number anywhere in
  the prose, at any sha, let an old acceptance or a quoted row hide a new failure. SKILL.md now
  shows the `Defect N` form.
- check-1's `drive.py attack` asserts the old `done` result to reproduce the defects, so it now
  stops at that assert after printing `next=fix; expected=fix` for the first case. A scratch copy
  with those two asserts flipped to `fix` passes both cases. I left the checker's driver unedited.
- Defects marked `carried from check-N` stay open for `next`, unlike in `record`'s count, because a
  carried defect is still unfixed.
- `next` also takes `--config`, shared with `seat`, so both resolve the same seat.
- Row 1 replay: all 25 run commits of the three runs give the expected step, including the human
  stop from `3775002` through `1f0389c`.
