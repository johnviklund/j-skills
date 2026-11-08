# check-5 @ 1f0389c · claude-opus-5.5 · high
| # | Verdict | Evidence |
|---|---|---|
| 1 | PROVED | `python3 .jflow/jflow-config/drive.py 1` → spec/build/fix/done `claude-opus-5.5 medium None`; check `gpt-6.1-sol high` with fallback `gpt-6-astra high` |
| 2 | PROVED | `drive.py 2` → build `repo-b`, check `env-c`, spec `claude-opus-5.5`; `check --config` → `flag-c` |
| 3 | PROVED | `drive.py 3` → `{bad`: exit 1, stdout '', `<tmp>/.jflow/config.json: cannot read valid config JSON`; effort 5: exit 1, `...: seat model, vendor and effort must be nonempty strings` |
| 4 | PROVED | `drive.py 4` → builder gpt-6.1-sol/openai: `on: claude-opus-5.5 high`; `different_vendors: false` → `off: gpt-6.1-sol high` |
| 5 | PROVED | `drive.py 5` → rules all three True; each rule false → exit 1, stdout '', `locked rule <name>` |
| 6 | PROVED | `drive.py 6` → sk-ant-, ghp_, AKIA, 40-char token: config and record each exit 1, `not echoed`; record `log unchanged` |
| 7 | PROVED | `drive.py 7` → all 7 flow.json steps resolve with role True; `bogus` → exit 1, `unknown flow step` |
| 8 | PROVED | the row's `grep -n` → exit 1, no match; SKILL.md:28 `Run python3 <skill>/scripts/jflow.py seat <step> and copy its assignment into each card` |
| 9 | PROVED | `$(uv python find 3.9) -m unittest discover -s .github/skills/jflow/scripts/tests` → `Ran 13 tests ... OK`; record and summary for `sk-onboarding-checklist-v2`, `sk-migrate-postgres-to-16`, `sk-ui` exit 0 |
| 10 | PROVED | `git diff --numstat bc5d3cb -- .github/skills/jflow/scripts/jflow.py` → `88 5` (net +83 ≤ 90); skill files without `__pycache__` → 49,905 bytes ≤ 50,000 |

## Defects
- none

## Maybes
- Only `--model` and `--effort` are scanned now. A key passed as an unknown extra argument, `record sk-ui spec --model m --effort high --token ghp_…`, or as `--session ghp_…`, exits 2 and writes nothing, but argparse echoes it on stderr. bc5d3cb echoes it the same way.
- Check-4's Maybe inputs `sk-migrate-postgres-to-16` and `sk-onboarding_checklist_x` now record with exit 0; `--model=ghp_…` and the abbreviation `--mod ghp_…` are refused without echo.
- This is check 5, past the cap of three, approved by the human for this one fix (notes.md, option A).
