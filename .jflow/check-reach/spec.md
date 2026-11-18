# check-reach
Status: ready
Base: 94f20b2
Serves: none

## Problem
A defect in a check receipt always sends the run to a fix round and another check, however unlikely
its input. In check-scope the gpt-6.2-sol checker raised 10 defects in 5 checks; 6 used inputs
normal work never makes (a CRLF receipt, a merge commit, a `git mv` into a run folder, a UTF-16
receipt, a non-UTF-8 filename, a heading over a list). Checks 2 and 3 found only those, and each
cost a fix round: 5 checks, 12.2 hours, a cap raise. The 2026-11-17 reviewer exam shows the same
pattern: 9 to 11 traced but exotic P0/P1s on 10 clean diffs.

## Goals
1. Each defect is tagged `[use]` (normal work produces the input) or `[edge]` (a caller could send
   it, but normal work does not). The checker still reports every defect.
2. When every open defect is `[edge]` and no row is BROKEN, `next` stops for the human:
   A (recommended) accept them all under `## Accepted`, B run a fix round.
3. A `[use]` defect, an untagged defect or a BROKEN row still routes to fix, as today.
4. `validate` refuses a tag other than `[use]` or `[edge]`; an untagged defect still validates.

## Non-goals
- Changing the cap rules, the Maybe rule or the attack rule.
- Rewriting old receipts.
- Filtering edge defects out before the human sees them.

## Constraints
- Must not break: old runs that validate today; the receipt template `jflow.py` parses; the
  30,000-byte script cap (`jflow.py` is at 29,927, so the builder makes room in existing code);
  standard library only.
- Ask first: nothing.
- Gate: none.

## Proof
Rows 1 to 5 run in a scratch clone at `b5b2e13`, with `Checks allowed: 9` added to check-scope's
`notes.md` and its `check-4.md` edited as each row says, with the HEAD `jflow.py`.

| # | Claim | Surface | Check | Pass signal | Kind | Base |
|---|---|---|---|---|---|---|
| 1 | Edge-only defects stop for the human | `next` | tag defect 1 `[edge]`, commit, `jflow.py next check-scope --json` | step `human`; the blocker names defect 1 and its first, ➡️ option accepts it | new | red |
| 2 | A `[use]` defect routes to fix | `next` | as row 1, tagged `[use]` | step `fix` | keep | green |
| 3 | An edge defect with a BROKEN row routes to fix | `next` | as row 1, with row 3 `BROKEN` citing defect 1 | step `fix` | keep | green |
| 4 | An untagged defect routes to fix | `next` | as row 1, the receipt as committed | step `fix` | keep | green |
| 5 | `validate` refuses an unknown tag | `validate` | tag defect 1 `[odd]`, then `[use]`, then `[edge]`; `jflow.py validate check-scope check` | `[odd]` exits non-zero; `[use]` and `[edge]` exit 0 | new | red |
| 6 | The checker is told both tags | `references/check.md` | read the attack rule and the receipt template | both definitions are there and the template's defect line shows the tag | new | red |
| 7 | Old runs still validate | `validate` | `jflow.py validate <slug> check` for every run in `.jflow/` | the same 9 of 10 exit 0; corrections-bad-records already fails | keep | green |

## Human checks
- After five runs, judge whether edge-only stops replaced fix rounds without hiding a real bug.
