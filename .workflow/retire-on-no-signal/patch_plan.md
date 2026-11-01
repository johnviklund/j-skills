Command: workflow review retire-on-no-signal · patch cycle 3
Created: 2026-11-01 · Claude Opus 5.5
Base:    83cfa35
Inputs:  .workflow/retire-on-no-signal/review.md @ 83cfa35
Status:  complete

One ticket for cycle 3, approved by the human as a fourth cycle ("1a"). C3-T1 changes tests only: the code already behaves correctly, so there is no red commit.

## Execution state
Current: C3-T1 ready

## Tickets

### C3-T1 — A row with too many cells names its location
Delivers: B6 · Blocked by: none · Lane: logic
Fixes: C3-1 (P1)
Budget: code +0 · tests +5
Seam: exit code and stderr of `skill-trials.py` on a fixture archive, run as a subprocess like the existing tests
Change: tests only, in `test_skill_trials.py`. Extend `test_bad_archive_row_names_location` (or add a sibling) with an archive row at line 3 that has 7 cells, one extra unescaped `|` in its Change cell. Reuse the existing `rows`, `row` and subprocess helpers. Site search: `len(cells) != 6` at `skill-trials.py:14` is the only cell-count guard.
Accept:
- [ ] An archive row at line 3 with 7 cells → exit 2, and stderr holds `SKILL-IMPACT_ARCHIVE.md:3` and `got 7` (C3-1)
- [ ] The existing 5-cell case still asserts `SKILL-IMPACT_ARCHIVE.md:3` (C3-1)
- [ ] Each mutation applied alone fails the suite: `len(cells) != 6` at `:14` as `< 6`, and as `> 6` (C3-1)
Verify: `python3 -m unittest discover -s .github/skills/checkup/scripts/tests -p test_skill_trials.py` (pre: suite OK, and `!= 6` as `< 6` also passes)
Skills: .github/skills/workflow/references/tests.md
Status: todo
