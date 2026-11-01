Command: workflow review git-hooks · patch cycle 1
Created: 2026-11-01 · Claude Opus 5.5
Base:    6ea2df2
Inputs:  .workflow/git-hooks/review.md @ 6ea2df2
Status:  complete

Five tickets. C1-T1 and C1-T5 fix behaviour bugs, so each lands as two commits: first a failing test on its own, recorded as `Red: <sha>`, then the fix, which leaves test files untouched. C1-T2 adds tests only. C1-T3 and C1-T4 edit Markdown only.

## Execution state
Current: C1-T4 todo; session limit reached
C1-T1 @ a2d308f
C1-T2 @ d6de8e2
C1-T3 @ 8667607
writer: GPT-6.1 Sol
Baseline: workflow 119 tests OK; checkup 9 tests OK
Red: C1-T1 @ 860ebb2, spaced-target push incorrectly exits 0
Reuse: existing HookRepo and PrePush fixtures; no helper needed

## Tickets

### C1-T1 — Fail closed when the push range cannot be listed
Delivers: B1, B2 · Blocked by: none · Lane: logic
Fixes: C1-1 (P1)
Budget: code +8 · tests +15
Seam: `git push` from a temp repo with the hooks installed, to a bare origin whose path holds a space
Change: `hooks.py pre_push` scans `<sha> --not --remotes`, with no remote name, so `$1` never enters `--log-opts`. Before gitleaks it runs `git rev-list --quiet <sha> --not --remotes`; a nonzero exit refuses the push and names the ref. The delete skip at `:98` stays.
Accept:
- [x] Push of a `ghp_` commit to a bare repo at a path with a space → refused, output lacks the token (C1-1)
- [x] Existing cases still pass: a clean branch over a secret already on origin pushes, and a branch delete pushes (C1-1)
- [x] Mutation M14, dropping the delete skip, now fails `PrePush` (reviewer checks)
Verify: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests -p test_hooks.py -k PrePush` (pre: the new case fails, the remote gets the commit)
Skills: none
Status: done @ a2d308f
Writer: GPT-6.1 Sol
Red: 860ebb2

### C1-T2 — Cover the four surviving pre-commit and stub mutations
Delivers: B4, B5 · Blocked by: none · Lane: logic
Fixes: C1-3 (P1)
Budget: code +0 · tests +30
Seam: `git commit` in a temp repo with the hooks installed, beside a committed broken run `r`
Change: tests only, in `test_hooks.py`; no script changes, so no Red commit.
Accept:
- [x] Commit staging `docs/r/notes.md` → allowed (M7) (C1-3)
- [x] Commit of `git rm -r .workflow/r` → allowed (M10) (C1-3)
- [x] `check-run.py` deleted from the installing copy, broken run staged → allowed, stderr names `check-run.py` (M11) (C1-3)
- [x] Installing copy gone, a copy only under a `CODEX_HOME` outside `HOME` → a broken run's commit is refused (M22) (C1-3)
Verify: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests -p test_hooks.py` (pre: all pass, and each of M7, M10, M11, M22 stays green)
Skills: none
Status: done @ d6de8e2
Writer: GPT-6.1 Sol

### C1-T3 — The hook rules keep a manual fallback for repos without hooks
Delivers: B1, B4 · Blocked by: none · Lane: mechanical
Fixes: C1-2 (P1)
Budget: code +0 · tests +0
Seam: `SKILL.md` ground rules and `worktrees.md` *Commit and hand off*
Change: each of `SKILL.md:157-158` stays one line and adds: when `hooks.py install --check` does not print `installed`, run the old command by hand. For the push: `gitleaks git --log-opts="@{u}..HEAD" --redact -v --no-banner`, or `origin/<primary>..HEAD` without an upstream. For the commit: `python3 <skill>/scripts/check-run.py <slug> && git commit ...`. `worktrees.md:60` says the pre-push hook scans, or the hub's manual scan where no hook is installed.
Accept:
- [x] `grep -c 'install --check' .github/skills/workflow/SKILL.md` → 2 (C1-2)
- [x] `grep -c 'gitleaks git --log-opts="@{u}..HEAD"' .github/skills/workflow/SKILL.md` → 1 (C1-2)
- [x] `grep -c "hub's gitleaks scan" .github/skills/workflow/references/worktrees.md` → 0 (C1-2)
Verify: `grep -c 'install --check' .github/skills/workflow/SKILL.md && grep -c 'gitleaks git --log-opts="@{u}..HEAD"' .github/skills/workflow/SKILL.md && ! grep -q "hub's gitleaks scan" .github/skills/workflow/references/worktrees.md` (pre: 0 · 0 · 1)
Skills: .github/skills/agent-docs/SKILL.md, .github/skills/plain/SKILL.md
Status: done @ 8667607
Writer: GPT-6.1 Sol

### C1-T4 — Restore the write-after-reads rule
Delivers: B4 · Blocked by: C1-T3 · Lane: mechanical
Fixes: C1-5 (P2)
Budget: code +0 · tests +0
Seam: `SKILL.md` ground rules
Change: append "Write an artifact only after the reads it reports on have returned." to the pre-commit line from C1-T3, or put it on its own line after it.
Accept:
- [ ] `grep -c 'Write an artifact only after the reads it reports on have returned' .github/skills/workflow/SKILL.md` → 1 (C1-5)
Verify: `grep -c 'Write an artifact only after the reads it reports on have returned' .github/skills/workflow/SKILL.md` (pre: 0)
Skills: none
Status: todo

### C1-T5 — Probe the --no-verify deny rules with a realistic command
Delivers: B8 · Blocked by: none · Lane: logic
Fixes: C1-4 (P2)
Budget: code +2 · tests +3
Seam: `config-scan.py` run as a subprocess in a temp repo and home
Change: `config-scan.py:181` probes `Bash(git commit -m x --no-verify)` and `Bash(git push origin main --no-verify)`.
Accept:
- [ ] Deny `Bash(git commit --no-verify)` and `Bash(git push --no-verify)` → the line prints (C1-4)
- [ ] Existing subtest still passes: both `*--no-verify*` rules → no line (C1-4)
- [ ] Existing subtest still passes: `Bash(git *--no-verify*)` alone → no line (C1-4)
Verify: `python3 -m unittest discover -s .github/skills/checkup/scripts/tests -k NoVerify` (pre: the new subtest fails)
Skills: none
Status: todo
