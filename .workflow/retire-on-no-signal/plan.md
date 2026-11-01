Command: workflow plan retire-on-no-signal
Created: 2026-11-01 · claude-opus-5-5
Base:    d116760
Inputs:  .workflow/retire-on-no-signal/brainstorm.md @ 952031e
Status:  drafting

Docs read: none in scope (no PRODUCT.md or DESIGN.md)
Size: code 0 · tests 0 · ratio n/a (the script and its test are new files) · largest touched seats.md 76, learning-worklog.md 136, SKILL-IMPACT.md 71 (Markdown) · over 1,000: none
Decisions: pending

## Execution state

## Findings
| # | What is true | What it changes |
|---|---|---|
| F1 | `SKILL-IMPACT.md` has 59 rows, each 6 cells with no `\|` inside a cell; 36 are `trialing`. The table has no `##` heading | The script reads lines starting `\| 20` and splits them with `strip("\|").split("\|")` |
| F2 | The Skill cell can list several skills joined by ` · `, and some carry a `(new)` suffix (`design (new)`, `plain (new)`) | A tag matches a row when its skill is any of the listed skills, with `(new)` dropped |
| F3 | 9 date and skill pairs repeat among `trialing` rows: `2026-10-30 workflow` 7 times, `2026-10-29 workflow` 7 times | B5 is the common case. Rule: the words between the skill and ` — ` must appear, ignoring case, in exactly one matching Change cell; none or several prints the tag as unmatched or ambiguous |
| F4 | The Trial until cell opens with a count and a unit. 29 of 59 say `runs`; the rest count checkups, exams, lands, setups, handoffs, explainers, retros or weeks. Dated notes follow after ` · ` | A trial is finished when its unit contains `runs` and that many later worklog entries list the skill. Any other unit prints `open — count <unit> by hand` |
| F5 | `WORKLOG.md` keeps 15 entries, oldest 2026-10-17. Each has `- Run:` with review cycles and deviations, and `- Skills: <skill>@<sha>, …` | Better numbers compare entries by date and skill name, with no sha mapping. A row with no earlier entry for its skill has no before set and is never better |
| F6 | A dry run of that comparison on today's data, mean review cycles plus deviations of the first N entries after against the last N before: 11 better, 13 not, 12 no data. All 7 `2026-10-29 workflow` rows come out better and all 7 `2026-10-30 workflow` rows not, because they share the same runs | The numbers judge a date window, not a change. Decision 1 |
| F7 | No `learnings.md` holds a `[saved→skill]` line; the tag list lives in `learning-worklog.md:14-21` | The doc ticket adds the tag there. The first sweep finds 0 saves on every row by construction |
| F8 | No From cell holds `insurance:` | The first sweep shows no insurance rows until the human adds a note when confirming |
| F9 | The 2026-11-01 git-hooks row sits at the bottom of the table with Outcome `trial`, not `trialing` | The doc ticket moves it to the top and sets `trialing`, so the sweep sees it |
| F10 | Reuse: `check-run.py:150` `table()` needs a `##` heading the table lacks, and `config-scan.py` imports nothing from workflow. No worklog parser exists; `seats.md` greps it. `test_config_scan.py:14-38` runs the script as a subprocess in a temp dir | The script splits rows itself and imports nothing. Its test copies the subprocess and temp-dir pattern |
| F11 | Installed copies sit side by side: `~/.agents/skills/checkup` next to `~/.agents/skills/workflow`, and `.github/skills/` in this repo | `--impact` defaults to `<script folder>/../../workflow/SKILL-IMPACT.md`, which resolves in every install folder |
| F12 | Many trials are judged on work-repo runs, whose runs and `WORKLOG.md` checkup never sees from this repo | Decision 2 |
