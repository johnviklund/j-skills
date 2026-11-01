Command: workflow review retire-on-no-signal · patch cycle 2
Created: 2026-11-01 · Claude Opus 5.5
Base:    1fba169
Inputs:  .workflow/retire-on-no-signal/review.md @ 1fba169
Status:  complete

Three tickets for cycle 2, approved by the human as a third cycle ("1a"). C2-T1 fixes a crash, so it lands as two commits: first a failing test alone, recorded as `Red: <sha>`, then the fix, which leaves test files untouched. C2-T2 changes tests only. C2-T3 edits one README sentence.

## Execution state
Current: C2-T1 ready

## Tickets

### C2-T1 — The report reads escaped pipes and names a bad row
Delivers: B1, B2, B6 · Blocked by: none · Lane: logic
Fixes: C2-1 (P0)
Budget: code +6 · tests +14
Seam: exit code, stdout and stderr of `skill-trials.py` on fixture impact and archive files, and on this repo
Change: in `rows()` at `skill-trials.py:13`, split cells on unescaped pipes only: `re.split(r"(?<!\\)\|", line.strip())[1:-1]`. Cells keep their text as written. A row that still has a cell count other than 6 raises `ValueError` naming `<file>:<line>`, so `main()` exits 2 with that message. Site search: `rows()` is the only parser of `SKILL-IMPACT` rows; the `split("|")` calls in `check-run.py:156,596` read run artifacts and are out of scope.
Accept:
- [ ] An archive fixture row with `\|` inside its Change cell, as real archive row 17 has, plus a trialing impact row with `\|` in its Change → `--sweep` exits 0 and prints that row's Change as written (C2-1)
- [ ] A save tag whose words match only that archive row → no `⚠️ tag` line (C2-1)
- [ ] An archive row with 5 cells at line 3 → exit 2, and stderr holds `SKILL-IMPACT_ARCHIVE.md:3` (C2-1)
- [ ] From this repo's root, `skill-trials.py .` and `skill-trials.py --sweep .` each exit 0; the sweep prints one `^(keep|insurance|candidate) · ` line per `| trialing |` row of `SKILL-IMPACT.md`, 27 today (C2-1, Outcome)
- [ ] Narrowing `except (OSError, ValueError)` at `:104` to `except OSError` fails the suite (C2-1)
Verify: `python3 -m unittest discover -s .github/skills/checkup/scripts/tests -p test_skill_trials.py && python3 .github/skills/checkup/scripts/skill-trials.py . >/dev/null && [ "$(python3 .github/skills/checkup/scripts/skill-trials.py --sweep . | grep -cE '^(keep|insurance|candidate) · ')" = "$(grep -c '| trialing |$' .github/skills/workflow/SKILL-IMPACT.md)" ]` (pre: the new archive case fails, and `skill-trials.py .` exits 2 with `too many values to unpack`)
Skills: .github/skills/workflow/references/tests.md
Status: todo

### C2-T2 — Tests kill the three surviving mutations
Delivers: B2, B3, B6 · Blocked by: C2-T1 · Lane: logic
Fixes: C2-2 (P1)
Budget: code +0 · tests +15
Seam: stdout of `skill-trials.py` on fixture repos, run as a subprocess like the existing tests
Change: tests only, in `test_skill_trials.py`.
Accept:
- [ ] A `3 runs` row with 3 worklog entries before it and none after → `--sweep` exits 0 and its line ends `numbers unavailable (before 4.0 → after n/a)`; without `--sweep`, no line (C2-2)
- [ ] A finished `design (new) · workflow` row with no save and numbers not better → its line ends `removal candidate → workflow improve design` (C2-2)
- [ ] A finished row whose Change has exactly 6 words → its line holds those 6 words followed by ` · trial complete`, with no `…` (C2-2)
- [ ] Each mutation applied alone fails the suite: `before and after and` at `:61` without `after`; `{row['names'][0]}` at `:78` as `{row['skill']}`; `len(words) > 6` at `:68` as `>= 6` (C2-2)
Verify: `python3 -m unittest discover -s .github/skills/checkup/scripts/tests -p test_skill_trials.py` (pre: suite OK, and each of the three mutations also passes)
Skills: .github/skills/workflow/references/tests.md
Status: todo

### C2-T3 — The workflow README follows the trial rule
Delivers: B2 · Blocked by: none · Lane: mechanical
Fixes: C1-5 (P2)
Budget: code +0 · tests +0
Seam: `.github/skills/workflow/README.md` by grep
Change: at `README.md:214-215`, replace "`checkup` compares the runs before and after. If the runs got worse, revert the commit and log why." with "`checkup seats` counts save tags and compares the runs before and after. A finished trial with no save and no better numbers becomes a removal candidate for `workflow improve`, and you confirm before anything is removed." Site search: `git grep -n -i -E 'revert the commit|worse means|got worse' -- .github README.md` finds only this line.
Accept:
- [ ] The site search returns no hit, and the README's *A skill change* bullet names `workflow improve` (C1-5)
Verify: `[ "$(git grep -h -i -E 'revert the commit|worse means|got worse' -- .github README.md | wc -l)" = 0 ] && grep -q 'removal candidate for `workflow improve`' .github/skills/workflow/README.md` (pre: one hit at `README.md:215`)
Skills: .github/skills/agent-docs/SKILL.md
Status: todo

## Deviations
