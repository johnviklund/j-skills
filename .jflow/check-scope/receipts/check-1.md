# check-1 @ edf6deb0e0d5dc078989471a6c125885c9454c42 · gpt-6.2-sol · high

| # | Verdict | Evidence |
|---|---|---|
| 1 | BLOCKED | Five completed jflow runs after check-scope ships are missing. |
| 2 | BROKEN | defect 1, defect 2 |
| 3 | PROVED | `python3 .jflow/check-scope/drive.py 3` → validate: exit 0 |
| 4 | BROKEN | defect 3 |
| 5 | PROVED | `sed -n '26,28p;95,97p' .github/skills/jflow/references/check.md` → BLOCKED evidence names the missing input. `next` and the human decide what follows, including the cap. |
| 6 | BROKEN | defect 4 |
| 7 | PROVED | `sed -n '40,41p' .github/skills/jflow/references/spec.md` → Fixed labelled cases run free. Keep rows need no payment or approval and read values at check time. |
| 8 | PROVED | `python3 .jflow/check-scope/drive.py 8` → 8 of 9 historical runs pass. Failed: corrections-bad-records |

## Defects
- 1. `jflow.py` `validate`: A caller leaves `check-1.md` uncommitted and adds `check-2.md` at the same HEAD. The validator accepts the second receipt. It should require a committed first receipt and subsequent input. Evidence: run, `python3 .jflow/check-scope/drive.py uncommitted` → validate: exit 0.
- 2. `jflow.py` `validate`: A caller commits only an unrelated run's receipt, then adds a repeat receipt to the current run. The validator accepts it. The check instructions say receipt-only changes do not supply input. Evidence: run, `python3 .jflow/check-scope/drive.py other-receipt` → validate: exit 0.
- 3. `jflow.py` `validate`: A caller saves a 3,001-byte receipt with CRLF line endings after committing new notes. Text mode drops the carriage returns before counting bytes. The validator accepts the file and should reject it. Evidence: run, `python3 .jflow/check-scope/drive.py crlf` → 3001 bytes: exit 0.
- 4. `references/check.md` Write `receipts/check-N.md`: Row 1 lacks five completed runs. The template sends that check limit to Maybes, where it becomes a status note. Maybes should contain only suspected defects with a named input. Evidence: traced, `sed -n '58,66p' .github/skills/jflow/references/check.md` → "a limit on the check goes in Maybes."

## Maybes
- none
