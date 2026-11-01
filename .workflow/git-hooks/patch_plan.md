Command: workflow review git-hooks · patch cycle 2
Created: 2026-11-01 · Claude Opus 5.5
Base:    b071f38
Inputs:  .workflow/git-hooks/review.md @ b071f38
Status:  complete

Three tickets for cycle 3, approved by the human. C2-T1 fixes a behaviour bug, so it lands as two commits: first a failing test on its own, recorded as `Red: <sha>`, then the fix, which leaves test files untouched. C2-T2 and C2-T3 add tests only.

## Execution state
Current: C2-T1 ready

## Tickets

### C2-T1 — Exclude only the push target's remote refs when the target is a named remote
Delivers: B1 · Blocked by: none · Lane: logic
Fixes: C2-1 (P1)
Budget: code +4 · tests +15
Seam: `git push` from a temp repo with the hooks installed and two bare remotes, `work` and `origin`
Change: `hooks.py pre_push` builds one exclusion: `--remotes=<remote>` when `remote` is a name listed by `git remote`, else `--remotes`. Git refuses remote names with spaces, so the name is safe inside `--log-opts`. The rev-list guard and the gitleaks `--log-opts` both use it. A push to a URL or path keeps `--remotes`, as now.
Accept:
- [ ] A `ghp_` commit already on `work` (pushed with `core.hooksPath=/dev/null`), then `git push origin HEAD:refs/heads/feature` → refused, output lacks the token, `origin` lacks `refs/heads/feature` (C2-1)
- [ ] Existing `PrePush` cases still pass: spaced-path target refused, clean branch over a secret already on origin pushes, branch delete pushes (C2-1)
- [ ] Mutation: replacing the named exclusion with plain `--remotes` fails the new test (reviewer checks)
Verify: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests -p test_hooks.py -k PrePush` (pre: the new case fails and `origin` holds the commit)
Skills: none
Status: todo

### C2-T2 — Test the rev-list guard
Delivers: B1 · Blocked by: C2-T1 · Lane: logic
Fixes: C2-2 (P1)
Budget: code +0 · tests +8
Seam: `hooks.py pre-push origin` run as a subprocess in the `PrePush` temp repo, ref lines on stdin
Change: tests only, in `test_hooks.py`; the guard already exists, so no Red commit.
Accept:
- [ ] stdin `refs/heads/x 1234567890abcdef1234567890abcdef12345678 refs/heads/x <40 zeros>` → exit 1, stderr names `refs/heads/x` (C2-2)
- [ ] Mutation: disabling the guard's `if` fails the new test (reviewer checks)
Verify: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests -p test_hooks.py -k PrePush` (pre: all pass; with the guard disabled, the new test fails)
Skills: none
Status: todo

### C2-T3 — Narrow each --no-verify rule on its own
Delivers: B8 · Blocked by: none · Lane: logic
Fixes: C2-3 (P1)
Budget: code +0 · tests +3
Seam: `config-scan.py` run as a subprocess in a temp repo and home
Change: tests only: two more `deny` cases in `test_config_scan.py`, `[Bash(git commit --no-verify), push]` and `[commit, Bash(git push --no-verify)]`, each expected to print the line.
Accept:
- [ ] Deny narrow commit + wide push → the line prints (C2-3)
- [ ] Deny wide commit + narrow push → the line prints (C2-3)
- [ ] Mutation: reverting either probe string alone at `config-scan.py:181` fails a subtest (reviewer checks)
Verify: `python3 -m unittest discover -s .github/skills/checkup/scripts/tests -k NoVerify` (pre: all pass; each probe reverted alone fails a subtest)
Skills: none
Status: todo
