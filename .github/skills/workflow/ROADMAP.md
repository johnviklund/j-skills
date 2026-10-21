# Roadmap

Updated: 2026-10-21. This repo holds the `j-skills` skills (`workflow`, `checkup`, `evals`,
`memory.remember`, `memory.compact`, `agent-docs`, `plain`, `retro`, `understand`, `verify`).
Undecided intake lives in `TODO.md`; what shipped lives in `WORKLOG.md` and git.

## Goal: keep the code base and test suites from growing unchecked

Shipped 2026-10-17/18 (runs `lean-runs`, `growth-ratchets`, `guard-keys`): brief ≤ 8 behaviours,
plan ≤ 20 acceptance lines, tests net ≤ 1.5× code per ticket, keyed waivers, one test per
behaviour and per guard key. Their trials closed 2026-10-21 as kept (`SKILL-IMPACT_ARCHIVE.md`).

| # | Step | Run name | Status |
| --- | --- | --- | --- |
| 1 | Judge the three trials on the next 3 cx-intelligence runs (`topic-assistant` is the first under all rules, then `cli-split`): smaller runs, fewer test lines, no false errors, no squeezing to fit the limits | `checkup` | Done 2026-10-21: briefs and plans shrank to the caps (behaviours 11.2 → 6.6, acceptance 31 → 20.5) but net code per run did not (+331 → +361); 7 of 16 per-ticket ratio hits were false, absorbed by 14 waivers |
| 2 | Retire the date gates (`SLOP_SINCE`, `SIZING_SINCE`, `LEAN_SINCE`, `GROWTH_SINCE`) and their legacy branches (`LEGACY_TEST_RATIO`, any-mention deviation skip); check only runs not yet done, so a rule change needs no start date | `retire-date-gates` | Planned |
| 3 | Decide from step 1's evidence which comes next: a simplify pass before review, real retiring at wrap, or a run-level ratio gate (growth-ratchets D4) | — | Evidence points to the run-level ratio gate (growth-ratchets D4): run-level tests ÷ code is already under 1.5× (0.97 cx-intelligence, 1.46 agent-cv) and all 7 false hits were ticket-level (test-first prefactors, code under Budget); gate the run, keep the per-ticket ratio as a warning. Simplify pass is next, after the 2026-10-21 `workflow improve` trial |

Step 2 can run any time; it touches only `check-run.py`, its tests and the references.
