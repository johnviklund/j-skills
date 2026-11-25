# Roadmap
Updated: 2026-11-25

This repo holds the `j-skills` skills. Undecided intake lives in [TODO.md](TODO.md), what shipped
lives in [WORKLOG.md](WORKLOG.md) and git, and done items and earlier goals sit in
[ROADMAP_ARCHIVE.md](ROADMAP_ARCHIVE.md). The jflow trial ended on 2026-11-16: jflow stays, and
workflow was deleted on 2026-11-25 (delete-workflow). Start every item with
`jflow spec <slug>`; a `plain` item is small enough for spec, build and check in one session.
Budgets count sessions or changed lines.

## Next up

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

## Measurement

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
