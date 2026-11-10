# jflow-validate
Status: ready
Base: d53d8d1

## Problem
jflow agents, and the conductor sessions that run them, write `spec.md`, receipts and `## Accepted`
lines by hand, and nothing checks their shape. `next` and `summary` read them with regexes and skip
lines that do not match, so a misspelled verdict, a missing row or a bad Accepted line silently
changes what `next` decides. At Base, `record check` on a receipt with `| 1 | NOPE | x |` exits 0.
Roadmap item 1.3 in https://github.com/johnviklund/hq/blob/main/docs/jflow-standalone-and-hq-roadmap.md.

## Goals
1. `jflow.py validate <slug> <step>` checks what that step just wrote: `spec.md` for `spec`, the
   newest receipt for `check`, the `## Accepted` lines for `accept`. It prints one line per problem,
   naming the file and row, and exits 1. Clean output prints nothing and exits 0.
2. `record` runs the same check for those three steps and refuses to write `run.jsonl` while any
   problem remains.
3. Every known-good output from the five recent runs passes unchanged.

## Non-goals
- Judging evidence quality or any other taste.
- Checking older receipts or `notes.md`.
- Changing `next`'s decisions, the templates, or the `build`, `fix`, `live` and `done` steps.
- A `--fix` mode.

## Constraints
- Must not break: `next`, `summary` and `seat` output; Python 3.9, standard library only; the skill
  under about 50 KB.
- Ask first: nothing.
- Gate: none.

## Proof
| # | Claim | Surface | Check | Pass signal | Kind | Base |
|---|---|---|---|---|---|---|
| 1 | Known-good output passes | `jflow.py validate` | `validate spec` on drive-py-at-done, jflow-config, jflow-next, receipt-evidence-cap and wait-points; `validate check` on each of their 16 receipts as the newest, in a scratch copy | 21 of 21 exit 0 with no output, including wait-points row 7 with `\|` inside a code cell | new | red |
| 2 | Spec faults caught | `jflow.py validate` | one planted fault per scratch copy: Status not ready or done, unknown Base, missing section, missing Proof column, bad Kind, `new` row with Base green, `keep` row with Base red, missing Gate line | 8 of 8 exit 1, each line names the fault | new | red |
| 3 | Receipt faults caught | `jflow.py validate` | one planted fault per copy: header N not matching the file, unknown sha, missing row, extra row, bad verdict, Evidence cell of 241 characters, defect Evidence of 241, `defect K` with no defect K, ACCEPTED on a row not under Accepted, an extra section; then a cell of exactly 240 | 10 of 10 exit 1, each naming the file and row; the 240-character cell passes | new | red |
| 4 | Accepted faults caught | `jflow.py validate` | `validate accept` with an Accepted line missing its sha, one naming a row not in the Proof table, one with an unknown sha | 3 of 3 exit 1 | new | red |
| 5 | `record` refuses bad output | `jflow.py record` | `record check`, then `record spec`, on broken copies; then `record check` on a valid receipt | broken copies exit non-zero, print the problems, `run.jsonl` byte-identical; the valid receipt records as before | new | red |
| 6 | Other steps unaffected | `jflow.py record` | `record build` in a copy holding a broken receipt | exits 0 and writes the line | keep | green |
| 7 | `next` and `summary` unchanged | `jflow.py next`, `summary` | `next --json` and `summary --json` on the five runs, at HEAD and at Base | byte-identical | keep | green |
| 8 | Python 3.9 works | jflow test suite | `uv run --offline --no-project --python 3.9 python -m unittest discover -s .github/skills/jflow/scripts/tests` | OK | keep | green |
| 9 | Skill size | jflow skill files | bytes of the skill's tracked files, tests excluded | under 50000 (Base: 45404) | keep | green |
| 10 | Agents learn of it | `SKILL.md` | `grep -n validate .github/skills/jflow/SKILL.md` | one line saying `record` validates the spec, check and accept steps | new | red |

## Human checks
- none
