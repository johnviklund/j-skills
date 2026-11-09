# jflow-next notes

- A human stop returns `step: "human"`, as row 2's pass signal lists it, with `model`, `command`
  and `session` null. No seat belongs to a human.
- The cap applies before `fix`, and before `check` only when code changed since the newest receipt.
  A check after `Live done:` only reruns WAITING rows, so it never counts and is never capped.
  `done` and `live` are never capped.
- A check counts toward the cap when code changed since the receipt before it, or since `Base` for
  check-1. An unknown sha counts, as `changed()` already treats it in `summary`.
- `## Accepted` closes an item only when the line starts with `Row N ·` or `Defect N ·` and was
  committed in or after the commit that created the newest receipt; an uncommitted line counts as
  newer. A later receipt that still fails the item saw the acceptance, so the miss is new.
  check-1 defects 1 and 2 came from matching the number anywhere in the prose. check-2's defect
  came from my first fix keying on the receipt sha, which two receipts can share after live steps.
  Creation, not last touch, orders the receipt, so re-editing a receipt keeps its acceptance.
- The line's trailing sha stays in the template for the record; `next` no longer reads it.
- Defects marked `carried from check-N` stay open for `next`, unlike in `record`'s count, because a
  carried defect is still unfixed.
- `next` also takes `--config`, shared with `seat`, so both resolve the same seat.
- Row 1 replay: all 25 run commits of the three runs give the expected step, including the human
  stop from `3775002` through `1f0389c`.
