# check-scope
Status: ready
Base: 02f4d66
Serves: none

## Problem
Check took longer than build and fix together in 13 of 28 runs, 2,217 against 1,490 minutes, and
wrote 381 Maybes in 111 checks, 3.4 a check, each a stop for the human before done. Check also
decides instead of proving: one work-repo run had 5 cap raises, and in the three worst runs 12
checks found no defect and only moved BLOCKED or WAITING rows while the checker planned how to
unblock them. In this repo, jflow-next repeats one Maybe in all 5 receipts, and jflow-config's
Maybes are mostly fix proposals and status notes.

## Goals
1. Check proves and reports: it writes no plan to unblock a row, and never asks for or argues for
   more checks.
2. A Maybe is only a suspected defect with a named input the checker could neither run nor trace.
   Fix proposals, status notes, repeats of an earlier Maybe and reports of what a fix closed go.
3. `validate check` rejects a receipt when no commit landed after the previous receipt's commit,
   and rejects a receipt over 3,000 bytes.
4. `spec.md` says a row that grades a model's judgement runs on a fixed labelled case set the
   builder can run free, and a `keep` row needs no paid call and no approval and reads its values
   at check time.

## Non-goals
- Paid-call budgets and approval rules themselves.
- Why fix rounds keep finding new defects.
- Changing the existing rule that check lists each row's needs before running any.
- Rewriting old receipts.

## Constraints
- Must not break: the receipt template `jflow.py` parses; the newest receipt of every run that
  validates today; the 14,000-byte step and 30,000-byte script size caps; standard library only.
- Ask first: nothing.
- Gate: none.

## Proof
Rows 2 to 4 run in a scratch clone with the HEAD `jflow.py`, using jflow-size-room checked out at
the commit that added its `check-1.md`, and a `check-2.md` built from it.

| # | Claim | Surface | Check | Pass signal | Kind | Base |
|---|---|---|---|---|---|---|
| 1 | over the next five runs, the median falls below today's 3.5 checks a run, Maybes average under half of 3.4 a check, no check reruns rows when nothing was supplied since the last one, and every receipt stays under 3 KB | run folders | `jflow.py summary --json` and receipt sizes on the five runs after done | all four bars met | new | red |
| 2 | A check with no new input is refused | `validate` | add `check-2.md` at the same HEAD as check-1's commit, then `jflow.py validate jflow-size-room check` | exits non-zero and names the missing input | new | red |
| 3 | A check after new input is accepted | `validate` | as row 2, after a commit to `notes.md` | exits 0 | keep | green |
| 4 | An oversized receipt is refused | `validate` | as row 3, with `check-2.md` at 3,001 bytes, then at 3,000 | 3,001 fails, 3,000 exits 0 | new | red |
| 5 | Check writes no unblock plans or cap requests | `references/check.md` | read the BLOCKED verdict and the Route section | a BLOCKED row names only what is missing; cap and unblock decisions go to `next` and the human | new | red |
| 6 | Maybes hold one kind | `references/check.md` | read the Maybe rule | it matches Goal 2 and names the four kinds that go | new | red |
| 7 | The spec-side rules exist | `references/spec.md` | read the Proof table rules | both rules of Goal 4 are there | new | red |
| 8 | Old runs still validate | `validate` | `jflow.py validate <slug> check` for every run in `.jflow/` | the same 8 of 9 exit 0; corrections-bad-records already fails on its older receipts | keep | green |

## Human checks
- After five runs, read the row 1 measurement and judge whether check still catches real defects
  with fewer Maybes.

## Accepted
- Row 1 · Five post-shipping runs are still needed to measure the four bars · "option A" · 2026-11-17 · b9d49c8ac30b6831fa4d83458a1c4be5632f5726
- Defect 1 · A numbered list below a bare `Checks allowed:` heading can override the last complete cap line · "option A" · 2026-11-17 · b9d49c8ac30b6831fa4d83458a1c4be5632f5726
