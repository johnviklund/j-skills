# check-1 @ e08114c · claude-opus-5.5 · high
| # | Verdict | Evidence |
|---|---|---|
| 1 | PROVED | `jflow.py seat {spec,build,fix,done,check}` in a fresh git repo → Opus 5.5 medium, fallback null for four; check: gpt-6.1-sol high, fallback gpt-6-astra high |
| 2 | PROVED | repo build, env check, then `--config` check → `repo-b` for build, `env-c` for check, `claude-opus-5.5` for spec; with the flag, `flag-c` for check |
| 3 | PROVED | `seat build` with broken JSON, then effort 5 → exit 1, `<path>/.jflow/config.json: cannot read valid config JSON` / `...: seat model, vendor and effort must be nonempty strings`, no seat printed |
| 4 | PROVED | builder on gpt-6.1-sol/openai: `seat check` → `claude-opus-5.5 ... high`; with `"different_vendors": false` → `gpt-6.1-sol` |
| 5 | PROVED | `seat build` → `"rules": {"public_paid_needs_human": true, "checker_read_only": true, "no_secrets": true}`; each rule set false → exit 1, `locked rule <name>`, no seat |
| 6 | PROVED | sk-ant-, ghp_, AKIA and 40-char tokens as model → exit 1, `secret-like value refused`, echoed=0; `record t spec --model ghp_...` → exit 1, run.jsonl sha1 unchanged |
| 7 | PROVED | `seat` for every step in flow.json → role matches for all 7; `seat bogus` → exit 1, `unknown flow step` |
| 8 | PROVED | `grep -n "claude-opus-5.5\|gpt-6.1-sol\|Opus 5.5 · high" SKILL.md references/*.md` → no match (exit 1); SKILL.md:30 and :108 point to `jflow.py seat` |
| 9 | BROKEN | defect 1 |
| 10 | PROVED | `git diff --numstat bc5d3cb -- .../jflow.py` → `81 2` (net +79 ≤ 90); skill files without `__pycache__` → 49,932 bytes ≤ 50 KB |

## Defects
- 1. `scripts/jflow.py` `secret()` applied to all of argv in `main()`: slug `task-list`, or `--repo /tmp/example/projects/long_repository_directory` → `secret-like argument refused`, exit 1 → record, summary and seat run as at bc5d3cb. Evidence: run, `jflow.py record task-list spec --model claude-opus-5.5 --effort high` → `secret-like argument refused`; bc5d3cb exits 0

## Maybes
- Checker and builder vendors differ: GPT-6.1 Sol built, Opus 5.5 checked, which is the configured other-vendor seat.
- Build ran on 2026-11-08, before the spec's "no earlier than 2026-11-14" trial wait; notes.md says the build request superseded it.
- Row 10's skill size has 68 bytes of headroom under 50,000; the fix for defect 1 may push it over.
- `seat --repo /tmp`, outside a git repo, ends in a Python traceback instead of one error line.
