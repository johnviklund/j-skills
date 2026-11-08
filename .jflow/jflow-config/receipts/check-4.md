# check-4 @ 832708f · claude-opus-5.5 · high
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
| 9 | BROKEN | defect 1 |
| 10 | PROVED | `git diff --numstat bc5d3cb -- .github/skills/jflow/scripts/jflow.py` → `84 3` (net +81 ≤ 90); skill files without `__pycache__` → 49,886 bytes ≤ 50,000 |

## Defects
- 1. `scripts/jflow.py` `secret()` via `main()` record scan: slug `sk-onboarding-checklist-v2`, a valid `SLUG` → `secret-like argument refused`, exit 1 → record it as bc5d3cb does. Evidence: run, `jflow.py record sk-onboarding-checklist-v2 spec --model m --effort high` → exit 1; bc5d3cb exit 0

## Maybes
- The digit branch causes this: any hyphenated `sk-` slug of 20+ characters with a digit (`sk-migrate-postgres-to-16`) is refused, and so is one with underscores and no hyphen (`sk-onboarding_checklist_x`). Both exit 0 at bc5d3cb.
- Fourth defect from guessing names apart from keys. The slug already passes `SLUG` and names an existing run folder; exempting it from the scan, as `--repo` is, would end this class while `--model` and `--effort` stay scanned.
- Check-3's input `sk-onboarding-checklist` now records with exit 0. Python 3.9: 13 jflow tests OK; record and summary for `sk-ui` and `sk-onboarding-checklist` exit 0.
- This is check 4, past the cap of three, approved by the human for this one fix only.
