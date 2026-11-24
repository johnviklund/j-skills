# Roadmap
Updated: 2026-11-24

This repo holds the `j-skills` skills. Undecided intake lives in [TODO.md](TODO.md), what shipped
lives in [WORKLOG.md](WORKLOG.md) and git, and done items and earlier goals sit in
[ROADMAP_ARCHIVE.md](ROADMAP_ARCHIVE.md). The jflow trial ended on 2026-11-16: jflow stays, and
workflow goes once what other skills still need from it has moved. Start every item with
`jflow spec <slug>`; a `plain` item is small enough for spec, build and check in one session.
Budgets count sessions or changed lines.

## Next up
1. headless-done-wait-point · the conductor half is left: jflow now stops at a typed `edits` wait point, and conductor must read it so done exits 2, not 1, before Phase 2 runs conductor on every task
2. delete-workflow · two skills for one job cost every session that reads them; it waits for nothing
3. escaped-defects · the first conductor run opens a bug window that should land in its run folder

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

### headless-done-wait-point · conductor pauses cleanly for done-step doc and TODO approvals

- **Status:** started
- **Problem:** Headless `conductor` runs abort with exit 1 (`no progress`) at `jflow done` whenever
  `done` asks to approve `PRODUCT.md`, `DESIGN.md`, `TODO.md` or `drive.py` verb edits, forcing a
  manual session resume. Seen in 3 of 3 recent conductor runs (`hq-py39`, `jflow-issue-pr-mode` and
  a private-repo run on 2026-11-24).
- **Impact:** conductor `done` exit-1 aborts on doc or TODO edits drop from 3 of 3 runs to 0,
  removing a manual resume and wall-clock stall on every run.
- **Why now:** `hq` Phase 2 is unblocked and will run `conductor` on every task.
- **Solved when:** a conductor run whose `done` step proposes `PRODUCT.md`, `DESIGN.md` or `TODO.md`
  edits stops cleanly with exit 2 and a typed wait point, and finishes `done` after
  `conductor SLUG --answer yes` without a manual CLI resume.
- **Out of scope:** changing interactive `jflow done` questions or rewriting `jflow.py` beyond
  making room under its 30,000-byte cap.
- **Budget:** 2 runs. The `j-skills` run shipped on 2026-11-24: `jflow.py next --json` has a typed
  `wait_point`, and an unattended `done` writes `## Proposed edits` and stops until `Yes: edits`.
  The `conductor` run is left: `conductor.py` reads `wait_point` instead of blocker text, tells
  `done` it runs unattended, and exits 2 at `edits`.
- **Run:** jflow · j-skills
- **After:** none

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
