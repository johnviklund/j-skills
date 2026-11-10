# check-2 @ 4d109e8 · claude-opus-5-5 · high
| # | Verdict | Evidence |
|---|---|---|
| 1 | PROVED | `jflow.py validate <slug> spec` on the 5 runs, `validate <slug> check` with each of the 16 receipts newest, scratch clone → 21 of 21 rc=0, no output (wait-points check-1/2 row 7 hold `\|`) |
| 2 | PROVED | wait-points spec copies, one fault each → 8 of 8 rc=1: invalid Status, unknown commit sha, missing section Non-goals, expected columns…, invalid Kind or Base ×3, missing Gate line |
| 3 | PROVED | wait-points check-1 copies, one fault each → 10 of 10 rc=1 naming `check-1.md:<line>`, e.g. `:5: unknown defect 7`, `:1: missing row 2`; 240-char cell → rc=0 |
| 4 | PROVED | `validate x accept`: no sha → `spec.md:63: invalid Accepted line`; Row 42 → `Accepted names unknown row 42`; deadbee → `unknown commit sha`; 3 of 3 rc=1, good line rc=0 |
| 5 | PROVED | `record x check` (NOPE verdict), `record x spec` (Status: draft) → rc=1, problems printed, run.jsonl sha256 same; valid receipt → rc=0, check n=1 line replaced, same as Base script |
| 6 | PROVED | `record x build` with check-2 holding `\| 2 \| NOPE` → rc=0, build line appended (6 → 7 lines) |
| 7 | PROVED | `next <slug> --json` and `summary <slug> --json`, HEAD script vs Base worktree script, on the 5 runs plus jflow-validate → 12 of 12 byte-identical |
| 8 | PROVED | `uv run --offline --no-project --python 3.9 python -m unittest discover -s .github/skills/jflow/scripts/tests` → Ran 27 tests … OK |
| 9 | PROVED | `git ls-files .github/skills/jflow \| grep -v /tests/ \| xargs cat \| wc -c` → 49998 |
| 10 | PROVED | `grep -n validate .github/skills/jflow/SKILL.md` → 120:`record` validates the spec, check and accept steps; fix reported problems before recording. |

## Defects
- 1. `jflow.py` `validate`, `re.fullmatch(r"(?i)defect (\d+)", evidence)`: a BROKEN row citing two defects, `\| 4 \| BROKEN \| defect 1, defect 9 \|`, with no defect 9 → passes, record writes → `unknown defect 9`, as 17afb7a did. Evidence: run, wait-points copy → HEAD rc=0, 17afb7a rc=1

## Maybes
- The same whole-cell rule also lets `defect 9.` and `see defect 9` through on BROKEN rows. These are off-template, so only the comma list above is reported as a defect.
- Row 9 now passes with 2 bytes to spare. Any fix for defect 1 that adds code must save bytes elsewhere, or the human raises the cap.
