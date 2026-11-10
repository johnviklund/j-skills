# check-3 @ df19d36 · claude-opus-5-5 · high
| # | Verdict | Evidence |
|---|---|---|
| 1 | PROVED | `python3 .jflow/jflow-validate/drive.py 1` → 1: 21 of 21 rc=0 with no output |
| 2 | PROVED | `python3 .jflow/jflow-validate/drive.py 2` → 2: 8 of 8 rc=1; each names the fault, e.g. `spec.md:54: invalid Kind or Base`, `spec.md:1: missing Gate line` |
| 3 | PROVED | `python3 .jflow/jflow-validate/drive.py 3` → 3: 10 of 10 rc=1 naming check-1.md:<line>; 240-char cell rc=0 '' |
| 4 | PROVED | `python3 .jflow/jflow-validate/drive.py 4` → 4: 3 of 3 rc=1; good line rc=0 '' |
| 5 | PROVED | `python3 .jflow/jflow-validate/drive.py 5` → broken check and spec: rc=1 same=True, problems printed; 5: valid receipt HEAD rc=0 n=6, Base rc=0 n=6, same=True |
| 6 | PROVED | `python3 .jflow/jflow-validate/drive.py 6` → 6: rc=0 lines 6 -> 7 last step=build |
| 7 | PROVED | `python3 .jflow/jflow-validate/drive.py 7` → 7: 12 of 12 byte-identical (5 runs plus jflow-validate, next and summary --json, HEAD vs Base worktree) |
| 8 | PROVED | `uv run --offline --no-project --python 3.9 python -m unittest discover -s .github/skills/jflow/scripts/tests` → Ran 28 tests in 19.669s … OK |
| 9 | PROVED | `git ls-files .github/skills/jflow \| grep -v /tests/ \| xargs cat \| wc -c` → 49996 |
| 10 | PROVED | `grep -n validate .github/skills/jflow/SKILL.md` → 120:`record` validates the spec, check and accept steps; fix reported problems before recording. |

## Defects
- none

## Maybes
- Citation shapes outside the template still pass on BROKEN rows with no defect 9: `defect 1 and defect 9`, `defect 1, 9`, `defects 1, 9` (`drive.py attack`). Fixing them costs bytes the 50000 cap no longer has: 49996 now.
- `defect 01` with defect 1 present fails as `unknown defect 01`. Off-template, so no defect.
- Bare `jflow.py next jflow-validate` names gpt-6.1-sol for check; the run needs `--builder-vendor openai`, as notes.md says. `next` is unchanged from Base (row 7), so this is not from this change.
