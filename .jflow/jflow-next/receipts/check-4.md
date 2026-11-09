# check-4 @ 046bb7e · gpt-6.1-sol high
| # | Verdict | Evidence |
|---|---|---|
| 1 | PROVED | `python3 .jflow/jflow-next/drive.py history` → Row 1: PASS; 25 historical run commits, cap interval and final done states |
| 2 | PROVED | `python3 .jflow/jflow-next/drive.py states` → Rows 2,3,5,6,7,8: PASS; 14 states, shape, cards, vendor, slug, code-only changes |
| 3 | PROVED | `python3 .jflow/jflow-next/drive.py states` → Rows 2,3,5,6,7,8: PASS; 14 states, shape, cards, vendor, slug, code-only changes |
| 4 | PROVED | `python3 .jflow/jflow-next/drive.py cap` → Row 4: PASS; cap 3, rerun stays 3, allowance 5 gives fix |
| 5 | PROVED | `python3 .jflow/jflow-next/drive.py states` → Rows 2,3,5,6,7,8: PASS; 14 states, shape, cards, vendor, slug, code-only changes |
| 6 | PROVED | `python3 .jflow/jflow-next/drive.py states` → Rows 2,3,5,6,7,8: PASS; 14 states, shape, cards, vendor, slug, code-only changes |
| 7 | PROVED | `python3 .jflow/jflow-next/drive.py states` → Rows 2,3,5,6,7,8: PASS; 14 states, shape, cards, vendor, slug, code-only changes |
| 8 | PROVED | `python3 .jflow/jflow-next/drive.py states` → Rows 2,3,5,6,7,8: PASS; 14 states, shape, cards, vendor, slug, code-only changes |
| 9 | PROVED | `python3 .jflow/jflow-next/drive.py docs` → Row 9: PASS; table removed; hub, spec, build, fix, live, check call next; done closes without a card |
| 10 | PROVED | `python3 .jflow/jflow-next/drive.py compat` → Row 10: PASS; Python 3.9, 17 tests OK, next runs, 3 outputs byte-identical to Base |
| 11 | PROVED | `python3 .jflow/jflow-next/drive.py budget` → Row 11: PASS; script +111, tests +94, agent files 43077 bytes |

## Defects
- none

## Maybes
- Row 9's first literal grep has an empty alternative and matches every line. The driver runs it and checks table removal directly too.
