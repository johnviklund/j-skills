# Roadmap

Updated: 2026-11-08. This repo holds the `j-skills` skills (`workflow`, `checkup`, `evals`,
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
not write, then attacking what that key never asked, catches what review catches, for less.

**The skill.** `jflow`, in `.github/skills/jflow/`, with a hub of at most ~8 KB.

| Step | Seat | Job | Output |
|---|---|---|---|
| `jflow spec <slug>` | From config, with the human | Grill the what, never the how | `spec.md`, about one page |
| `jflow build <slug>` | From config | One session builds it all; no plan phase, no tickets | Commits and a few lines of judgement calls |
| `jflow check <slug>` | From config | Fresh context runs the Proof table on the real app, then attacks what it never asked | PROVED, BROKEN, BLOCKED or UNREACHABLE per row, plus defects with a failing input, in one receipt |

- **Spec:** problem, goals, non-goals, constraints with "ask first" boundaries, Proof table. A line
  belongs only if the human would object to the builder choosing differently. Facts are looked up,
  not asked. The interview stops when the agent can predict the human's next three answers.
- **Proof table:** claim, surface, check, pass signal. Every row can fail: a script, test or query,
  a flow driven with `verify-APP`, or a measurement with a threshold. Taste is a human check and
  never counts as proof. Rows for new behaviour must fail on the base commit before the build
  starts. The builder never edits the table.
- **Fixes:** BROKEN rows and defects go back to the same builder session together, three checks at
  most. If that session is gone, a new one gets the branch and the open items.
- **Defects** need a failing input. Maybes go to the human and nobody fixes them.
- **Writer and checker** default to different vendors; JSON config supplies seats and this policy.
- **Record:** `.jflow/<slug>/` holds the spec and receipts, outside the `.workflow/` run hook, plus
  a worklog entry of about five lines. Lessons only when the human corrected the agent.
- **Any CLI:** every step is a plain message and a fresh session works anywhere. The skill keeps
  `flow.json` and layered seat config and calls no `workflow` script.

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
5. Done 2026-11-07, except the Sol builder, which moved to step 8. Three work-repo tasks ran on
   `jflow` on the real app, all with Opus builders. Planned as two with an Opus builder and one with
   a Sol builder, with review on all three as a safety net, since step 4 missed its bar. Log
   sessions, fix rounds, usage, the human's minutes, each defect found, and bugs found within a
   week of shipping. Task 1 and one private-repo run took 7 sessions each. Prove alone had by then
   caught 2 of 8 known defects, counting the replay, and the 4 that review added would have shown
   wrong data or hidden an answer.
6. Done 2026-11-05. Prove and review merged into `jflow check`, to remove the handoff that made
   every run at least four sessions. One Sol session on the private run's pre-review code found both
   defects in 13 minutes, for 26k output tokens against 22k for the separate sessions, plus one
   finding on a made-up input and one that real dates contradicted. A deletion pass in the same
   session found 2 lines, so it stayed out, and the builder now cuts its own diff. Planted bugs
   showed 9 of 23 new tests caught nothing the others missed, and new tests per line of net code ran
   1.6 and 1.9 on `jflow` against a work-repo `workflow` median of 1.1, so tests now follow the rows.
7. Done 2026-11-07, after two runs on 2026-11-06. A check on a real-data cutover found a market page
   showing global numbers on all but one of its topics, which the builder had noted and left. That
   code was outside the diff, and the builder's own proof passed. The same check ran after the
   delete, so it could not prove a guard whose starting state was gone, and that row shipped on the
   builder's run. Three changes followed. A spec names a gate, the first live step that cannot be
   undone or that removes a row's starting state, and a check clears it first. `## Accepted` records
   what the human accepts, with the bar left as written, in place of editing the key. A row about a
   conclusion names the numbers that would disprove it.
8. Open. Run the next three runs under step 7, one with a Sol builder and Opus at check. Log the same
   numbers as step 5.

**Verdict.** The recent work-repo median is 6.5 sessions a run. The original bar was a `jflow`
median of 3 or fewer. Eight runs gave a median of 6, so that goal was missed. The human decided on
2026-11-07 not to apply the loss rule: three sessions needs no fixes and no reopened spec, while
`jflow` cut commits to about a third, cut tests per line of code and caught a wrong-data bug that
review would probably have missed. The new bar is a median of 4 or fewer on the three runs of step
8. Today's runs would miss it too, so it was not set to fit them.

Decide once step 8 is in, and no earlier than 2026-11-14, when the one-week bug window of the last
runs ends. `jflow` wins with that median, with `jflow check` catching at least two thirds of the
real defects, and no shipped bug that loses data or shows wrong data as correct. A win ports what
outlives `workflow` to `jflow`: the next-step, worktree and hook scripts, because the conductor and
the unattended path need them. It then removes `workflow` and the scripts only it uses, and that
release is v4. A class of bug check misses gets one targeted row, not a phase. A loss removes
`jflow` and lifts the freeze.

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
