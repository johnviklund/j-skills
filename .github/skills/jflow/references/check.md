# jflow check

You are the **checker**, on a different vendor from the builder, and you judge the change against
`spec.md`. Change no product code, and clean up anything you start. Skip the
repo's full build, test and lint commands, even when `AGENTS.md` asks for them;
`jflow done` runs them. Do both passes, in order. Read `notes.md` only after your findings are
drafted, so the builder's reasoning does not shape what you see.

Check the key first: `git log --oneline <Base>..HEAD -- .jflow/<slug>/spec.md` must show only the
spec's own commits, including any `jflow accept` commit that touches only `## Accepted`. A change
the human did not confirm is BLOCKED, and the check stops there.

Before running anything, check every credential, input and service the rows name. Ask the human
for what they can supply and wait: a missing value otherwise costs a whole check. Else that row is
BLOCKED.

## 1. Prove

Run each row exactly as written, at `HEAD`, on the real surface, using the repo's `verify-*` skill
for driven flows. With a `Gate:` in the spec and no `Live done:` line in `notes.md`, run nothing from
the gate on. Run only what a row names. A row that needs a driver reuses and extends
`.jflow/<slug>/drive.py`. Give each row one verdict
against its pass signal:

- **PROVED**: observed the pass signal.
- **BROKEN**: ran, and saw something else.
- **BLOCKED**: could not run: a missing credential, service or tool that no work in this folder can
  repair. Its evidence names only what is missing. Writing a driver is your job, so an unwritten
  driver is never BLOCKED.
- **UNREACHABLE**: the row's starting state is one the app never creates, so the code never runs.
- **WAITING**: Kind `live`, and the gate is not passed yet.
- **ACCEPTED**: listed under `## Accepted`, and you saw the miss that line describes. A row listed
  there that now passes is PROVED, and any other result is BROKEN.

A verdict rests on what you saw this session, with one exception: when neither code nor `spec.md`
changed since the last receipt, `## Accepted` aside, rerun only its BLOCKED and WAITING rows, plus
every `keep` row once `Live done:` is new, since live steps change what those rows stand on. Carry
its other verdicts over, with `carried from check-N` as their evidence. When a row cannot be run, it is BLOCKED, even if a weaker
check would pass.

## 2. Attack

Green rows say nothing about what the table never asked. Read `spec.md`, then `git diff <Base>..HEAD`, and the code
around it. Go for what no row varies: shapes the rows did not try, what runs upstream of where a row
begins, and what the output leaves a reader believing after filtering or defaulting. On a later
check, attack only what changed since the last one.

Run `python3 <skill>/scripts/jflow.py checklist <slug>`. It prints the repo's `RELIABILITY.md`
items that this diff triggers. Do each item's check; a failed one is a defect like any other.

Report a defect only with a concrete failing input, one the service, a user or a caller can send,
and name how it arrives.
Run it in a scratch copy when you can, so the output is the evidence; otherwise trace it through
the code and say so. A defect that breaks a row's claim also makes that row BROKEN.

When one pattern repeats, report it once as a class: one concrete failing input, plus where else
the same pattern appears, so the builder fixes every instance in one pass.

Once your findings are drafted, read `notes.md` and, in issue mode, the pull request comments.
Drop a defect from an earlier receipt that was fixed, or that the builder answered with evidence,
unless the new diff broke it again or the answer is wrong.

Tag each defect by how its input arrives. `[use]`: normal work on this repo makes it. `[edge]`: a
caller could send it, but normal work does not, such as a CRLF receipt, a non-UTF-8 or git-quoted
non-ASCII filename, custom git diff config, or a rare grammar corner of a heuristic matcher.
Report every defect either way. When every open defect is `[edge]`, and BROKEN rows cite only those, `next`
asks the human to accept or fix them.

Leave out style, structure, a missing test or surviving mutant on its own, duplication, and risks
that need a future change to matter. No defects is a valid result.

A **Maybe** is only a suspected defect with a named input you could neither run nor trace. It goes
to the human; nobody fixes it. Never a Maybe: fix proposals, status notes, repeats of
a Maybe from an earlier receipt, and reports of what a fix closed. Measured 2026-11-17: 381 Maybes
in 111 checks, each a stop before done.

## Write `receipts/check-N.md`

One number up from the last receipt. Use this template exactly, with no added sections: a limit on
the check goes in the evidence of the row it stops. Each Evidence cell holds at most 240
characters: the command plus the one output line that decides the verdict. A BROKEN row with a defect cites its number; without
one, it uses the capped command and output line.
Number defects; each defect's `Evidence:` part also holds at most 240 characters.
Quote a command that reruns as written; raw output stays in the temp
folder. Done when every row has a verdict and evidence, every defect its input and evidence, both
caps hold, and the receipt is at most 3,000 bytes. `validate` refuses a larger
receipt, and one with only receipts and `run.jsonl` committed since the previous receipt.

```markdown
# check-N @ <sha> · <model and effort from the card, or unknown>
| # | Verdict | Evidence |
|---|---|---|
| 1 | PROVED | `<command>` → <decisive output line> |
| 2 | BROKEN | defect 1 |
| 3 | BROKEN | `<command>` → <decisive output line; no defect> |

## Defects
- 1. [use] <file and symbol>: <input> → <what happens> → <what should happen>. Evidence: <run or traced>, `<command>` → <decisive output line>

## Maybes
- <none, or for the human only>
```

## Route

Record the step as `check`, commit, and print the `jflow.py next <slug>` card. The check ends there, even when the card says `done`. To any later message about
this run, print the card again and do nothing else: decisions, `## Accepted` and done belong to
the builder session. BROKEN rows and defects go to the
builder in one fix. BLOCKED and UNREACHABLE rows do not, since no fix reaches them. Name what each
BLOCKED row is missing and stop: `next` and the human decide what follows, the check cap included.
Never plan how to unblock a row or argue for more checks. For UNREACHABLE, the human chooses between deleting the code and saying what reaches it. With only
WAITING rows left, say the change is clear to pass the gate.

## Issue and pull request mode

On `jflow/<issue>`, read the spec in the issue's comments and no pull request comment until your
findings are drafted. `next` refuses a changed spec: skip the
key check. Keep `drive.py` in `.git/jflow/<issue>/`. Post the receipt: `record <slug> check --file F`.
