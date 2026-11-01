# Roadmap

Updated: 2026-11-01. This repo holds the `j-skills` skills (`workflow`, `checkup`, `evals`,
`memory.remember`, `memory.compact`, `agent-docs`, `plain`, `retro`, `understand`, `verify`,
`design`).
Undecided intake lives in `TODO.md`; what shipped lives in `WORKLOG.md` and git.

## Goal: v3, runs an outside conductor can drive unattended

Decided 2026-10-26. A script, not model judgement, decides a run's next step, and j-skills stays
neutral about which app or agent reads it. Driving runs unattended (handing phases to other
vendors' models, live questions, wake-ups) belongs to a separate conductor skill in its own repo.
Dependencies point one way: the conductor uses j-skills, and j-skills never names the conductor
or its app. The conductor is optional; without it, j-skills works by hand as before.

No open steps. Step 3, the conductor skill, shipped in its own repo (see `ROADMAP_ARCHIVE.md`).

## Goal: keep the code base and test suites from growing unchecked

Shipped 2026-10-17/18 (runs `lean-runs`, `growth-ratchets`, `guard-keys`): brief ≤ 8 behaviours,
plan ≤ 20 acceptance lines, tests net ≤ 1.5× code per ticket, keyed waivers, one test per
behaviour and per guard key. Their trials closed 2026-10-21 as kept (`SKILL-IMPACT_ARCHIVE.md`).

No open steps. Steps 1 to 4 are in `ROADMAP_ARCHIVE.md`; the last, `lean-workflow-tests`, closed 2026-10-31.

## Goal: a harness that is pruned on evidence and enforced by code

Decided 2026-11-01, from a review of harness-engineering advice checked against its sources. Most
of it j-skills already does. Three gaps: two ground rules are prose only, no skill change has ever
been reverted (every "no signal" trial ends kept), and a correction becomes a rule only when an
agent logs it or someone runs `retro` on that session. One run per step, in this order.

| # | Step | Slug | Status |
|---|---|---|---|
| 2 | "No signal" means retire, not keep: a learnings tag records when a skill rule visibly stopped a mistake, `checkup seats` counts it per `SKILL-IMPACT.md` row, and a trial that ends with no save becomes a removal candidate for `workflow improve`. A rule guarding a rare, costly failure stays, marked `insurance: <incident>` from its `From` column. Also judges the open `trialing` rows | `retire-on-no-signal` | next |
| 3 | Mine corrections from every session: a stdlib script reads the transcript stores `retro` lists and pulls human redirect turns, interrupts and denied tool calls over the last N days, by repo. `checkup` reports the top repeats; `retro` uses them for its *Recurring* test | `correction-mining` | after 2 |
