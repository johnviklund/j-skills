# check-1 @ 04beb5f5ef0cd7c2f3809c02e18d86fcf77f382b · gpt-6.1-sol high
| # | Verdict | Evidence |
|---|---|---|
| 1 | PROVED | `grep -n "drive.py" .github/skills/jflow/references/done.md` → 34: Delete `.jflow/<slug>/drive.py` with `git rm`, so the done commit removes it. |
| 2 | PROVED | `grep -n "verify.maintain" .github/skills/jflow/references/done.md` → 38: line that names the verb, the commit that holds the script, and `verify.maintain` as the command |
| 3 | PROVED | `sed -n '8,10p;35,37p' .github/skills/jflow/references/done.md` → qualifies only when a later run would drive the same user path; a comparison against `Base` or |
| 4 | BROKEN | defect 1 |
| 5 | PROVED | `grep -n "drive.py" .github/skills/jflow/SKILL.md` → 51: drive.py ... reused by later checks, deleted at done |
| 6 | PROVED | `grep -n "reuse and extend it" .github/skills/jflow/references/check.md` → 21: reuse and extend it, so no check writes it twice. No diff from Base. |
| 7 | PROVED | `python3 .jflow/drive-py-at-done/drive.py row7` → False |
| 8 | PROVED | `git diff --name-only c45e466..HEAD -- . ':(exclude).jflow'` → .github/skills/jflow/SKILL.md and .github/skills/jflow/references/done.md only |

## Defects
- 1. `.github/skills/jflow/references/done.md`, step 6: a first-check receipt quotes a newly written driver, but its header SHA names the build commit. The driver arrives in the later check commit. Restoring at the header SHA exits 128, so the promised replay fails. The existing receipt-evidence-cap check-1 supplies this input through its row 4 command. Select the commit containing that receipt's driver version, while keeping the tested code SHA distinct. Evidence: run, `python3 .jflow/drive-py-at-done/drive.py receipt-sha` → receipt header 3ad0bd2: git show exits 128; receipt-containing commit: driver restored successfully

## Maybes
- none
