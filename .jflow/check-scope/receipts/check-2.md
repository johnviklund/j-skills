# check-2 @ 75643a3efa319de48f2dfa1cefe20f3e248843b9 · gpt-6.2-sol · high

| # | Verdict | Evidence |
|---|---|---|
| 1 | BLOCKED | The five completed runs after this change ships. |
| 2 | PROVED | `python3 .jflow/check-scope/drive.py 2` → exit 1, no new input since check-1 |
| 3 | BROKEN | defect 1, defect 2 |
| 4 | PROVED | `python3 .jflow/check-scope/drive.py 4` → 3,001 bytes exits 1, 3,000 bytes exits 0 |
| 5 | PROVED | `sed -n '26,28p;91,99p' .github/skills/jflow/references/check.md` → name only what is missing. next and the human decide what follows. |
| 6 | PROVED | `sed -n '58,61p' .github/skills/jflow/references/check.md` → A Maybe is only a suspected defect with a named input you could neither run nor trace. All four exclusions follow. |
| 7 | PROVED | `sed -n '40,41p' .github/skills/jflow/references/spec.md` → fixed labelled case set the builder can run free. keep needs no paid call or approval and reads values at check time. |
| 8 | PROVED | `python3 .jflow/check-scope/drive.py 8` → 8 of 9 historical runs pass. Failed: corrections-bad-records |

## Defects
- 1. `jflow.py validate`: A builder adds this run's `notes.md` input while completing a merge. The validator misses changes made in the merge commit and rejects check-2. It should accept the committed notes. Evidence: run, `python3 .jflow/check-scope/drive.py merge-input` → exit 1, no new input since check-1.
- 2. `jflow.py validate`: A builder moves a workflow script into a run folder with `git mv`. Git lists the destination alone, so the validator ignores the removal from the workflow and rejects check-2. It should count the removal as code input. Evidence: run, `python3 .jflow/check-scope/drive.py renamed-input` → exit 1, no new input since check-1.
- 3. `jflow.py validate`: A caller validates check-2 with an uncommitted check-1 saved as UTF-16. The validator raises a traceback when it reads the prior receipt's header. It should give a validation error naming the unreadable check-1. Evidence: run, `python3 .jflow/check-scope/drive.py unreadable-prior` → UnicodeDecodeError.

## Maybes
- none
