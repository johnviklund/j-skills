---
name: evals
description: >
  The evals.run and evals.list commands; load this skill to run either. A recall check for
  strict-reviewer candidates and for changes to the review instructions: "evals.run reviewer
  [vendor model effort]" shows the candidate each case in the private exam set (at most 10
  diffs with planted or missed P0/P1s, each with a clean twin), then records which defects it
  named and how many false alarms it raised on the clean twins. "evals.list" shows the set's
  status. No other seat is examined: models earn every other seat on trial runs recorded in
  WORKLOG.md. Run only on an explicit "evals.run ..." or "evals.list" message; never on casual
  mentions of evals or testing. Never edits the workflow skill or product code.
---

# evals

One exam, one seat. A reviewer miss is the expensive kind, and a diff with a known defect is a
cheap, honest exam of exactly that. Every other seat (brainstorm, plan, execution lanes) is
judged on trial runs: the worklog's `Run:`/`Seats:` lines, compared by `checkup`.

Run it before giving a new model the strict-reviewer seat, and before keeping a change to
`workflow/references/phase-4-review.md` (same model, old and new instructions). The human
invokes it.

## The exam set

One central set for every repo, in the private repo `j-skills-evals`, cloned beside the j-skills
clone. Find it with `git -C <this skill's folder> rev-parse --show-toplevel`, then `../j-skills-evals/strict-reviewer/`.
Missing → stop and give the human the clone command:
`gh repo clone johnviklund/j-skills-evals <j-skills root>/../j-skills-evals`. The set is private
because cases copy code from private repos; never copy a case into a public repo.

Each case is one file, `strict-reviewer/<kind>-<topic>.md`, in this exact shape (scripts and
this skill parse it):

```markdown
# <title: the defect, as a user would meet it>
Kind: missed | seeded
Source: <repo> · run <slug> · <base>..<head>
Added: <date> · missed by <model> | planted by <model>

## Context
<2-6 lines: what the change is meant to do, the behaviours a reviewer needs>

## Diff
```diff
<the diff the candidate reviews, self-contained>
```

## Clean diff
<one line on what it is> + a fenced diff, or `none`

## Must name
- <P0|P1> · <file and symbol> · <the defect in one line>
```

- **missed:** a real P0/P1 that a writer or reviewer missed, deposited by `workflow wrap`. The
  clean diff is the change with the fix applied, when one exists. These outrank seeded cases.
- **seeded:** a shipped, reviewed diff with one realistic slip planted on one added line (an
  off-by-one, a flipped comparison, a stale constant). The shipped diff is the clean twin. They
  make the exam runnable before any real miss exists; the generator that built them is in
  `scripts/` so they can be rebuilt.
- **Cap: 10, rolling.** When full, a new missed case displaces the oldest seeded case first,
  then the weakest missed one.

## Commands

- `evals.run reviewer [<vendor> <model> <effort>]`: ask for the candidate if not given. For a
  review-instruction change, the candidate is the incumbent twice: once with `phase-4-review.md`
  at `HEAD`, once at the change's parent commit.
- `evals.list`: read-only. Cases by kind, any that break the shape above, the last result.

## Procedure: `evals.run reviewer`

**1. Preflight.** Load the set. A case missing its diff or its `## Must name` lines is skipped
and flagged, never fails the run. Fewer than 3 usable cases: say the exam is not meaningful and
stop. State the bill: one candidate call per diff (planted plus each clean twin), at the
reviewer seat's review effort, no grader model. Confirm with the human.

**2. Run the candidate, one diff per fresh context.** Give it the case's `## Context`, one diff,
and the review instructions from the `workflow` skill (`references/phase-4-review.md`), at the
seat's review effort. Never show it `## Must name`, the case's `Kind`, or that a clean twin exists:
the planted and clean diffs of one case go to separate fresh contexts, in random order. Capture
its findings verbatim, plus tokens and latency where the CLI reports them. One retry on a
mechanical failure; a second failure scores that diff as missed.

**3. Score, no grader model.** Two numbers, kept apart:

- **Recall:** per `## Must name` line, did the candidate name that defect on the planted diff, at
  P0 or P1? A matching defect at the wrong one of those two severities still counts. Recall =
  named ÷ planted, reported for missed and seeded cases separately.
- **False alarms:** each P0/P1 it raised on a clean diff. Show each to the human: a false alarm
  costs a patch cycle, but a real defect in shipped code is a find. A real one becomes a new
  `missed` case (missed by the original review), never a penalty.

Present one table: case → planted defect → the candidate's matching line or "—" → its P0/P1s on
the clean twin. Matching is a short human read, and the human's mark is final.

**4. Record.** Append one block to `strict-reviewer/RESULTS.md` in the exam set: date, candidate
(vendor · model · effort) or instruction change (commit), recall N/M (missed · seeded), false
alarms N on K clean diffs, per-case misses, cost and latency, one-line verdict. Commit and push
in `j-skills-evals`. No routing proposal: the human edits `ROUTING.md` if the numbers convince
them, and only full recall with no false alarm on a set of 3 or more cases should.

## Ground rules

- **Writes only `RESULTS.md`, and new `missed` cases the human confirmed in step 3.** Never
  edits other cases, the workflow skill, or code.
- **Bounded.** At most 10 cases, one seat, one candidate per invocation.
- **Provenance.** Exact model and effort, never a family name.
