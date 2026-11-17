# Roadmap
Updated: 2026-11-17

This repo holds the `j-skills` skills. Undecided intake lives in [TODO.md](TODO.md), what shipped
lives in [WORKLOG.md](WORKLOG.md) and git, and done items and earlier goals sit in
[ROADMAP_ARCHIVE.md](ROADMAP_ARCHIVE.md). The jflow trial ended on 2026-11-16: jflow stays, and
workflow goes once what other skills still need from it has moved. Start a `jflow` item with
`jflow spec <slug>`, and a `plain` item with one session sent `Roadmap item <slug>`. Budgets count
sessions or changed lines.

## Next up
1. jflow-size-room · one session, and every jflow change waits for it, check-scope first
2. check-scope · the costliest wait: check outlasts build in half the runs and stops the human most
3. jflow-next-properties · the conductor trusts `next` at every step, and unattended runs need it tested
4. delete-workflow · two skills for one job cost every session that reads them; it waits for nothing
5. escaped-defects · the first conductor run opens a bug window that should land in its run folder

## Features

### change-recording · a short video of each user-facing change

- **Status:** open
- **Problem:** hq's north star says each queue item carries a short video of the change, and
  nothing records one. Only hq's web UI would show it, and that waits for hq's Phase 4 gate.
- **Impact:** a reviewer sees a screen change working without running the app; no run has measured
  how many minutes that saves.
- **Why now:** nothing shows the video until hq's web UI exists, so it waits.
- **Solved when:** a change to a screen comes with a recording of it working, made during check and
  linked from the receipt.
- **Budget:** not set
- **Run:** jflow · j-skills
- **After:** none
- **Open for spec:** is the recording a required Proof row for UI changes, and from when?

## Tooling

### jflow-size-room · a jflow change fits under the size test

- **Status:** open
- **Problem:** The size test in `jflow/scripts/tests/test_validate.py` caps jflow at 50,000 bytes,
  and jflow measured 49,995 on 2026-11-17. Three changes already wait for room: the `spec-why`
  deferral in `TODO.md` and two check-scope ideas of about 72 words.
- **Impact:** every jflow change can land without first cutting other text to fit.
- **Why now:** check-scope waits for it.
- **Solved when:** a jflow change that adds about 150 words, check-scope's budget, passes the size
  test with no cut elsewhere, and the limit's reason is written beside it.
- **Out of scope:** rewriting jflow for style.
- **Budget:** one session
- **Run:** plain · j-skills
- **After:** none
- **Open for spec:** raise the limit, move text into more reference files, or cut text no run has
  used?

### check-scope · check proves and reports, and leaves decisions to others

- **Status:** open
- **Problem:** Check took longer than build and fix together in 13 of 28 runs, 2,217 against 1,490
  minutes in all, and wrote 381 Maybes in 111 checks, 3.4 a check, each a stop for the human before
  done. Check also decides instead of proving: one work-repo run had 5 cap raises, and in the three
  worst runs 12 checks found no defect and only moved BLOCKED or WAITING rows while the checker
  planned how to unblock them. Sol and Opus checkers both write 3.4 Maybes a check, so check's rules
  cause it, not the model.
- **Impact:** ~4 fewer sessions a run in the three worst runs, from those 12 checks, and fewer stops
  for the human than 3.4 Maybes a check.
- **Why now:** every run pays it, and an unattended conductor run stops at each cap raise and Maybe.
- **Solved when:** over the next five runs, the median falls below today's 3.5 checks a run, Maybes
  average under half of 3.4 a check, no check reruns rows when nothing was supplied since the last
  one, and every receipt stays under 3 KB.
- **Out of scope:** paid-call budgets and approval rules themselves.
- **Budget:** about 150 words of jflow text and one session to measure
- **Run:** jflow · j-skills
- **After:** jflow-size-room
- **Open for spec:** Which jobs leave check: unblock plans, cap-raise questions, Maybes that propose
  a fix? Does any decision check makes need a stronger model, or does it go to the builder or the
  human? Should a row that grades a model's judgement run on a fixed labelled case set the builder
  can run free? Should a keep row never need a paid call or approval, and read live values? Should
  check list what each row needs before it runs any? When fix rounds keep finding new defects, is
  the cause a spec that left behaviour open, a check that attacks without end, or fixes that break
  what passed?

