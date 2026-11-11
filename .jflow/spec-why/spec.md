# spec-why
Status: ready
Base: d6fad8b
Serves: Every change proved (hq PRODUCT.md)

## Problem
jflow spec starts from a one-line roadmap item that names a solution, so its grill asks how.
Of the 7 specs in j-skills, jflow-next, jflow-validate and wait-points give mostly a roadmap
pointer as their why. The Goals of jflow-config and drive-py-at-done name commands to write.
Nothing makes spec read PRODUCT.md or DESIGN.md, so a run can drift from the desired state
unnoticed, and check proves the solution got built, not that the problem went away. Measured at
Base on a test repo: given a fully filled roadmap item, a fresh spec session re-asked the option
the item had already chosen, and wrote no Serves line. Its Proof row 1 didn't match the item's
Solved when. Without an item, it asked no why question at all. Deleting workflow (hq item
delete-workflow, after this one) removes brainstorm and realign, the only steps that asked why.
Roadmap item spec-why in https://github.com/johnviklund/hq/blob/main/ROADMAP.md.

## Goals
1. A spec started from a roadmap item asks no why question the item already answers, names the
   PRODUCT.md outcome it serves, and its first Proof row proves the item's Solved when.
2. Spec reads the item, PRODUCT.md and DESIGN.md before the grill. With no item, the grill
   asks the why first: who has the problem, what they see, the evidence, why now.
3. spec.md carries `Serves: <outcome> | none` under `Base:`. When the repo has a PRODUCT.md,
   `validate`/`record spec` refuse a spec whose Serves is missing or names no `###` heading in it.
4. Done's closing line says whether row 1 passed. Before any edit to PRODUCT.md or DESIGN.md
   that the change calls for, done shows the exact edit and waits for the human's yes. Otherwise
   it says there is no change.

## Non-goals
- No changes to build, check, the roadmap skill or bootstrap.
- No edits to the 7 existing specs.
- No date gate: old specs pass because their repo has no PRODUCT.md.

## Constraints
- Must not break: the 7 historical specs and 16 receipts validate clean; repos without
  PRODUCT.md need no Serves line; SKILL.md stays within its size test.
- Ask first: nothing. The Serves line's shape was settled in the grill.
- Gate: none

## Proof
| # | Claim | Surface | Check | Pass signal | Kind | Base |
|---|---|---|---|---|---|---|
| 1 | Goal 1: from an item, no answered why, Serves named, row 1 = Solved when | fresh headless `jflow spec` session, first round | Test repo "tally" (word counter) with PRODUCT.md outcomes "Counts you can trust" and "Fast on big folders", DESIGN.md, and ROADMAP.md item skip-binary with Problem, Why now, Options, Solved when, Out of scope, Serves and Open for spec filled. Message: `jflow spec skip-binary: roadmap item skip-binary in ROADMAP.md`, told to stop at round 1 and print the spec header and row 1. Two runs | In both runs: no question asks who has the problem, its evidence, why now, which option, or what is out of scope; header has `Serves: Counts you can trust`; row 1 Claim is the item's Solved when word for word | new | red |
| 2 | Goal 2: without an item, the why comes first | same, test repo with no roadmap items | Message: `jflow spec skip-binary: tally counts binary files such as PNGs as words`. Two runs | In both runs: round 1 asks at least one of who has the problem, the evidence, why now; header has a Serves line naming one of the two outcomes | new | red |
| 3 | Goal 3: validate enforces Serves where PRODUCT.md exists | `jflow.py validate <slug> spec` and `record`, in a git repo with PRODUCT.md | Spec with no Serves; then Serves naming an unknown outcome; then Serves naming a real `###` outcome | First two exit 1 with a `spec.md:<line>:` error naming Serves, and `record` writes no run.jsonl line; the third exits 0 | new | red |
| 4 | Old specs and repos without PRODUCT.md still pass | `validate` | The historical-specs unittest; a spec with no Serves in a repo with no PRODUCT.md | Test OK; exit 0, no output | keep | green |
| 5 | Goal 4: done reports row 1 and asks before editing the north star | `references/done.md` | `grep -n "PRODUCT.md\|DESIGN.md\|Solved when" references/done.md` and read the matched steps | A step shows the exact PRODUCT.md or DESIGN.md edit and waits for a yes before making it; the closing line names row 1's result | new | red |

## Human checks
- Read the new spec.md and done.md wording once for plain language.
