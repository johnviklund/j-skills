# check-3 @ f6fb039 · gpt-6.1-sol high
| # | Verdict | Evidence |
|---|---|---|
| 1 | PROVED | `python3 .jflow/jflow-next/drive.py history` → Row 1: PASS; 25 historical run commits, cap interval and final done states |
| 2 | BROKEN | defects 1 and 2 |
| 3 | PROVED | `python3 .jflow/jflow-next/drive.py states` → Rows 2,3,5,6,7,8: PASS; 14 states, shape, cards, vendor, slug, code-only changes |
| 4 | PROVED | `python3 .jflow/jflow-next/drive.py cap` → Row 4: PASS; cap 3, rerun stays 3, allowance 5 gives fix |
| 5 | PROVED | `python3 .jflow/jflow-next/drive.py states` → Rows 2,3,5,6,7,8: PASS; 14 states, shape, cards, vendor, slug, code-only changes |
| 6 | PROVED | `python3 .jflow/jflow-next/drive.py states` → Rows 2,3,5,6,7,8: PASS; 14 states, shape, cards, vendor, slug, code-only changes |
| 7 | PROVED | `python3 .jflow/jflow-next/drive.py states` → Rows 2,3,5,6,7,8: PASS; 14 states, shape, cards, vendor, slug, code-only changes |
| 8 | PROVED | `python3 .jflow/jflow-next/drive.py states` → Rows 2,3,5,6,7,8: PASS; 14 states, shape, cards, vendor, slug, code-only changes |
| 9 | PROVED | `python3 .jflow/jflow-next/drive.py docs` → Row 9: PASS; table removed; hub, spec, build, fix, live, check call next; done closes without a card |
| 10 | PROVED | `python3 .jflow/jflow-next/drive.py compat` → Row 10: PASS; Python 3.9, 17 tests OK, next runs, 3 outputs byte-identical to Base |
| 11 | PROVED | `python3 .jflow/jflow-next/drive.py budget` → Row 11: PASS; script +93, tests +90, agent files 41813 bytes |

## Defects
- 1. `.github/skills/jflow/scripts/jflow.py:next_step` discards an acceptance when a later receipt carries the same failure. The user accepts Row 1 at 254 of 300 while Row 2 is BLOCKED. After the service returns, check-2 reruns Row 2 and proves it, carrying Row 1's BROKEN verdict and citing check-1, per the check instructions. With unchanged code, `next` returns fix instead of done for the already accepted miss. Evidence: run, `python3 .jflow/jflow-next/drive.py acceptance_edges` → Attack accepted-carried-row: check-2 carries accepted Row 1, proves Row 2; next=fix; expected=done
- 2. `.github/skills/jflow/scripts/jflow.py:next_step` no longer reads the acceptance's target sha. Check-1 reports Row 1 at 254 of 300 on old code. After a code change, check-2 reports Row 1 BROKEN at 0 of 300. The user then accepts only the old 254 result, recording the old sha in the documented acceptance format. Because that acceptance commit follows check-2, `next` returns done and suppresses the new failure. It should return fix for the failure on code the user did not accept. Evidence: run, `python3 .jflow/jflow-next/drive.py acceptance_edges` → Attack acceptance-other-sha: acceptance names old code, newest Row 1 BROKEN at 0 of 300; next=done; expected=fix

## Maybes
- Row 9's first literal grep has an empty alternative and matches every line. The driver runs it and checks table removal directly too.
