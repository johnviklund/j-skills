### 6. Seat & skill performance, reviewer exam set

Models earn seats on **trial runs**, not exams: every `jflow done` adds a `WORKLOG.md` entry, or a
`notes.md` line when the repo has no worklog, with a `jflow:` line (sessions · fix rounds · rows ·
accepted · check defects · net code, tests and docs). Each step's model is in the run's
`.jflow/<slug>/run.jsonl`. Checkup turns those into a per-seat comparison and *detects the need* to
promote, demote, or run the one exam. It never edits a seat.

```sh
grep -nE '^\s*- jflow:' WORKLOG.md 2>/dev/null | head -30             # recent run evidence
grep -h '"model"' .jflow/*/run.jsonl 2>/dev/null | tail -60           # model per step
python3 <jflow skill folder>/scripts/jflow.py seat check                 # incumbent checker
E="$HOME/.agents/j-skills-evals/strict-reviewer"
ls "$E"/*.md 2>/dev/null | grep -v RESULTS.md | wc -l                 # exam cases (cap 10)
grep -L '^## Must name' "$E"/*-*.md 2>/dev/null                        # cases missing their findings
tail -20 "$E"/RESULTS.md 2>/dev/null                                   # last exam results
ls -d evals/strict-reviewer 2>/dev/null                                # old per-repo set, to move
```

- **Per-seat table.** From the last ~10 runs, group by step → model and average fix rounds and
  check defects. Read the incumbent per seat from `python3 <jflow skill folder>/scripts/jflow.py
  seat <step>`, which merges jflow's `config.json` with the repo's `.jflow/config.json`. Print the
  table; it *is* the evaluation.
- **Pending skill proposals.** `find . ~/.agents -name 'SKILL.md.proposed' 2>/dev/null` and any
  `SKILL-IMPACT.md` row with outcome `proposed`: ⚠️ "awaiting your accept/reject — `mv` to accept,
  delete and mark `rejected` to decline". Never accept or reject on the human's behalf.
- **Skill trials.** Run `python3 <checkup skill folder>/scripts/skill-trials.py [REPO ...]`.
  Pass every repo whose worklog and `.jflow/*/notes.md` save tags supply trial evidence; no
  arguments means this repo. Python 3 is the only dependency; the impact table defaults to this
  skill's own `SKILL-IMPACT.md`.
  Copy its lines. A finished trial needs a save tag or better mean review cycles plus deviations.
  The script compares the first N later runs against the last N earlier runs for the row's skills.
  Dates define the window, so same-day changes share numbers; the comparison does not attribute gains to one rule.
  Other trial units require a manual count. A removal candidate becomes a `TODO.md` line naming
  the rule; confirm with the human before removing a rule. A From note `insurance: <incident>`
  protects it.
- **Corrections.** Run `python3 <checkup skill folder>/scripts/corrections.py` from the repo, using Python 3 and git.
  Report the first 5 lines under `repeats:` or say there are none; copy no redirect line into a file, because transcripts are private.
- **Trial in progress.** A model on a seat with only one run: ✅ note "trial, 1 run -- needs one
  more before judging".
- **Promotion candidate.** A non-incumbent with ≥2 runs that ties or beats the incumbent on fix
  rounds and check defects: ⚠️ recommend the human promote it in `.jflow/config.json` or jflow's
  `config.json` (quote the seat).
- **Regression.** The incumbent's last 2–3 runs clearly worse than its earlier average, or a
  candidate worse than the incumbent: ⚠️ say so with the numbers; the decision is the human's.
- **Code and test growth.** Sum `net code` and `tests` over the last ~10 `jflow:` lines and name
  the directory that grew most (`git diff --dirstat=lines <oldest run's Base> HEAD -- .
  ':(exclude).jflow'`). When none of those runs shrank the code: ⚠️ ten runs with no pay-down,
  recommend a `TODO.md` line "simplify <that directory>, same behaviour". When net tests exceed
  net code: ⚠️ recommend a `TODO.md` line "fewer tests, same coverage".
- **Missing evidence.** A run with `Status: done` in `spec.md` but no `jflow:` line: ⚠️ the done
  step is being skipped -- nothing can be judged until it isn't.
- **Reviewer exam set.** It lives in the private `j-skills-evals` repo, cloned at `~/.agents/j-skills-evals`;
  missing clone is ⚠️ (give `gh repo clone johnviklund/j-skills-evals ~/.agents/j-skills-evals`). A per-repo
  `evals/strict-reviewer/` is ⚠️ "move its cases into the exam set". More than 10 cases is ⚠️
  (rolling cap; recommend a human prune). A case without
  an inlined diff or its P0/P1 lines is ⚠️. Fewer than 3 usable cases is ⚠️ -- the exam cannot run;
  seed it from shipped diffs (the `evals` skill's *seeded* kind).
- **Unchecked reviewer.** The check seat's model from `jflow.py seat check` has no passing entry in
  the exam set's `RESULTS.md` and the set has ≥3 usable cases: ⚠️ recommend
  `evals.run reviewer`. No other seat is examined -- do not recommend exams for them.
