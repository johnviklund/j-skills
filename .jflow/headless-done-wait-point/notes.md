# headless-done-wait-point notes

## Build

- `## Proposed edits` and `Yes: edits` are read from the same post-re-spec notes text as the other
  `Yes:` lines, so a mid-run `jflow spec` voids both with no extra code.
- The `edits` stop comes after the `done` stop. With Human checks and proposed edits, the human
  answers `Yes: done` first, then `Yes: edits`. Each `Yes:` clears only its own point.
- The blocker lists only the `- ` lines under `## Proposed edits`. `done.md` tells the unattended
  done to write one `- ` line per edit, so prose under the heading is not shown.
- `wait_point` is added to the `next --json` dict only at a wait point, so every other output keeps
  its old keys and the historical runs stay byte for byte.
- Issue and pull request mode needed no code: `jflow_gh.py` replays the notes comments into a
  `notes.md` and runs the same `next_step`. The shared story test now also compares `wait_point`.
- `SKILL.md` plus `check.md` was at 13,917 of 14,000 bytes. To fit the new text I rewrote the wait
  points paragraph shorter and dropped "live" before `Gate:`. The total is now 13,997.
- `SKILL.md` used to say a re-spec needs fresh `Yes: approach` and `Yes: gate`. The code already
  voided every `Yes:` line, `Yes: done` included, so the text now says "earlier `Yes:` lines".
- Open: `done` decides for itself whether it runs unattended. The follow-up `conductor` run has to
  tell it so in the prompt it sends, and read `wait_point` instead of the blocker text.
