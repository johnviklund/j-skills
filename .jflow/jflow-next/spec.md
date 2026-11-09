# jflow-next
Status: done
Base: ecdfea7

## Problem
After every step, the session reads the prose "What is next" table in `SKILL.md` and works out the
next step by hand. A conductor can't read prose, so each step waits for the human to type the next
command. Roadmap item 1.2 in https://github.com/johnviklund/hq/blob/main/docs/jflow-standalone-and-hq-roadmap.md
asks for a script that decides the next step instead. It is the first step toward conductor driving
jflow, in item 1.5.

## Goals
1. `jflow.py next <slug> --json` prints the next step, read from the run folder and git, with its
   seat, role and session. It covers every row of today's table, including the stops for BLOCKED or
   UNREACHABLE rows and for the three-check cap. Those stops return `role: "human"` with a `blocker`.
2. The output shape is the roadmap's: `schema_version`, `slug`, `step`, `n`, `role`,
   `model {model, vendor, effort}`, `command`, `session`, `blocker`, plus `why`. `n` is the check
   number for a check and the receipt number for a fix. A run with `Status: done` returns
   `step: null` and `command: null`.
3. Without `--json`, `next` prints the closing card. Every step ends by running it, and the prose
   table leaves `SKILL.md`.
4. A `Checks allowed: N` line in `notes.md` raises the cap to N.
5. `--builder-vendor V` overrides the builder vendor, as it does for `seat`.

## Non-goals
- No change to conductor.
- No new wait points: the live gate, missing credentials, the Ask-first note and done's open items belong to 1.4.
- No `validate` command, which is 1.3.
- No change to the output of `record`, `summary` or `seat`, or to the shape of `run.jsonl`.

## Constraints
- Must not break: `record`, `summary` and `seat` give the same output as at Base. Python 3.9 still works.
- Ask first: nothing.
- Gate: none.
- Budget: `jflow.py` grows by at most about 150 lines. Test growth is no larger than script growth.
  The files an agent reads, which are `SKILL.md`, `references/`, `flow.json`, `config.json` and
  `jflow.py`, stay at or under 50 KB. Tests don't count toward the 50 KB.

## Proof
| # | Claim | Surface | Check | Pass signal | Kind | Base |
|---|---|---|---|---|---|---|
| 1 | Goal 1, against saved good output | CLI on a worktree of each run commit | For every run commit of `drive-py-at-done`, `receipt-evidence-cap` and `jflow-config`, run HEAD's `next --json --repo <worktree>` | `step` equals the step of the following run commit. From jflow-config's check-3 at `3775002` through fix 4 at `1f0389c`, it is the cap stop: `role: "human"` with a blocker. The final done commits give `step: null` | new | red |
| 2 | Goal 1, every state | CLI on temp repos | One fixture for each state: no spec; drafting; ready with no code commit; code changed with no receipt; BROKEN or a defect; BLOCKED; UNREACHABLE; WAITING without `Live done:`; WAITING with it; all proved; `Status: done` | spec, spec, build, check, fix, human, human, live, check, done, null. Fix has session `builder` and a command naming the receipt path | new | red |
| 3 | "Changed" means code | CLI on temp repo | After a clean receipt, commit only `.jflow/` files, then commit a code file | `done` after the `.jflow/` commit, `check` after the code commit | new | red |
| 4 | Goals 1 and 4, cap | CLI on temp repo | Three checks that each follow a code change, with defects still open; a fourth receipt with no code change since the last; then `Checks allowed: 5` in `notes.md` | Human blocker at three. The rerun-only receipt doesn't count toward the cap. `Checks allowed: 5` gives `fix` | new | red |
| 5 | Goal 2, shape | CLI | `next --json` on every fixture from row 2 | Every key from Goal 2 is present. `model` equals `seat <step>`'s model, vendor and effort. `n` follows Goal 2 | new | red |
| 6 | Goal 3, card | CLI | `next <slug>` without `--json` on a check fixture and a fix fixture | First line is `Model: <model · effort>. Session: <…>.`, followed by a fenced block that holds exactly the JSON `command` | new | red |
| 7 | Goal 5 | CLI | `next --json --builder-vendor openai` on a check fixture | `model` is the `other_vendor` seat, which is anthropic | new | red |
| 8 | Bad input | CLI | `next ../x` | Exits non-zero with a "bad slug" message and writes nothing | new | red |
| 9 | Goal 3, docs | SKILL.md | `grep -n "What is next\|^\| no \`spec.md\`" SKILL.md`; `grep -n "jflow.py next" SKILL.md references/*.md` | The first grep finds no state table. The second shows that steps end by running `next` | new | red |
| 10 | Must not break | CLI | Under Python 3.9: the jflow test suite, `next --json` on a fixture, then `summary jflow-config --json`, `seat check` and `seat check --builder-vendor openai` | Tests OK. `next` runs. The other three outputs match Base byte for byte | keep | green |
| 11 | Budget | files | `git diff --numstat ecdfea7` on `jflow.py` and the tests; bytes of the files an agent reads | Script growth ≤ about 150 lines. Test growth ≤ script growth. Files an agent reads ≤ 50 KB, 36,591 bytes today | keep | green |

## Human checks
- none
