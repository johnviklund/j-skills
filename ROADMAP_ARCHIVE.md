# Roadmap archive

Completed steps, moved from `ROADMAP.md` at wrap.

| 2 | Retire the date gates (`SLOP_SINCE`, `SIZING_SINCE`, `LEAN_SINCE`, `GROWTH_SINCE`) and their legacy branches (`LEGACY_TEST_RATIO`, any-mention deviation skip); check only runs not yet done, so a rule change needs no start date | `retire-date-gates` | Done 2026-10-22: one rule set for every run not yet done; done runs keep header, sha and layout checks; see `.workflow/retire-date-gates/wrap.md` |
| 3 | Decide from step 1's evidence which comes next: a simplify pass before review, real retiring at wrap, or a run-level ratio gate (growth-ratchets D4) | `run-ratio-and-retire` | Done 2026-10-23: check-run judges tests net against code added once per run (error above 1.5×, `Ratio waived: run`); the per-ticket ratio is a warning; checkup reports test growth. Simplify pass is next, after the 2026-10-21 `workflow improve` trial; see `.workflow/run-ratio-and-retire/wrap.md` |
