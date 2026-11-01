Command: workflow plan retire-on-no-signal
Created: 2026-11-01 · claude-opus-5-5
Base:    d116760
Inputs:  .workflow/retire-on-no-signal/brainstorm.md @ 952031e
Status:  complete

Docs read: none in scope (no PRODUCT.md or DESIGN.md)
Size: code 0 · tests 0 · ratio n/a (the script and its test are new files) · largest touched seats.md 76, learning-worklog.md 136, SKILL-IMPACT.md 71 (Markdown) · over 1,000: none
Decisions: tickets approved 1a · 1a (keep D2's numbers arm; every line prints before and after numbers) · 2a (repo folders as arguments, default `.`)

## Execution state
Current: patch cycle 2 C2-T1 done; C2-T2 ready.
T1 @ 3aeab1c
T2 @ 1ad5a7d
T3 @ dcaedc4
writer: GPT-6.1 Sol
Session 1: T1, T2
Session 2: T3
Session 3: C1-T1, C1-T2, C1-T3
Session 4: C1-T4, C1-T5
Session 5: C2-T1
Baseline: workflow 124 tests OK; checkup 12 tests OK. No pre-existing failures.
T1 final: workflow 124 tests OK; checkup 12 tests OK.
T2 final: workflow 124 tests OK; checkup 15 tests OK.
T3 final: workflow 124 tests OK; checkup 15 tests OK.
Uncommitted: none after record commit. Pending decision: none.

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

## Tickets

### T1 — Save tags count per row, and `--sweep` labels every trialing row
Delivers: B1, B4, B5, B6 · Blocked by: none · Lane: logic
Budget: code +100 · tests +100
Seam: stdout of `python3 .github/skills/checkup/scripts/skill-trials.py --sweep [--impact PATH] [REPO ...]` on a fixture `SKILL-IMPACT.md` and fixture repos; the docs by grep
Accept:
- [x] One `2026-11-01 · workflow` row; `- [saved→skill] 2026-11-01 workflow — stopped a bad push` in each of two repo args → `--sweep A B` prints a line starting `keep · 2026-11-01 · workflow · 2 saves` (B1)
- [x] Two `2026-10-30 · workflow` rows; a tag `[saved→skill] 2026-10-30 workflow run routing — …` with `run routing` only in the second Change → second row `1 save`, first `0 saves` (B5)
- [x] The same two rows and a tag with no words → `⚠️ tag .workflow/<slug>/learnings.md:<n> matches 2 rows; add words of the change`, and both rows `0 saves` (B5)
- [x] A row with From `insurance: lost a release` and 0 saves → its line starts `insurance ·`, never `candidate ·` (B4)
- [x] `--sweep` prints exactly one line per `trialing` row, none for a `kept` row, and leaves every fixture file's bytes unchanged (B6)
- [x] `learning-worklog.md` lists `- [saved→skill] <row date> <skill> [words of the change] — <what it stopped>`; the `SKILL-IMPACT.md` header names `insurance: <incident>`; no row ends `| trial |` (B1, B4)
Verify: `python3 -m unittest discover -s .github/skills/checkup/scripts/tests -p test_skill_trials.py && grep -q 'saved→skill\] <row date> <skill>' .github/skills/workflow/references/learning-worklog.md && grep -q 'insurance: <incident>' .github/skills/workflow/SKILL-IMPACT.md && ! grep -q '| trial |$' .github/skills/workflow/SKILL-IMPACT.md` (pre: new file · `NO TESTS RAN`, exit 5)
Skills: .github/skills/agent-docs/SKILL.md
Status: done @ 3aeab1c
Writer: GPT-6.1 Sol

### T2 — A finished trial is judged on saves and worklog numbers in `checkup seats`
Delivers: B2, B3 · Blocked by: T1 · Lane: logic
Budget: code +60 · tests +80 · why: each case needs worklog entries before and after its row
Seam: stdout of `python3 .github/skills/checkup/scripts/skill-trials.py [REPO ...]` (no `--sweep`) on fixture repos; `seats.md` by grep
Accept:
- [x] `3 runs` row, 0 saves, cycles plus deviations averaging 4 before and 2 after → `✅ <date> <skill> · trial complete · kept · numbers better (before 4.0 → after 2.0)` (B3)
- [x] The same row averaging 4 after → `⚠️ <date> <skill> · trial complete · 0 saves · numbers not better (before 4.0 → after 4.0) · removal candidate → workflow improve <skill>` (B2)
- [x] A finished row with 1 save and a higher average after → its line holds `kept · 1 save`, not `removal candidate` (B3)
- [x] A `3 runs` row with 2 later entries → no line without `--sweep`; a `3 checkups` row → line ends `open · count checkups by hand` (B2)
- [x] `seats.md` *Skill trials* runs `scripts/skill-trials.py` and names `workflow improve` for a candidate; the tree-hash mapping text `git rev-parse <commit>:<skill folder>` is gone (B2)
Verify: `python3 -m unittest discover -s .github/skills/checkup/scripts/tests -p test_skill_trials.py && grep -q 'scripts/skill-trials.py' .github/skills/checkup/references/seats.md && ! grep -q 'rev-parse <commit>:<skill folder>' .github/skills/checkup/references/seats.md` (pre: new file · `NO TESTS RAN`, exit 5)
Skills: .github/skills/agent-docs/SKILL.md
Status: done @ 1ad5a7d
Writer: GPT-6.1 Sol

### T3 — The first sweep over this repo's open trials, confirmed by the human
Delivers: B6 · Blocked by: T1, T2 · Lane: operator
Budget: code +0 · tests +0
Runner: agent after approval · Risk: cheap (Markdown edits to `SKILL-IMPACT.md`, reverted with git; no removal of any rule)
Seam: `receipts/t3-sweep.txt` and the Outcome column of `SKILL-IMPACT.md`
Handoff: run `python3 .github/skills/checkup/scripts/skill-trials.py --sweep . > .workflow/retire-on-no-signal/receipts/t3-sweep.txt`, this repo only. Show the human each row's label in the plan's decision shape; record the answers in `decisions.md`. A confirmed keep row's Outcome becomes `kept — <saves or numbers> (<date>)`; a confirmed insurance row gets `insurance: <incident>` in From and `kept`; a candidate stays `trialing`, so `checkup seats` keeps naming it for `workflow improve`.
Accept:
- [x] receipt → 37 lines matching `^(keep|insurance|candidate) · ` and 0 `⚠️ tag` lines (D3)
- [x] after recording → `skill-trials.py --sweep .` prints no line starting `keep ·`, and each human answer has a `decisions.md` row (D3)
Verify: `receipt: receipts/t3-sweep.txt — 37 rows · 0 tag lines; then the sweep shows no keep line` (pre: no receipt)
Skills: none
Status: done @ dcaedc4
Writer: GPT-6.1 Sol

## Coverage
- Outcome → T2 (`checkup seats` runs the script and names a finished trial with no save and no gain as a candidate for `workflow improve`)
- B1 → T1 · B2 → T2 · B3 → T2 · B4 → T1 · B5 → T1 · B6 → T1, T3
- Out of scope: `correction-mining` → untouched

## Risks
T2 is the riskiest: its numbers judge a date window, so same-day rows share one verdict (F6). Decision 1a accepted that; every line prints both numbers, and T3's human confirmation catches a row kept by its date.
Outside its files, T2 changes what every `checkup seats` reports: the tree-hash comparison in `seats.md` goes. Option not taken: saves and insurance only (1b).

## TODO impacts
None named by the brief.

## Product doc impacts
No `PRODUCT.md` or `DESIGN.md`. `ROADMAP.md` step 2 (`retire-on-no-signal`) is completed by this run; wrap archives the row.

## Deviations
T3 receipt keeps labels, row references and numbers rather than full Change prose. The full-output checksum and temporary path preserve provenance without duplicating home-path examples.
