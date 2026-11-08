# receipt-evidence-cap
Status: done
Base: 01f9bba82091e79c5d6eccf05af1dfa29f7b410e
Issue: roadmap item 0.3 in https://github.com/johnviklund/hq/blob/main/docs/jflow-standalone-and-hq-roadmap.md

## Problem
Every later check, `retro` and the human read check receipts. Measured 2026-11-08 on 13 receipts
from finished private runs: 3.3 to 8.5 KB each. About 60% is the Evidence column, with a median
cell of 330 characters, 90th percentile 509 and maximum 1,048; only 28 of 131 cells fit in 240.
Defects and Maybes add 0.9 to 3.5 KB. The cause is `references/check.md`'s evidence rule, which asks
for the command and "the output that matters, quoted here" with no limit.

## Goals
1. Every Evidence cell in a receipt holds at most 240 characters: the command and the one output
   line that decides the verdict.
2. Each defect's `Evidence:` part has the same 240-character cap. A BROKEN row cites its defect
   number instead of repeating it.
3. Raw output stays in the temp folder, and the quoted command reruns as written, so a reader can
   get the rest.

## Non-goals
- No code: no warning or validation in `jflow.py`. That is roadmap item 1.3.
- No cap on a defect's input or its "what should happen".
- No change to verdicts, routing, the check cap or how a check decides: the trial stays comparable.
- No rewrite of existing receipts, and nothing about `drive.py` (roadmap item 0.4).

## Constraints
- Must not break: the receipt template shape `jflow.py` parses (heading sha, verdict column,
  `## Defects` and `## Maybes` bullets); `carried from check-N` as evidence.
- Ask first: nothing.
- Gate: none.

## Proof
| # | Claim | Surface | Check | Pass signal | Kind | Base |
|---|---|---|---|---|---|---|
| 1 | Goal 1 | `references/check.md` | Read the evidence rule and the template | Both state at most 240 characters per Evidence cell: the command plus the decisive output line | new | red |
| 2 | Goal 2 | `references/check.md` | Read the Defects rule and template | A defect's `Evidence:` part is capped at 240 characters, and a BROKEN row cites its defect number | new | red |
| 3 | Goal 3 | `.github/skills/jflow/` | `grep -rn "quoted here" .github/skills/jflow`, then read the rule | No hits; the rule says the quoted command reruns as written and raw output stays in the temp folder | new | red |
| 4 | Parser still counts | `scripts/jflow.py` | `receipt_fields` on a receipt written to the new template, with PROVED, BROKEN and BLOCKED rows, one defect and `- none` maybes | `rows {PROVED:1, BROKEN:1, BLOCKED:1}`, `defects 1`, `maybes 0`, sha read | keep | green |
| 5 | Carried evidence kept | `references/check.md` | `grep -n "carried from check-N"` | Still allowed as a row's evidence | keep | green |
| 6 | Text only | git | `git diff --name-only <Base>..HEAD -- . ':(exclude).jflow'` | Only `.md` files under `.github/skills/jflow/` | keep | green |

## Human checks
- On the next three trial runs, every Evidence cell and every defect `Evidence:` part is at most
  240 characters, and each receipt is under 3 KB.
