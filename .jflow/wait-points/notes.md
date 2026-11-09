# wait-points notes

- `next` reads the wait points from the spec's `- Ask first:` and `- Gate:` lines. A trailing period
  and the values `none` and `nothing` count as no wait point, because this run's own spec writes
  `- Gate: none.`
- The approach stop keys on a `## Approach` heading in `notes.md`. Before that heading exists,
  `next` says `build` with a fresh session, so the builder can write it.
- After `Yes: approach`, `next` gives `build` with session `builder`. `record` still writes every
  build as `fresh`, because the spec rules out changes to `record`. Open: a run that pauses for an
  approach counts one build session, the same as before.
- `Yes: done` clears the done stop for good. A Maybe that a later check adds after that line does
  not stop `next` again; done step 2 still shows it in chat. Open, if a stricter rule is wanted.
- The test is one table for rows 1 to 5. It uses a failure message instead of `subTest`, so test
  growth stays at the script's net growth: 27 lines each.
- Python 3.9 came from `uv run --python 3.9`, because this machine has no system 3.9.
