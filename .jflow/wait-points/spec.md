# wait-points
Status: done
Base: 43121e6

## Problem
`jflow.py next --json` stops for the human only when rows are BLOCKED or UNREACHABLE and at the
check cap. The other wait points live in prose: the builder asks before the live gate and before an
Ask-first approach, and done asks about human checks and maybes. A conductor reads only the JSON, so
it would run straight past them. Roadmap item 1.4 in
https://github.com/johnviklund/hq/blob/main/docs/jflow-standalone-and-hq-roadmap.md asks for these
as blockers. It comes before item 1.5, conductor driving jflow.

## Goals
1. Each wait point is a stop for the human, in the 1.2 shape: `step: "human"`, `role: "human"`, a
   `blocker` that says what to decide, and null `model`, `command` and `session`. The card says the
   same.
2. A yes is one line in `notes.md`, `Yes: <point> · "<the human's words>" · <date>`, committed by the
   session the human answered. A line counts only when it starts with `Yes: <point>`. It clears that
   point and no other.
3. Live gate: the spec names a `Gate:`, only WAITING rows are left, and `notes.md` has neither
   `Live done:` nor `Yes: gate`. Then `next` stops and the blocker names the gate. After the yes,
   `live` runs as today.
4. Ask first: the spec's `Ask first:` is not "nothing" and no code changed since Base. Build writes
   `## Approach` in `notes.md`, commits only that, and stops. `next` then stops until `Yes: approach`
   appears. After that, `build` runs in the builder session.
5. Done: the spec's Human checks are not "none", or the newest receipt has Maybes. Then `next` stops
   before done until `Yes: done` appears. With that line present, done skips its own wait.

## Non-goals
- No missing-credential code. Check asks in chat. A row it cannot run is BLOCKED, which `next`
  already stops on, and a rerun of BLOCKED rows does not count toward the cap.
- No `needs-human` label and no public-or-paid judgement: that belongs to hq.
- No count of open items in `notes.md`: they are free text, and done still shows them in chat.
- No change to conductor, `record`, `summary`, `seat`, or the shape of `run.jsonl`.

## Constraints
- Must not break: the stops 1.2 added, the cap, and a run with no wait points, which goes from spec
  to done with no stop. `record`, `summary` and `seat` give the same output as at Base. Python 3.9
  still works.
- Ask first: nothing.
- Gate: none.
- Budget: `jflow.py` grows by about 30 lines. Test growth is no larger than script growth. The
  files an agent reads, which are `SKILL.md`, `references/`, `flow.json`, `config.json` and
  `jflow.py`, stay at or under 50 KB. They are 43,078 bytes today.

## Proof
| # | Claim | Surface | Check | Pass signal | Kind | Base |
|---|---|---|---|---|---|---|
| 1 | Goals 1 and 3 | CLI on temp repo | `Gate: publish the release to npm`, check-1 with rows PROVED and WAITING; `next --json` and `next`; then commit `Yes: gate · "go" · <date>` and run again | Human stop, and the blocker contains the gate text. The card starts `The human decides:`. After the yes: `live`, builder | new | red |
| 2 | Goal 4 | CLI on temp repo | `Ask first: the config.json shape`, no code commit; then commit `## Approach` in notes; then add `Yes: approach` | `build` fresh, then a human stop that names the approach, then `build` with session `builder` | new | red |
| 3 | Goal 5, human checks | CLI on temp repo | All rows PROVED, Human checks `- try it on the laptop`; then add `Yes: done` | Human stop that names the human checks, then `done` | new | red |
| 4 | Goal 5, maybes | CLI on temp repo | All rows PROVED, Human checks none, receipt Maybes `- slow on big repos`; then add `Yes: done` | Human stop that names the maybes, then `done` | new | red |
| 5 | Goal 2, only its own point | CLI on temp repo | Row 2's approach state, with notes holding `Yes: gate`, `Yes: done` and `- the human said Yes: approach` | Still the human stop for the approach | new | red |
| 6 | No false stops | CLI on temp repos | Ask first nothing, Gate none, no human checks or maybes: ready, built, proved. Also BROKEN with human checks, and WAITING with `Live done:` | `build`, `check`, `done`, `fix`, `check`: no human stop | keep | green |
| 7 | Docs | skill files | `grep -n "Yes: \(gate\|approach\|done\)" SKILL.md references/*.md` | `SKILL.md` defines the `Yes:` line. `build.md` has the approach stop and `done.md` skips its wait on `Yes: done` | new | red |
| 8 | Must not break | CLI | Under Python 3.9: the jflow test suite; then `summary jflow-config --json`, `seat check` and `seat check --builder-vendor openai` | Tests OK. The three outputs match Base byte for byte | keep | green |
| 9 | Budget | files | `git diff --numstat 43121e6` on `jflow.py` and the tests; bytes of the files an agent reads | Script growth about 30 lines. Test growth no larger than script growth. Files an agent reads at or under 50 KB | keep | green |

## Human checks
- Mark item 1.4 in the hq roadmap. The missing credential is covered by BLOCKED rows, not by new code.
