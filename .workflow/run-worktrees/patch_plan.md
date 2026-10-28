Command: workflow review run-worktrees · patch cycle 5
Created: 2026-10-28 · claude-opus-5-5
Base:    cf15502
Inputs:  .workflow/run-worktrees/review.md @ cf15502
Status:  complete

## Execution state
Current: C5-T3 todo · writer: GPT-6.1 Sol · baseline failures: none
C5-T1 @ 00a4ae6
C5-T2 @ bbaa7a1

## Tickets

Every ticket proves itself with `.workflow/run-worktrees/scripts/mutate.py [ids]`. It applies each named
mutation to a temporary copy of the skill, runs the full suite there and never edits tracked files.
At `cf15502` it reports 54 killed and 20 survived: X4 and X5 for C4-1, the 18 ids of C5-1. A full run
takes about 9 minutes with 8 jobs. If a pattern no longer matches, the script exits 2. Update only that
entry's text and say so in the receipt.

### C5-T1 — Tests fail when the `shell` tag or a later non-shell fence breaks setup
Delivers: B1 · Blocked by: none · Lane: logic
Fixes: C4-1 (P1)
Budget: code +0 · tests +2 · why: two rows in the existing `cases` tuple
Seam: `test_Open_setup_reads_shell_fences_line_by_line` (`test_run_worktree.py:174`)
Change: add `("```shell\ntouch ready\n```\n", 0)` and `("```sh\ntouch ready\n```\n```text\nok\n```\n", 0)`. Test-only, so there is no red commit; the mutations are the proof.
Accept:
- [x] `mutate.py X4 X5` → 2 killed, each on its own new row (C4-1, B1)
- [x] `mutate.py` on every parser id, M25–M28 and X1–X21 → 25 killed, 0 survived (C4-1)
Verify: `python3 .workflow/run-worktrees/scripts/mutate.py X4 X5` (pre: 2 survived)
Skills: none
Status: done @ 00a4ae6
Writer: GPT-6.1 Sol

### C5-T2 — A test fails for each of the 18 C5-1 conditions
Delivers: B1, B2, B3, B5, B8 · Blocked by: none · Lane: logic
Fixes: C5-1 (P1)
Budget: code +0 · tests +90 · why: about 12 cases on temp repos, two needing a fake `git`
Seam: `run-worktree.py` as a subprocess on the existing `RepoTests` fixture. Add rows or subtests to the method named here when one fits; add a method only when none does. For L5 and L8, put a `git` script first on `PATH` with `mock.patch.dict(os.environ, ...)` around the one `run_command` call. It exits with a set code for `merge-tree` and hands every other call to the real `git`.
Change: one case per group below. `.worktrees/B` means `open B` with uncommitted `src.py`.
- A4, A5: setup fence `false` then `touch ready` → `open B` exits 1, `.worktrees/B` exists, no `ready`
- A2, WH5: remove the worktree but keep local `run/B`, with no `origin/run/B` → `where B` prints `.worktrees/B` at `run/B`'s sha
- WH1: no `origin` remote → `where B` exits 0, prints `.`, and stderr lacks `could not fetch`
- S1, O6: clean folder → `open B` prints `.` when A's ticket has no `Status:`, and again when A is parked with a done ticket
- O8: uncommitted `src.py` plus a live, unstarted run A → `.worktrees/B`
- L2: `land B` with no worktree → exit 1 naming `no worktree for B`. L11: `run/B` never pushed → exit 0, no `run/B`
- L5: fake `merge-tree` exit 1 on a clean merge → exit 1. L8: exit 128 → exit 1, `main` unmoved
- D1: `doctor` with no `.worktrees/` and no setup block → empty stdout
- MN1: `open a/b` → exit 2 naming the slug rule. MN2: `open` with no slug → exit 2 naming `a run slug is required`. MN3: `where a..b` → exit 1
- C6b, MN4: `git remote set-head origin -d` → `where B` exits 0; then rename `main` to `trunk` → exit 1 naming `no primary branch found`
Accept:
- [x] `mutate.py A2 A4 A5 WH1 WH5` → 5 killed by the setup and `where` cases (C5-1, B1, B3)
- [x] `mutate.py S1 O6 O8` → 3 killed by the `open` cases (C5-1, B1, B2)
- [x] `mutate.py L2 L5 L8 L11` → 4 killed by the `land` cases (C5-1, B5)
- [x] `mutate.py D1 MN1 MN2 MN3 MN4 C6b` → 6 killed by the `doctor` and command-line cases (C5-1, B8)
- [x] The commit changes only `test_run_worktree.py`, existing assertions are unchanged, and the full suite passes (C5-1)
Verify: `python3 .workflow/run-worktrees/scripts/mutate.py A2 A4 A5 WH1 WH5 S1 O6 O8 L2 L5 L8 L11 D1 MN1 MN2 MN3 MN4 C6b` (pre: 18 survived)
Skills: none
Status: done @ bbaa7a1
Writer: GPT-6.1 Sol

### C5-T3 — `land` stops before merging when the primary branch moved on origin
Delivers: B5 · Blocked by: C5-T1, C5-T2 · Lane: logic
Fixes: C5-2 (P2, the human chose to fix it)
Budget: code +5 · tests +15 · why: one temp repo plus a second clone that pushes `main`
Seam: `run-worktree.py land B` as a subprocess; a clone of the fixture's bare `origin` commits and pushes `main`
Change: first a red commit, the new test alone, run and seen failing: today `main` moves. Then the fix, after `land`'s branch check and before any merge: fetch `origin <primary>`. If `<primary>..origin/<primary>` is not empty, raise and name `origin/<primary>` and the pull. Reuse `git()` and the unpushed check's pattern (`run-worktree.py:134`). Add one line to `worktrees.md`'s exit 1 entry: when the primary branch moved on origin, pull it into the primary checkout, then land again.
Accept:
- [ ] The red commit fails at its parent because `main`'s sha changes (C5-2)
- [ ] After the fix: exit 1, `main` unchanged, `.worktrees/B` and `run/B` kept, and stderr names `origin/main` (C5-2, B5)
- [ ] `mutate.py` gains `L15`, deleting the new check; the full `mutate.py` run → 75 killed, 0 survived (C5-2)
- [ ] `grep -c 'moved on origin' .github/skills/workflow/references/worktrees.md` → 1, and the fix commit leaves test files untouched (C5-2)
Verify: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests -k Land` (pre: the red test fails)
Skills: none
Status: todo
