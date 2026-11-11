# check-2 @ e9539bd46f48f4313a99637498f34e27e3e63021 · gpt-6.1-sol · high
| # | Verdict | Evidence |
|---|---|---|
| 1 | BROKEN | defect 1 |
| 2 | PROVED | `python3 .jflow/spec-why/drive.py 2` → 2/2 fresh runs ask who, evidence and why now first; both name Counts you can trust in Serves. |
| 3 | BROKEN | defect 2, defect 3 |
| 4 | PROVED | `python3 .jflow/spec-why/drive.py 4` → row 4: historical-specs unittest OK; no PRODUCT.md: validate exit 0, no output |
| 5 | PROVED | `cd .github/skills/jflow && grep -n "PRODUCT.md\|DESIGN.md\|Solved when" references/done.md` → step 2 shows exact edits and waits for yes; the closing line reports row 1. |

## Defects
- 1. `.github/skills/jflow/references/spec.md`, Grill the what: the row 1 roadmap fixture already chooses skipping files with a NUL in the first 8 KiB. In fresh run 1, the session asks whether binary files without a NUL in that prefix may count and offers scanning the whole file instead. That reopens the chosen cutoff. It should retain that answered choice and ask only unresolved questions. Both runs name Serves and copy Solved when exactly. Evidence: run, `python3 .jflow/spec-why/drive.py 1` → run 1 asks "Can a binary file with no NUL in its first 8 KiB still be counted?" and offers "B. No. Scan the whole file."
- 2. `.github/skills/jflow/scripts/jflow.py:208`, `validate`: a PRODUCT.md author appends a four-backtick fenced example containing an inner triple-backtick fence and `### Retired outcome`. A spec author names Retired outcome in Serves. Validate and record accept it and write a run line, although the outcome exists only inside the example. Three-space-indented and unclosed fences also expose example headings. Reject these names. Evidence: run, `python3 .jflow/spec-why/drive.py attack` → nested-fence: validate=0, record=0, run.jsonl lines=1; indented-fence and unclosed-fence also accept
- 3. `.github/skills/jflow/scripts/jflow.py:209`, `validate`: a PRODUCT.md author indents the real `### Counts you can trust` heading by three spaces, which Markdown permits. A spec naming Counts you can trust now fails validate and record with a Serves error. Recognize this heading and accept the spec. Evidence: run, `python3 .jflow/spec-why/drive.py attack` → indented-heading: validate=1, record=1, run.jsonl lines=0

## Maybes
- none
