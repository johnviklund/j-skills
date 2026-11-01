Command: workflow review git-hooks
Created: 2026-11-01 · Claude Opus 5.5
Base:    6ea2df2
Inputs:  .workflow/git-hooks/plan.md @ 90b7bd1
Status:  complete

## Coverage
- [x] T1 — acceptance 6/6 tested and passing; `grep -c 'pre-commit hook'` SKILL.md 1, `hooks.py install` bootstrap.md 1
- [x] T2 — acceptance 5/5 tested and passing; B1 fails for one input, see C1-1
- [x] T3 — acceptance 5/5 tested and passing; the deny check accepts too-narrow rules, see C1-4
- [x] B1…B8 delivered, B1 with the C1-1 hole · Outcome observed via manual run, no verify skill: in a temp repo the installed pre-push refused a `ghp_` commit to `origin`, and in this repo `hooks.py install --check` printed `would install pre-commit, pre-push` and `config-scan.py` printed 1 `--no-verify` line · out of scope untouched: no CI, settings, gitleaks config or chaining in the diff
- [x] .workflow/ dependency check: hits are pre-existing run tooling (`run-worktree.py:66,126`, test fixtures); this run adds none
- [x] Escape-hatch scan: no hits · new dependencies: none
- [x] Full suites: workflow `Ran 119 tests` OK, checkup `Ran 9 tests` OK, exit 0; existing config-scan tests unchanged
Size: +153 code · +189 tests · ratio 1.24 · net +341 · over 1,000: none
Reachability: `hooks.py` → the installed stubs, run by `bootstrap.md` step 5 and checkup `workspace.md`; `no_verify()` → `config-scan.py main()` · guards shown failing: hooks.py sweep M1–M23 in a throwaway worktree, 16 killed; survivors M3, M5, M9 are equivalent; M7, M10, M11, M14, M22 are C1-1 and C1-3
Independence: cross-vendor (writer GPT-6.1 Sol / OpenAI · reviewer Claude Opus 5.5 / Anthropic)
Threats: hook stub → hooks.py · git sends ref lines on stdin and the remote name or URL as `$1`; the staged paths come from the user; the repo's own committed `hooks.py` runs when the installing copy is gone (plan F14, F15) · it reaches `python3`, `check-run.py` and `gitleaks` · it only allows or refuses the commit or push · gitleaks prints redacted output · fails open when gitleaks's git log call fails, C1-1 · worst case: a secret reaches the remote
Threats: config-scan → Claude settings · reads only `permissions.deny` strings from the three Claude files (`config-scan.py:163-185`) · prints a fixed line, never a setting value · fails closed: unreadable files count as no rule

## Cycle 1 findings
### P1 — pre-push lets a secret through when the push target holds a space (C1-1)
- Evidence: B1 · `hooks.py:101` puts `$1` into `--log-opts`, and gitleaks splits that on spaces. `git push "/tmp/x/o space.git" HEAD:refs/heads/leak` with a `ghp_` commit printed `no leaks found`, exited 0, and the remote holds the commit. gitleaks 8.30.1 exits 0 whenever its git log call fails: a bad revision and the split range both scanned 0 bytes. Mutation M14, which drops the delete skip at `hooks.py:98`, survives for the same reason.
- Disposition: fix now
- Resolved: —

### P1 — A repo without the hooks loses both rules (C1-2)
- Evidence: `SKILL.md:157-158` now only describe the hooks. `worktrees.md:60` still says "run the hub's gitleaks scan", and the hub no longer has one. In this repo `hooks.py install --check` prints `would install pre-commit, pre-push`. An agent here, or in any repo checkup has not fixed, pushes unscanned and commits unchecked artifacts with no rule against it. Before this run it had both rules.
- Disposition: fix now
- Resolved: —

### P1 — Four more hooks.py mutations survive (C1-3)
- Evidence: whole-file sweep of the new `hooks.py`. M7 drops `parts[0] == '.workflow'` at `:77`. M10 drops the `is_dir()` skip at `:78`, so a `git rm -r` of a run would run check-run on a missing folder, exit 2, and block. M11 makes the missing-`check-run.py` branch at `:80-82` block. M22 drops the `$CODEX_HOME` path at `:30`; the tests set it to `$HOME/.codex`. All four keep `test_hooks.py` green.
- Disposition: fix now
- Resolved: —

### P2 — The --no-verify check accepts deny rules that block only the bare form (C1-4)
- Evidence: B8 · `config-scan.py:181` tests only `Bash(git commit --no-verify)`. Deny rules `Bash(git commit --no-verify)` and `Bash(git push --no-verify)` give 0 lines, yet they miss `git commit -m x --no-verify`. Small: change the two probe strings and add one test case.
- Disposition: fix now
- Resolved: —

### P2 — SKILL.md dropped a rule the hook does not cover (C1-5)
- Evidence: `git diff 90b7bd1..HEAD -- .github/skills/workflow/SKILL.md` removes "Write an artifact only after the reads it reports on have returned." check-run does not check that cited files exist, so the hook does not enforce it. Small: restore the one sentence.
- Disposition: fix now
- Resolved: —

### P3 — Minor, deferred
- `hooks.py:58` `is_file()` is redundant: `os.access` is already false for a missing file (M3). `hooks.py:66` write guard changes nothing, the content is the same (M5).
- `hooks.py:54` `read_text()` on a non-UTF-8 foreign hook raises `UnicodeDecodeError`, which `main()` does not catch, so the user sees a traceback.
- `config-scan.py:181` warns when `Bash(git commit:*)` already denies every commit.
- A push to a bare URL makes `--remotes=<url>` match nothing, so the whole history is scanned and an old allowed secret blocks it. C1-T1 removes the remote name, which also fixes this.
- Disposition: defer — stays here
- Resolved: —

## Pre-existing / environmental
- This repo has no hooks installed yet. Installing them is checkup's opt-in fix, D3, and is the human's call.

## Cycle 1 verdict
Patch cycle 1: 3 P1 and 2 small P2 fix now, 4 P3 deferred. `patch_plan.md` holds C1-T1 to C1-T5.
