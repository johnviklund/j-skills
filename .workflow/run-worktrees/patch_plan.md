Command: workflow review run-worktrees · patch cycle 1
Created: 2026-10-27 · claude-opus-5-5
Base:    f445741
Inputs:  .workflow/run-worktrees/review.md @ f445741
Status:  complete

## Execution state
Current: C1-T2 done; next C1-T3 · writer: GPT-6.1 Sol · baseline failures: none
C1-T1 red @ 3c2b19f
C1-T1 @ b890db3
C1-T2 @ d75f8cd

## Tickets

### C1-T1 — Landing refuses to push primary commits no one scanned
Delivers: B5 · Blocked by: none · Lane: logic
Fixes: C1-1 (P1)
Budget: code +8 · tests +20
Seam: `run-worktree.py land <slug> --repo <dir>` as a subprocess on temp repos; `references/worktrees.md` §Land at wrap; `references/wrap.md` step 9
Change: on the clean path, before the primary checkout's `git merge` (`run-worktree.py:113`), exit 1 when `origin/<primary>..<primary>` is not empty, naming those shas. The conflict path is unchanged. Red commit: the new test, plus a `git push origin main` in `LandTests.run_branch` and after `primary advance`, so the existing Land tests model a scanned primary branch.
Accept:
- [x] `main` has a commit not on `origin/main` → `land B` exits 1; `main`, `origin/main` and `.worktrees/B` unchanged; stderr names that commit's short sha (B5)
- [x] The existing Land tests pass, and the fix commit changes no test file (B5)
- [x] `worktrees.md` exit 1 and `wrap.md` step 9: unpushed primary commits → scan `origin/<primary>..<primary>` with gitleaks, push, land again (B5)
Verify: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests -p 'test_run_worktree.py' -k Land && grep -c 'origin/<primary>\.\.<primary>' .github/skills/workflow/references/worktrees.md` (pre: 3 Land tests pass, grep 0)
Skills: .github/skills/agent-docs/SKILL.md
Status: done @ b890db3
Writer: GPT-6.1 Sol

### C1-T2 — Setup reads its block through check-run's fence-aware sections
Delivers: B1, B8 · Blocked by: none · Lane: logic
Fixes: C1-2 (P1)
Budget: code +6 · tests +10
Seam: `run-worktree.py open` as a subprocess on temp repos; `worktree_setup` (`run-worktree.py:22-25`); `check-run.py` `Doc` (`:100-127`)
Change: replace the section regex with `checks.Doc` sections. Let `Doc` take text as well as a path (for example an optional `text` argument) so `git show <primary>:AGENTS.md` output needs no temp file. Fence extraction (`:44`) stays.
Accept:
- [x] Committed `## Worktree setup` whose ```` ```sh ```` fence holds `# install deps` then `touch ready` → `open B` prints `touch ready` and `.worktrees/B/ready` exists (B1)
- [x] `run-worktree.py` has no section regex of its own (`grep -cF '(?=^#{1,2} |'` → 0); the existing Open, Doctor and check-run tests pass unchanged (B1, B8)
Verify: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests && test "$(grep -cF '(?=^#{1,2} |' .github/skills/workflow/scripts/run-worktree.py)" -eq 0` (pre: 61 pass, grep 1)
Skills: none
Status: done @ d75f8cd
Writer: GPT-6.1 Sol

### C1-T3 — Lookup keeps working when origin cannot be fetched
Delivers: B2, B3 · Blocked by: none · Lane: logic
Fixes: C1-3 (P1)
Budget: code +5 · tests +15
Seam: `run-worktree.py where <slug> --repo <dir>` with `origin` set to a missing path; `where` (`run-worktree.py:52-53`); `references/worktrees.md` §Find the run step 3
Change: a failed fetch prints `could not fetch origin: <git's error>; using local refs` to stderr and continues; nothing else in `where` changes.
Accept:
- [ ] Lone run, `origin` unreachable → `where B` exits 0, prints `.`, stderr says `using local refs` (B2)
- [ ] Existing `.worktrees/B`, `origin` unreachable → `where B` exits 0 and prints `.worktrees/B` (B3)
- [ ] `worktrees.md` step 3: a failed fetch warns, uses local refs, and a second clone may then read a stale copy (B3)
Verify: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests -p 'test_run_worktree.py' -k Where && grep -c 'local refs' .github/skills/workflow/references/worktrees.md` (pre: 2 Where tests pass, grep 0)
Skills: .github/skills/agent-docs/SKILL.md
Status: todo

### C1-T4 — A run already started in the primary checkout stays there
Delivers: B2 · Blocked by: none · Lane: logic
Fixes: C1-5 (P2)
Budget: code +4 · tests +12
Seam: `run-worktree.py open` as a subprocess on temp repos; `open_run` (`run-worktree.py:68-83`); `references/worktrees.md` §Start execution
Change: when the slug's own `plan.md` or `patch_plan.md` in the primary checkout has a ticket not `todo`, and it has no worktree, `open` returns `.` before the busy check.
Accept:
- [ ] B on `main` with T1 `done @`, T2 `todo` and untracked `t2.py` → `open B` prints `.`; `git worktree list` gains no line; `t2.py` untouched (B2)
- [ ] B planned with only `todo` tickets and uncommitted `src.py` → `open B` still prints `.worktrees/B` (B1)
- [ ] `worktrees.md` §Start execution: a run with a started ticket stays in the checkout where it started (B2)
Verify: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests -p 'test_run_worktree.py' -k Open && grep -c 'started ticket stays' .github/skills/workflow/references/worktrees.md` (pre: 4 Open tests pass, grep 0)
Skills: .github/skills/agent-docs/SKILL.md
Status: todo

### C1-T5 — Tests pin the seven unguarded checks
Delivers: B1, B2, B5, B6 · Blocked by: C1-T1, C1-T2, C1-T3, C1-T4 · Lane: logic
Fixes: C1-4 (P1)
Budget: code +0 · tests +60 · why: four fixture shapes; no product code
Seam: `run-worktree.py open|land` as subprocesses on temp repos; mutations applied only in a throwaway `git worktree`, never committed
Change: tests only. Then apply each mutation listed in C1-4 (`review.md`) alone, run the suite, restore, and record one `KILLED <mutation>` line each in the receipt.
Accept:
- [ ] Conflicts in `src.py` and `WORKLOG.md` together → `land B` exits 3; a conflict only in `notes.txt` → exit 4 (B6)
- [ ] Run A on `main` with only `todo` tickets, clean folder → `open B` prints `.` (B2)
- [ ] `open B` then `open C`, both isolated → `.git/info/exclude` holds `.worktrees/` once (B1)
- [ ] `land B` with a dirty `.worktrees/B`, with the primary checkout off `main`, with `.worktrees/B` off `run/B` → each exits 1, `main` unchanged (B5)
- [ ] `receipts/c1-t5-mutations.md` holds 7 `KILLED` lines, one per C1-4 mutation (B1, B2, B5, B6)
Verify: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests && grep -c '^KILLED ' .workflow/run-worktrees/receipts/c1-t5-mutations.md` (pre: 61 pass; receipt missing, grep exit 2)
Skills: none
Status: todo

## Deviations
- C1-T2 Verify checks grep's count with `test ... -eq 0`: grep exits 1 on the required zero matches. Acceptance stays unchanged.
