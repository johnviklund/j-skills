# check-1 @ 1102462350a7aa4876c5f0e9c53083747c350b53 · gpt-6.1-sol · high
| # | Verdict | Evidence |
|---|---|---|
| 1 | PROVED | `python3 .jflow/spec-why/drive.py 1` → 2/2 fresh runs name Counts you can trust and copy Solved when exactly; neither re-asks an answered why, option or scope question. |
| 2 | PROVED | `python3 .jflow/spec-why/drive.py 2` → 2/2 fresh runs ask who, evidence and why now first; both name Counts you can trust in Serves. |
| 3 | BROKEN | defect 1, defect 2 |
| 4 | PROVED | `python3 .jflow/spec-why/drive.py 4` → row 4: historical-specs unittest OK; no PRODUCT.md: validate exit 0, no output |
| 5 | PROVED | `cd .github/skills/jflow && grep -n "PRODUCT.md\|DESIGN.md\|Solved when" references/done.md` → step 2 shows exact edits and waits for yes; the closing line reports row 1. |

## Defects
- 1. `.github/skills/jflow/scripts/jflow.py:212`, `validate`: a spec author omits the header's Serves and quotes `Serves: Counts you can trust` inside a fenced example under Problem. Both validate and record accept it and record writes a line. Reject the missing header; a quoted example does not declare the outcome. Evidence: run, `python3 .jflow/spec-why/drive.py attack` → body-example: validate=0, record=0, run.jsonl lines=1
- 2. `.github/skills/jflow/scripts/jflow.py:213`, `validate`: a PRODUCT.md author puts `### Retired outcome` inside a fenced example. A spec naming Retired outcome passes validate and record despite no such heading. Conversely, the valid heading `### Counts you can trust ###` rejects `Serves: Counts you can trust`. Match Markdown heading titles outside fenced examples. Evidence: run, `python3 .jflow/spec-why/drive.py attack` → fenced-outcome: validate=0, record=0, run.jsonl lines=1; closing-hashes: validate=1, record=1, run.jsonl lines=0

## Maybes
- none
