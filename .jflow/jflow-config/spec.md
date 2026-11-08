# jflow-config
Status: done
Base: bc5d3cb

## Problem
The jflow seat table lives in SKILL.md prose, so a model change edits the skill, and
conductor (roadmap item 1.5) and hq (item 2.5) have nothing to read seats from. The work
laptop needs its own model list without forking the skill. Roadmap item 1.1 in hq
docs/jflow-standalone-and-hq-roadmap.md. Build waits for the trial verdict, no earlier than
2026-11-14.

## Goals
1. `jflow.py seat <step>` prints the step's model, vendor, effort and fallback as JSON. A
   session's closing card and the conductor read seats from it, not from SKILL.md.
2. Seats come from `--config FILE` or `$JFLOW_CONFIG`, then the repo's `.jflow/config.json`,
   then the skill's defaults, merged seat by seat.
3. Defaults: spec, build and done on Opus 5.5 · medium; check on GPT-6.1 Sol · high, with
   Astra (`gpt-6-astra` · high) as its named fallback. A seat with no fallback says null.
4. When builder and checker resolve to one vendor, `seat check` returns the checker's named
   other-vendor seat, Opus 5.5 · high by default. Config can turn this off.
5. The three locked rules are fixed in the script, printed by `seat`, and a config that tries
   to change one is refused.
6. A config value or a `record` argument that looks like a secret is refused.
7. `flow.json` lists the steps with each step's role, session and skill, and the script reads
   its steps from it.

## Non-goals
- No `next` command, no `validate`, no preconditions, wait points or check cap in flow.json:
  those come with items 1.2 to 1.4.
- No changes to hq or conductor. No Jev.
- No "high stakes" or other task taxonomy. Raising effort for one run is a different config.
- No change to `record` beyond the secret check. No change to any seat's model.

## Constraints
- Must not break: `record` and `summary` as they work today, Python 3.9 standard library, the
  skill under 50 KB.
- Ask first: the config.json shape, `{"schema_version": 1, "seats": {...}}` with per-seat
  model, vendor, effort and fallback, is a contract hq and conductor will read. Any change
  to it after this spec.
- Gate: none.

## Proof
| # | Claim | Surface | Check | Pass signal | Kind | Base |
|---|---|---|---|---|---|---|
| 1 | Goals 1, 3 | CLI | In a repo with no config: `jflow.py seat` for spec, build, fix, done and check | JSON per step: Opus 5.5 medium with fallback null for spec/build/fix/done; Sol high with Astra high fallback for check | new | red |
| 2 | Goal 2 | CLI | Repo `.jflow/config.json` sets builder; `$JFLOW_CONFIG` sets checker; then also pass `--config` setting checker differently | build from the repo file, check from env, spec from defaults; with `--config`, check from the flag | new | red |
| 3 | Goal 2, failure | CLI | Repo `.jflow/config.json` is broken JSON, then has an unknown seat field type such as effort 5 | `seat` exits non-zero with one error line naming the file; it never prints a default seat | new | red |
| 4 | Goal 4 | CLI | Config with builder on gpt-6.1-sol, then the same with the vendor rule turned off | First: `seat check` gives Opus 5.5 high. Second: Sol | new | red |
| 5 | Goal 5 | CLI | `seat build` output; then a config that tries to turn off each locked rule, using the names SKILL.md documents | Output lists the three rules; each bad config exits non-zero naming the rule, prints no seat | new | red |
| 6 | Goal 6 | CLI | Config with a value like `sk-ant-…`, `ghp_…`, `AKIA…`, or a 40-char random string; `record <slug> spec --model ghp_…` in a temp repo | Each exits non-zero; the value is not echoed; run.jsonl is unchanged | new | red |
| 7 | Goal 7 | CLI + file | Read flow.json; `seat` each step it lists; `seat bogus` | Every listed step resolves, its role matches flow.json; `bogus` exits non-zero | new | red |
| 8 | Goal 1 | SKILL.md, references | `grep -n "claude-opus-5.5\|gpt-6.1-sol\|Opus 5.5 · high" .github/skills/jflow/SKILL.md .github/skills/jflow/references/*.md` | No seat values remain; SKILL.md tells the session to run `jflow.py seat` for the card | new | red |
| 9 | Must not break | CLI | Under Python 3.9 (`uv python find 3.9`): jflow test suite, then `record` and `summary` on a temp run | Tests OK; record and summary output unchanged in shape | keep | green |
| 10 | Budget | files | `git diff --numstat bc5d3cb -- .github/skills/jflow/scripts/jflow.py`; size of the skill folder without `__pycache__` | jflow.py net growth ≤ 90 lines; skill ≤ 50 KB (38,683 bytes today) | keep | green |

## Human checks
- none
