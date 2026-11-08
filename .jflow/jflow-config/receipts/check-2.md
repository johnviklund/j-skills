# check-2 @ f376c4b · claude-opus-5.5 · high
| # | Verdict | Evidence |
|---|---|---|
| 1 | PROVED | `jflow.py seat {spec,build,fix,done,check}` in a fresh git repo → claude-opus-5.5 medium, fallback None for four; check: gpt-6.1-sol high, fallback gpt-6-astra high |
| 2 | PROVED | repo build, `JFLOW_CONFIG` check, then `--config` → build `repo-b`, check `env-c`, spec `claude-opus-5.5`; with the flag, check `flag-c` |
| 3 | PROVED | `seat build` with `{bad`, then effort 5 → exit 1, `<path>/.jflow/config.json: cannot read valid config JSON` / `...: seat model, vendor and effort must be nonempty strings`; no seat printed |
| 4 | PROVED | builder gpt-6.1-sol/openai: `seat check` → `claude-opus-5.5 high`; with `"different_vendors": false` → `gpt-6.1-sol high` |
| 5 | PROVED | `seat build` → rules all three true; each rule false in config → exit 1, `locked rule <name>`, no seat |
| 6 | PROVED | sk-ant-, ghp_, AKIA, 40-char token as config model → exit 1, `secret-like value refused`, echoed=0; `record t spec --model ghp_…` → exit 1, run.jsonl sha1 unchanged |
| 7 | PROVED | `seat` for each of 7 flow.json steps → 7 role matches; `seat bogus` → exit 1, `unknown flow step` |
| 8 | PROVED | the row's `grep -n` on SKILL.md and references/*.md → exit 1, no match; SKILL.md:29 `Run ... jflow.py seat <step> and copy its assignment into each card` |
| 9 | BROKEN | defect 1 |
| 10 | PROVED | `git diff --numstat bc5d3cb -- .../jflow.py` → `83 3` (net +80 ≤ 90); skill files without `__pycache__` → 49,962 bytes ≤ 50,000 |

## Defects
- 1. `scripts/jflow.py` `secret()` via `main()` record scan: slug `sk-ui`, a valid `SLUG`, has no character before `sk-` → `secret-like argument refused`, exit 1 → record it as bc5d3cb does. Evidence: run, `jflow.py record sk-ui spec --model m --effort high` → refused; bc5d3cb exit 0

## Maybes
- Checker vendor differs from builder: GPT-6.1 Sol built and fixed, Opus 5.5 checked, the seat `seat check --builder-vendor openai` returns.
- The boundary lookbehind lets an embedded short key through: `record t spec --model x-ghp_ABCdef123456` exits 0 and writes it to run.jsonl. Real full-length GitHub tokens still hit the 40-character rule.
- Size headroom is 38 bytes. To fit, the fix cut SKILL.md lines such as "Bad config fails before printing a seat" and the closing card's pointer to `seat`.
- The fix commit rewrote a path in check-1.md, which is the checker's receipt, for privacy. No verdict changed.
- `seat --repo /tmp`, outside a git repo, still ends in a traceback. Carried from check-1, not rechecked.
