# check-2 @ 88c615714ccd52675e6cdc9a8f17834180c74701 · gpt-6.2-sol · high

| # | Verdict | Evidence |
|---|---|---|
| 1 | PROVED | `python3 .jflow/check-reach/drive.py 1` → step human, names defect 1, recommends A. Accept them |
| 2 | PROVED | `python3 .jflow/check-reach/drive.py 2` → step fix |
| 3 | PROVED | `python3 .jflow/check-reach/drive.py 3` → step fix |
| 4 | PROVED | `python3 .jflow/check-reach/drive.py 4` → step fix |
| 5 | BROKEN | defect 1 |
| 6 | PROVED | `sed -n '55,58p;90p' .github/skills/jflow/references/check.md` → defines [use] and [edge], and the defect example starts with [use] |
| 7 | PROVED | `python3 .jflow/check-reach/drive.py 7` → 9 of 10 old runs pass; failed: corrections-bad-records |

## Defects
- 1. [edge] `jflow.py` `validate`: A checker writes `[odd]` followed by a tab before the file name. Validation reads it as untagged and exits 0. It should reject the unknown tag, as it does when a space follows `[odd]`. Evidence: run, `python3 .jflow/check-reach/drive.py tab-tag` → [odd] exits 0, [use] exits 0, [edge] exits 0.
- 2. [edge] `jflow.py` `next_step`: A run has four counted checks and its cap is reset to three. Option B raises the cap to four and asks the builder to fix. The next check still stops at the cap. Option B should name a cap that permits the next check. Evidence: run, `python3 .jflow/check-reach/drive.py over-cap` → 4 checks used of 4 and check is next; BROKEN rows and defects went from 2 to 1.

## Maybes
- none