### jflow-next-properties · jflow's next-step rules are tested on generated run folders

- **Status:** open
- **Problem:** The conductor trusts `jflow.py next` to pick every step and every stop for the human,
  and that logic keeps breaking in small ways. On 9 Nov the jflow-next and wait-points runs needed
  five fixes to it, each found by a full check session and not by the 14 tests.
- **Impact:** ~1 to 2 fewer fix rounds on each change to `next`, from those five fixes; a wrong
  `next` in a conductor run skips a stop or loops, and nobody is watching.
- **Why now:** the conductor's first unattended runs rely on it.
- **Solved when:** one command generates random run folders and fails if `next` skips a wait point,
  counts a rerun of only BLOCKED or WAITING rows toward the cap, or lets an Accepted or `Yes:` line
  clear anything other than what it names; it fails on at least one of the five past bugs.
- **Out of scope:** TLA+, Lean or any model of the flow outside the test file.
- **Budget:** about 120 lines of tests, no change to `jflow.py` unless a test finds a bug
- **Run:** jflow · j-skills
- **After:** none
- **Open for spec:** is Hypothesis worth a test dependency, or does a seeded random generator do?

### delete-workflow · delete workflow and the scripts only it uses

- **Status:** open
- **Problem:** Two skills do one job. workflow is 786 KB, its runs took 3 to 10 sessions and up to 7
  review cycles, and j-skills took 232 sessions in two weeks, mostly building rules for workflow.
  Checked on 16 Nov, six things still need it: the git hooks, `SKILL-IMPACT.md`, the `ROUTING.md`
  readers, the reviewer exam, `workflow todo` and understand's run reader.
- **Impact:** about 786 KB of skill text goes, and every session sees one skill for a change, not two.
- **Why now:** the verdict on 2026-11-16 keeps jflow, and until workflow goes each skill change has
  to keep both in step.
- **Solved when:** workflow and the scripts only it uses are gone, all other suites pass, `git push`
  still scans for secrets in every repo with the hooks, and no surviving skill points at workflow.
- **Out of scope:** carrying over multi-ticket plans, mutation testing, worktrees, unattended mode or
  the brainstorm, improve, park and realign commands.
- **Budget:** the deletion, plus about 100 changed lines to move what other skills need
- **Run:** plain · j-skills
- **After:** none
- **Open for spec:** where do the hooks and `SKILL-IMPACT.md` live next: jflow, checkup or the repo
  root? Do the `ROUTING.md` readers switch to jflow's `config.json`, or does `ROUTING.md` go?

## Measurement

### escaped-defects · a defect that leaves with a run is recorded against it

- **Status:** open
- **Problem:** A bug found after done is not recorded against the run that shipped it, so nobody can
  count escaped defects. Defects accepted at done are not tracked either: one work-repo run shipped
  a count that shows wrong data as correct, and another closed with all 12 rows accepted, then cost
  a 6-session follow-up run for 3 defects its second check had found.
- **Impact:** escaped and accepted defects become countable per run; today the count is 0 because
  nothing records them.
- **Why now:** the first conductor run opens a bug window, and its bugs should land in its folder.
- **Solved when:** one jflow command records a bug, or an accepted defect, in the folder of the run
  that shipped it, in any repo, with or without hq, and hq's scores count it from there.
- **Budget:** about 40 lines
- **Run:** jflow · j-skills
- **After:** none
- **Open for spec:** should an accepted defect go through the same command, or is the `## Accepted`
  section already enough to count?

### retro-reads-scores · retro and memory.compact read the run record

- **Status:** open
- **Problem:** retro and memory.compact judge a run from transcripts, while `run.jsonl` and hq's
  scores already hold its sessions, checks and defects.
- **Impact:** a retro starts from the run's measured numbers; no run has measured the time saved.
- **Why now:** it waits for hq's scores index.
- **Solved when:** retro and memory.compact read `run.jsonl` and the scores.
- **Budget:** not set
- **Run:** jflow · j-skills
- **After:** none
- **Open for spec:** which numbers retro needs first, and whether it reads hq's scores or only
  `run.jsonl`?
