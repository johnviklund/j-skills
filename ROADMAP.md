# Roadmap

Updated: 2026-10-30. This repo holds the `j-skills` skills (`workflow`, `checkup`, `evals`,
`memory.remember`, `memory.compact`, `agent-docs`, `plain`, `retro`, `understand`, `verify`,
`design`).
Undecided intake lives in `TODO.md`; what shipped lives in `WORKLOG.md` and git.

## Goal: v3, runs an outside conductor can drive unattended

Decided 2026-10-26. A script, not model judgement, decides a run's next step, and j-skills stays
neutral about which app or agent reads it. Driving runs unattended (handing phases to other
vendors' models, live questions, wake-ups) belongs to a separate conductor skill in its own repo.
Dependencies point one way: the conductor uses j-skills, and j-skills never names the conductor
or its app. The conductor is optional; without it, j-skills works by hand as before.

| # | Step | Run name | Status |
| --- | --- | --- | --- |
| 2 | Rules a phase follows when nobody is watching, plus `decisions.md`; ships as 3.0.0 | `unattended-mode` | Open: after `next-step` |
| 3 | The conductor skill: reads the JSON and drives the runs | separate repo | Open: after `unattended-mode` |

## Goal: keep the code base and test suites from growing unchecked

Shipped 2026-10-17/18 (runs `lean-runs`, `growth-ratchets`, `guard-keys`): brief ≤ 8 behaviours,
plan ≤ 20 acceptance lines, tests net ≤ 1.5× code per ticket, keyed waivers, one test per
behaviour and per guard key. Their trials closed 2026-10-21 as kept (`SKILL-IMPACT_ARCHIVE.md`).

| # | Step | Run name | Status |
| --- | --- | --- | --- |
| 1 | Judge the three trials on the next 3 work-repo runs (`topic-assistant` is the first under all rules, then `cli-split`): smaller runs, fewer test lines, no false errors, no squeezing to fit the limits | `checkup` | Done 2026-10-21: briefs and plans shrank to the caps (behaviours 11.2 → 6.6, acceptance 31 → 20.5) but net code per run did not (+331 → +361); 7 of 16 per-ticket ratio hits were false, absorbed by 14 waivers |
| 4 | After 3 runs under the run-level ratio gate, read `checkup` test growth and decide: a simplify pass before review, real retiring at wrap, or nothing if growth has flattened | `checkup` | Open: no brainstorm until the numbers show growth is still a problem |
