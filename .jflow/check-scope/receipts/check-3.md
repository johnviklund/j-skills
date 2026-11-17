# check-3 @ a6b37fe60ee726e56c452c76f85ece90955dcc9d · gpt-6.2-sol · high

| # | Verdict | Evidence |
|---|---|---|
| 1 | BLOCKED | Five completed runs after shipping. |
| 2 | PROVED | `python3 .jflow/check-scope/drive.py 2` → exit 1, no new input since check-1 |
| 3 | BROKEN | defect 1 |
| 4 | PROVED | `python3 .jflow/check-scope/drive.py 4` → 3,001 bytes exits 1, 3,000 bytes exits 0 |
| 5 | PROVED | `sed -n '26,28p;91,99p' .github/skills/jflow/references/check.md` → name only what is missing. next and the human decide what follows. |
| 6 | PROVED | `sed -n '58,61p' .github/skills/jflow/references/check.md` → A Maybe needs a suspected defect with a named input you could neither run nor trace. All four exclusions follow. |
| 7 | PROVED | `sed -n '40,41p' .github/skills/jflow/references/spec.md` → fixed labelled case set the builder can run free. keep needs no paid call or approval and reads values at check time. |
| 8 | PROVED | `python3 .jflow/check-scope/drive.py 8` → 8 of 9 historical runs pass. Failed: corrections-bad-records |

## Defects
- 1. `jflow.py validate`: A builder commits this run's `notes.md` alongside a filename with a non-UTF-8 byte. The validator rejects the new input and reports that it cannot read the prior receipt. It should accept the committed notes and code. Evidence: run, `python3 .jflow/check-scope/drive.py non-utf8-path` → exit 1, cannot read check-1.

## Maybes
- none
