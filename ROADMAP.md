# Roadmap

Updated: 2026-11-04. This repo holds the `j-skills` skills (`workflow`, `checkup`, `evals`,
`memory.remember`, `memory.compact`, `agent-docs`, `plain`, `retro`, `understand`, `verify`,
`design`).
Undecided intake lives in `TODO.md`; what shipped lives in `WORKLOG.md` and git.

## Goal: v4, a short path that proves work instead of arguing about it

Proposed 2026-11-04. Not decided until the trial below ends.

**Problem.** Runs cost too much for what they ship. In the last two weeks j-skills took 232 agent
sessions, mostly building rules for the workflow itself. Runs take 3 to 10 sessions and up to 7
review cycles. About 40% of j-skills "fix now" findings, and about half of the work repo's P1s, ask
for a missing test or kill a mutant; the real bugs among the rest mostly show when the app runs.
Briefs drift into the how, because the brief template asks for test seams and file-level decisions.

**Bet.** A fresh agent proving the change on the real app, against an answer key the builder did
not write, catches most of what review catches, for less. Review becomes a short pass used by risk.

**The skill.** `jflow`, in `.github/skills/jflow/`, with a hub of at most ~8 KB.

| Step | Seat model | Job | Output |
|---|---|---|---|
| `jflow spec <slug>` | Opus 5.5, with the human | Grill the what, never the how | `spec.md`, about one page |
| `jflow build <slug>` | Opus 5.5 | One session builds it all; no plan phase, no tickets | Commits and a few lines of judgement calls |
| `jflow prove <slug>` | GPT-6.1 Sol, high; Terra, medium, for ready commands | Fresh context runs the Proof table on the real app | PROVED, BROKEN, BLOCKED or UNREACHABLE per row, with receipts |
| `jflow review <slug>` | GPT-6.1 Sol, high | Read-only pass, only when risk asks for it | Defects with a failing input shown by a run or traced, plus a list of maybes |

- **Spec:** problem, goals, non-goals, constraints with "ask first" boundaries, Proof table. A line
  belongs only if the human would object to the builder choosing differently. Facts are looked up,
  not asked. The interview stops when the agent can predict the human's next three answers.
- **Proof table:** claim, surface, check, pass signal. Every row can fail: a script, test or query,
  a flow driven with `verify-APP`, or a measurement with a threshold. Taste is a human check and
  never counts as proof. Rows for new behaviour must fail on the base commit before the build
  starts. The builder never edits the table.
- **Fixes:** BROKEN rows and review defects go back to the same builder session, two rounds at most
  per step, never a third. If that session is gone, a new one gets the branch and the open items.
- **Review runs** on auth, secrets, money, data migrations, concurrency, or a contract other code
  depends on. A finding that asks for new code names a path a user can reach. Maybes go to the
  human and nobody fixes them.
- **Writer and checker** stay on different vendors. With an OpenAI builder, prove and review move
  to Sonnet 5.5 and Opus 5.5.
- **Record:** `.jflow/<slug>/` holds the spec and receipts, outside the `.workflow/` run hook, plus
  a worklog entry of about five lines. Lessons only when the human corrected the agent.
- **Any CLI:** every step is a plain message and a fresh session works anywhere. The skill keeps
  its own small seat table and calls no `workflow` script.

**Not in the path:** plan phase, tickets, patch plans, mutation findings, guard-failing findings,
test-ratio gates, `decisions.md`, per-phase learnings. Mutation and formal checks stay tools a spec
can name for high-stakes code.

**Freeze.** No new `workflow` scripts, checks or rules until the verdict, except a fix for
something that blocks work. Build `jflow` in plain sessions, not through `workflow` runs.

**Steps, in order.**

1. Done 2026-11-04. `evals.run reviewer`, 11 known defects on 10 past misses: Astra 10, Sol 9, Sol
   with a traced-failing-input rule 10, with 0, 1 and 0 false alarms. Astra did not beat Sol, so Sol
   takes the seat with the rule. `references/review.md` alone scored 10 with 2 false alarms; a
   stricter reachability bar scored 8 with 1, so the bar stayed out. The exam is diff-only, so the
   first real reviews test the run half.
2. Done 2026-11-04. GPT-6.1 Terra is in the Codex and work Copilot pickers, Astra is not in Copilot.
3. Done 2026-11-04. `.github/skills/jflow/`, first tried on the `corrections-bad-records` run.
4. Done 2026-11-04, bar not met. Two past work-repo runs, blind specs, proved on a machine with no
   live model or real data. Sol caught 1 of 3 real defects, plus five false BROKEN rows, mostly
   from having no human at the spec. Of the two misses, one showed only with a live model and one
   had no row. Terra could not write the drivers, so Sol takes the seat unless rows are ready commands.
5. Run the next three work-repo tasks on `jflow`: two with an Opus builder, one with a Sol builder.
   Log sessions, fix rounds, usage, the human's minutes and bugs found within a week of shipping.

**Verdict.** The recent work-repo median is 6.5 sessions a run. `jflow` wins at a median of 3 or
fewer, with the replay catching at least two thirds of the real defects, and no shipped bug that
loses data or shows wrong data as correct. A win removes `workflow` and the scripts only it uses,
and that release is v4. A class of bug prove misses gets one targeted check, not a phase. A loss
removes `jflow` and lifts the freeze.

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

No open steps. Steps 1 to 3 are in `ROADMAP_ARCHIVE.md`; the last, `correction-mining`, closed 2026-11-02.
