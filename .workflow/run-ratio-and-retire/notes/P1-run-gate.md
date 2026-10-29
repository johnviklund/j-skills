P1 — which run-level tests÷code rule flags real test bloat but not refactors?
Variants (floor: tests net ≥ 100): A = tests net > 1.5× code added · B = tests net > 1.5× code net.
Range: plan.md Base .. last `done @` sha; receipts and `.workflow/` excluded. Runs created 2026-10-17 or later in work-repo (12), agent-cv (9), j-skills (5).
Script: `prototypes/P1-run-gate/measure.py <repo>...` (read-only, git numstat).
Result: A flags 1 of 26 runs (work-repo `live-run-guardrails`: tests +679, code added 442; planned that way, Budgets summed 760 tests vs 520 code).
B flags 5: refactor runs whose deletions shrink code net (`governed-execution-discovery` code net −21, `forkable-owner-artifacts` code net 7).
The same 26 runs carry 13 `Ratio waived:` lines for the per-ticket rule.
