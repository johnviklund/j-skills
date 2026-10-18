# Roadmap

Updated: 2026-10-18. This repo holds the `j-skills` skills (`workflow`, `checkup`, `evals`,
`memory.remember`, `memory.compact`, `agent-docs`, `plain`, `retro`, `understand`, `verify`).
Undecided intake lives in `TODO.md`; what shipped lives in `WORKLOG.md` and git.

## Goal: keep the code base and test suites from growing unchecked

Shipped 2026-10-17/18 (runs `lean-runs`, `growth-ratchets`, `guard-keys`): brief ≤ 8 behaviours,
plan ≤ 20 acceptance lines, tests net ≤ 1.5× code per ticket, keyed waivers, one test per
behaviour and per guard key. All are trialing in `SKILL-IMPACT.md`.

| # | Step | Run name | Status |
| --- | --- | --- | --- |
| 1 | Judge the three trials on the next 3 cx-intelligence runs (`topic-assistant` is the first under all rules, then `cli-split`): smaller runs, fewer test lines, no false errors, no squeezing to fit the limits | `checkup` | In progress |
| 2 | Retire the date gates (`SLOP_SINCE`, `SIZING_SINCE`, `LEAN_SINCE`, `GROWTH_SINCE`) and their legacy branches (`LEGACY_TEST_RATIO`, any-mention deviation skip); check only runs not yet done, so a rule change needs no start date | `retire-date-gates` | Planned |
| 3 | Decide from step 1's evidence which comes next: a simplify pass before review, real retiring at wrap, or a run-level ratio gate (growth-ratchets D4) | — | Waiting on step 1 |

Step 2 can run any time; it touches only `check-run.py`, its tests and the references.
