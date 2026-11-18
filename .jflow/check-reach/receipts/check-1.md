# check-1 @ 05054caafccb497647acca53b0f8d9b38ce3a156 · gpt-6.2-sol · high

| # | Verdict | Evidence |
|---|---|---|
| 1 | PROVED | `python3 .jflow/check-reach/drive.py 1` → step human, names defect 1, recommends A. Accept them |
| 2 | BROKEN | defect 3 |
| 3 | PROVED | `python3 .jflow/check-reach/drive.py 3` → step fix |
| 4 | PROVED | `python3 .jflow/check-reach/drive.py 4` → step fix |
| 5 | BROKEN | defect 2 |
| 6 | PROVED | `sed -n '55,58p;90p' .github/skills/jflow/references/check.md` → defines [use] and [edge], and the defect example starts with [use] |
| 7 | PROVED | `python3 .jflow/check-reach/drive.py 7` → 9 of 10 old runs pass; failed: corrections-bad-records |

## Defects
- 1. [use] `jflow.py` `next_step`: A user picks Fix them on an edge-only receipt at the check cap. The card starts a fix without a cap increase and the next check stops after the fix. The card should ask for a cap increase before starting the fix. Evidence: run, `python3 .jflow/check-reach/drive.py cap` → 4 checks used of 4 and check is next after following option B.
- 2. [edge] `jflow.py` `validate`: A checker enters `[needs-review]` in the tag slot. Validation treats it as untagged text. It should reject the unknown tag. Evidence: run, `python3 .jflow/check-reach/drive.py punctuation` → [needs-review] exits 0.
- 3. [edge] `jflow.py` `next_step`: A checker reuses defect number 1 for an `[edge]` defect after a `[use]` defect. The receipt validates and `next` offers acceptance after discarding the `[use]` line. Any receipt that validates and contains a `[use]` defect should route to fix. Evidence: run, `python3 .jflow/check-reach/drive.py duplicate` → validate exits 0, every open defect is [edge]: defect 1.

## Maybes
- none
