# check-4 @ f833813f922df6bc8b87767b2fd91fd6f469996c · gpt-6.2-sol · high

| # | Verdict | Evidence |
|---|---|---|
| 1 | BLOCKED | Five completed jflow runs after shipping. |
| 2 | PROVED | `python3 .jflow/check-scope/drive.py 2` → exit 1, no new input since check-1 |
| 3 | PROVED | `python3 .jflow/check-scope/drive.py 3` → validate: exit 0 |
| 4 | PROVED | `python3 .jflow/check-scope/drive.py 4` → 3,001 bytes exits 1, 3,000 bytes exits 0 |
| 5 | PROVED | `sed -n '26,28p;91,99p' .github/skills/jflow/references/check.md` → BLOCKED evidence names the missing input. `next` and the human decide, including at the cap. |
| 6 | PROVED | `sed -n '58,61p' .github/skills/jflow/references/check.md` → Maybes require a suspected defect with a named input the checker could neither run nor trace. All four exclusions follow. |
| 7 | PROVED | `sed -n '40,41p' .github/skills/jflow/references/spec.md` → fixed labelled cases run free. Keep rows need no payment or approval and read values at check time. |
| 8 | PROVED | `python3 .jflow/check-scope/drive.py 8` → 8 of 9 historical runs pass. Failed: corrections-bad-records |

## Defects
- 1. `jflow.py` `next_step`: A user follows the cap card and adds `Checks allowed: 2` to notes that already contain `Checks allowed: 1`. The parser reads the first line and the card still stops for the cap. Following the option should raise the cap. Evidence: run, `python3 .jflow/check-scope/drive.py cap-options` → After appending Checks allowed: 2: The human decides: 1 checks used of 1 and check is next.

## Maybes
- none
