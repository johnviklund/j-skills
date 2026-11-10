# check-1 @ 17afb7a · claude-opus-5-5 · high
| # | Verdict | Evidence |
|---|---|---|
| 1 | PROVED | `jflow.py validate <slug> spec` on the 5 runs, `validate <slug> check` with each of the 16 receipts newest, in a scratch clone → 21 of 21 (wait-points check-1/2 row 7 hold `\|`) |
| 2 | PROVED | scratch copies of wait-points spec, one fault each → 8 of 8 rc=1: invalid Status, unknown commit sha, missing section Non-goals, expected columns…, invalid Kind or Base ×3, missing Gate line |
| 3 | PROVED | wait-points check-1 copies, one fault each → 10 of 10 rc=1, e.g. `check-1.md:5: unknown row or verdict 2`, `missing row 9`, `row 2 not under Accepted`; 240-char cell → rc=0 |
| 4 | PROVED | `validate x accept` with planted lines → no sha `spec.md:63: invalid Accepted line`, row 42 `Accepted names unknown row 42`, deadbee `unknown commit sha`: 3 of 3 rc=1; good Row/Defect lines rc=0 |
| 5 | PROVED | `record x check` (NOPE verdict), then `record x spec` (Status: draft) → rc=1, problems printed, run.jsonl sha256 same; clean copy `record x check` → rc=0, check n=2 line replaced as before |
| 6 | PROVED | `record x build` with check-2 holding `\| 2 \| NOPE` → rc=0, build line appended |
| 7 | PROVED | `next <slug> --json` and `summary <slug> --json`, HEAD script vs Base worktree script, on the 5 runs (plus jflow-validate) → 12 of 12 byte-identical |
| 8 | PROVED | `uv run --offline --no-project --python 3.9 python -m unittest discover -s .github/skills/jflow/scripts/tests` → Ran 26 tests … OK |
| 9 | PROVED | `git ls-files .github/skills/jflow \| grep -v /tests/ \| xargs cat \| wc -c` → 49986 |
| 10 | PROVED | `grep -n validate .github/skills/jflow/SKILL.md` → 120:`record` validates the spec, check and accept steps; fix reported problems before recording. |

## Defects
- 1. `.github/skills/jflow/scripts/jflow.py` `validate` check branch, `re.findall(r"\bdefect (\d+)\b", evidence, re.I)`: a checker's PROVED row quotes a defect in its command, e.g. `` | 7 | PROVED | `grep -c "defect 1" receipts/check-1.md` → 2 | `` in a receipt whose Defects is `- none` → validate and `record check` fail `unknown defect 1` and refuse a template-valid receipt → only a BROKEN row's citation should be checked against the Defects list. Evidence: run, wait-points copy, `jflow.py validate x check` → `.jflow/x/receipts/check-2.md:10: unknown defect 1`, rc=1

## Maybes
- Row 9 passes with 14 bytes to spare, and the build met it by shortening existing comments and docstrings in `jflow.py` (e.g. `next_step`'s state-table docstring removed, the `closed` acceptance rule cut to one line). The next jflow change will hit the cap; the human may want to raise it rather than trim more explanation.
- receipt-evidence-cap check-1 row 2 (PROVED, quotes `\| 2 \| BROKEN \| defect 1 \|`) passes only because that receipt also has a defect 1; it is a live example of defect 1.
