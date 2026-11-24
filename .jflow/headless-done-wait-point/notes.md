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

## Fix 1 (check-1)

- Defects 1 and 2 share a cause: `next` read the first `## Proposed edits` heading among the lines
  added since the re-spec. It now reads the newest `## Proposed edits` in the whole notes text and
  counts only the lines added since the last re-spec, both its `- ` lines and the `Yes: edits`
  line. A proposal rewritten under its old heading counts. A newer proposal posted after the first
  one replaces it in the blocker. `done.md` now says the newest proposal is the one that counts.
- Defect 4: `next` now reads `notes.md` from `HEAD`, so an uncommitted `Yes:` line clears no wait
  point. This applies to all four points, matching `SKILL.md`, where the session commits the line.
- Defect 3: the code is right to refuse `.jflow/42/notes.md` in GitHub mode, so the scenario
  `drive.py github-done-instructions` still fails by design. The fix is in `done.md`: in issue and
  pull request mode, an unattended done posts `## Proposed edits` with `jflow.py note`. `drive.py 4`
  already runs that path: "stub gh routes edits to the human, then done in the builder session".
- To stay under 30,000 bytes I shortened the new blocker and option texts. `jflow.py` is now
  29,987 bytes.

## Fix 2 (check-2)

- Defects 1 and 2 share a cause: fix 1 judged the proposal line by line, by whether each line was
  new since the re-spec. So a kept edit vanished from a revised proposal, and an old edit copied
  into `## Deferred` counted as new. `next` now judges the whole proposal: it compares the `- `
  lines of the newest `## Proposed edits` with those of the newest one before the re-spec. If they
  differ, it shows every line. A `Yes: edits` line counts when it sits under the newest heading and
  is new since the re-spec.
- Only the `- ` lines are compared, not the raw section. A `Yes: done` line appended under an
  unchanged proposal must not turn it into a new one; `drive.py 3` caught that in my first try.
- `jflow.py` is 29,989 bytes.
