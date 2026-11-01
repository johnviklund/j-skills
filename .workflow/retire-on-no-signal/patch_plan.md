Command: workflow review retire-on-no-signal · patch cycle 1
Created: 2026-11-01 · Claude Opus 5.5
Base:    0248594
Inputs:  .workflow/retire-on-no-signal/review.md @ 0248594
Status:  complete

Five tickets for cycle 1. C1-T1 and C1-T2 change tests only, so they have no Red commit. C1-T3 and C1-T4 fix behaviour bugs, so each lands as two commits: first a failing test alone, recorded as `Red: <sha>`, then the fix, which leaves test files untouched. C1-T5 edits two docs.

## Execution state
Current: C1-T3 ready
C1-T1 @ 953e4ac
C1-T2 @ 59bd7be
writer: GPT-6.1 Sol
C1-T1 final: workflow 124 tests OK; checkup 18 tests OK.
Pending decision: none.

## Tickets

### C1-T1 — Tests kill the 19 surviving mutations
Delivers: B1, B2, B3, B6 · Blocked by: none · Lane: logic
Fixes: C1-1 (P1)
Budget: code +0 · tests +60
Seam: stdout and exit code of `skill-trials.py` on fixture repos, run as a subprocess like the existing tests
Change: tests only, in `test_skill_trials.py`. Fixtures copy the real forms of `SKILL-IMPACT.md`, `learnings.md` and `WORKLOG.md`.
Accept:
- [x] The impact fixture opens with the real title, `Mode:` line and prose; a learnings file holds a `## Phase` heading, a `[durable→memory]` line and a tag ending `[routed → SKILL-IMPACT 2026-11-02]` → exit 0, the tag counts once (C1-1)
- [x] A worklog with a preamble and four blocks, each missing one of date, `review cycles`, `deviations` and `- Skills:` → exit 0 and the numbers ignore those four blocks (C1-1)
- [x] Five entries before and five after with distinct scores, newest first, split across both repos, plus one on the row's date → the exact means of the last 3 before and the first 3 after (C1-1)
- [x] A sweep with worklog entries prints `· numbers` on every line; a kept-by-save line holds `kept · 1 save · numbers`, so `1 saves` fails (C1-1)
- [x] No repo argument, run from a fixture repo, counts its tag; one repo passed twice counts once; a missing repo and a missing `--impact` each exit 2 naming the path (C1-1)
- [x] The script copied to `<tmp>/skills/checkup/scripts/` with no `--impact` reads `<tmp>/skills/workflow/SKILL-IMPACT.md`; each of the 19 C1-1 mutations, applied alone, fails the suite (C1-1)
Verify: `python3 -m unittest discover -s .github/skills/checkup/scripts/tests -p test_skill_trials.py` (pre: 6 tests OK, and each of the 19 mutations also passes)
Skills: .github/skills/workflow/references/tests.md
Status: done @ 953e4ac
Writer: GPT-6.1 Sol

### C1-T2 — Delete the fixture write that the next line overwrites
Delivers: B6 · Blocked by: C1-T1 · Lane: mechanical
Fixes: C1-2 (P1)
Budget: code +0 · tests -3
Seam: `test_skill_trials.py` `test_saves_across_repos_and_sweep_is_read_only`
Change: delete the first `self.rows(...)` call and the comment above the second; the test keeps the second call.
Accept:
- [x] That test calls `self.rows(` exactly once and still passes (C1-2)
Verify: `python3 -m unittest discover -s .github/skills/checkup/scripts/tests -p test_skill_trials.py && [ "$(sed -n '/def test_saves_across/,/def test_tag/p' .github/skills/checkup/scripts/tests/test_skill_trials.py | grep -c 'self.rows(')" = 1 ]` (pre: count 2)
Skills: none
Status: done @ 59bd7be
Writer: GPT-6.1 Sol

### C1-T3 — Each report line names the row it judges
Delivers: B2 · Blocked by: C1-T2 · Lane: logic
Fixes: C1-3 (P2)
Budget: code +4 · tests +10
Seam: stdout of `skill-trials.py` without `--sweep` on fixture repos
Change: in normal mode, put the first 6 words of the Change cell after the skill, then `…` when cut: `⚠️ <date> <skill> · <6 words>… · trial complete · …`, and the same for the `open` line. Sweep lines stay as they are.
Accept:
- [ ] Two finished `2026-10-30 · workflow` rows with Change `tests.md: a fixture copies every real form` and `Run routing tables override model and effort` → two candidate lines, each holding its own first 6 words (C1-3)
- [ ] A `3 checkups` row prints `· open · count checkups by hand` after its words; the T2 verdict wording after the words is unchanged (C1-3)
Verify: `python3 -m unittest discover -s .github/skills/checkup/scripts/tests -p test_skill_trials.py` (pre: the new case fails because both lines are identical)
Skills: none
Status: todo

### C1-T4 — A save tag for a closed row prints no warning
Delivers: B1, B5 · Blocked by: C1-T3 · Lane: logic
Fixes: C1-4 (P2)
Budget: code +8 · tests +12
Seam: stdout of `skill-trials.py --sweep` on a fixture impact file, an archive file beside it, and fixture repos
Change: a tag still counts only on exactly one trialing match, and 2 or more trialing matches still warn. With 0 trialing matches, it warns only when no row of any outcome matches, in `--impact` or in `SKILL-IMPACT_ARCHIVE.md` beside it.
Accept:
- [ ] A tag whose words match one `kept` row → no `⚠️ tag` line and every row `0 saves` (C1-4)
- [ ] A tag matching one row in `SKILL-IMPACT_ARCHIVE.md` beside the impact file → no `⚠️ tag` line; with no archive file, the same tag still warns `matches 0 rows` (C1-4)
- [ ] The T1 cases for one save, ambiguous words and the sweep's line count keep passing (B1, B5, B6)
Verify: `python3 -m unittest discover -s .github/skills/checkup/scripts/tests -p test_skill_trials.py` (pre: the kept-row case prints `matches 0 rows`)
Skills: none
Status: todo

### C1-T5 — Two docs follow the new trial rules
Delivers: B1, B2 · Blocked by: none · Lane: mechanical
Fixes: C1-5 (P2)
Budget: code +0 · tests +0
Seam: `learning-worklog.md` and `memory.remember/references/workflow-runs.md` by grep
Change: in `learning-worklog.md:86-89`, keep the sha definition, and say checkup compares `Run:` numbers by date and skill name (`checkup/references/seats.md`). A finished trial with no save and no better numbers is a removal candidate for `workflow improve`, removed only after the human confirms. In `workflow-runs.md` step 3, a `[saved→skill]` line gets the routed mark `[routed → SKILL-IMPACT <date>]`, and no file changes.
Accept:
- [ ] `learning-worklog.md` holds no `worse means revert` and names `workflow improve` (C1-5)
- [ ] `workflow-runs.md` names `[saved→skill]` once, on a line that says to change no file (C1-5)
Verify: `[ "$(grep -c 'worse means revert' .github/skills/workflow/references/learning-worklog.md)" = 0 ] && grep -q 'workflow improve' .github/skills/workflow/references/learning-worklog.md && [ "$(grep -c 'saved→skill' .github/skills/memory.remember/references/workflow-runs.md)" = 1 ]` (pre: counts 1 and 0)
Skills: .github/skills/agent-docs/SKILL.md
Status: todo
