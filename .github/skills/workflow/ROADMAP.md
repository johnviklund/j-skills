# Roadmap

Updated: 2026-10-22. This repo holds the `j-skills` skills (`workflow`, `checkup`, `evals`,
`memory.remember`, `memory.compact`, `agent-docs`, `plain`, `retro`, `understand`, `verify`).
Undecided intake lives in `TODO.md`; what shipped lives in `WORKLOG.md` and git.

## Goal: keep the code base and test suites from growing unchecked

Shipped 2026-10-17/18 (runs `lean-runs`, `growth-ratchets`, `guard-keys`): brief ≤ 8 behaviours,
plan ≤ 20 acceptance lines, tests net ≤ 1.5× code per ticket, keyed waivers, one test per
behaviour and per guard key. Their trials closed 2026-10-21 as kept (`SKILL-IMPACT_ARCHIVE.md`).

| # | Step | Run name | Status |
| --- | --- | --- | --- |
| 1 | Judge the three trials on the next 3 cx-intelligence runs (`topic-assistant` is the first under all rules, then `cli-split`): smaller runs, fewer test lines, no false errors, no squeezing to fit the limits | `checkup` | Done 2026-10-21: briefs and plans shrank to the caps (behaviours 11.2 → 6.6, acceptance 31 → 20.5) but net code per run did not (+331 → +361); 7 of 16 per-ticket ratio hits were false, absorbed by 14 waivers |
