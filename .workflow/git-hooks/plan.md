Command: workflow plan git-hooks
Created: 2026-11-01 · Claude Opus 5.5
Base:    90b7bd1
Inputs:  .workflow/git-hooks/brainstorm.md @ e3b8e98
Status:  complete

Docs read: none in scope, this repo has no PRODUCT.md or DESIGN.md
Size: code 182 · tests 116 · ratio 0.64 · largest touched README.md 366, checkup/scripts/config-scan.py 182, workflow/SKILL.md 180 · over 1,000: none · new: workflow/scripts/hooks.py, workflow/scripts/tests/test_hooks.py
Decisions: 1a · 2a · 3a, with the human's note that the run must work with any vendor and any harness, which F15 applies

## Execution state
Current: T1, verification complete; commit pending
writer: GPT-6.1 Sol
Baseline: workflow 112 tests OK; checkup 8 tests OK
Session 1: T1
Reuse: no install, marker or skill-path helper found, as F12 records.

## Findings
| # | What is true | What it changes |
|---|---|---|
| F1 | `check-run.py` exits 0 with warnings, 1 with errors, 2 on bad input, and reads the working tree, not the index (check-run.py:859-909) | Pre-commit passes its exit code through. A partly staged artifact is checked as it is on disk, the same as today's manual chain |
| F2 | Bootstrap stages `.workflow/.gitkeep`, wrap can stage `.workflow/archive/`, and `check-run.py` exits 2 on a name that is not a run | Pre-commit skips a file directly under `.workflow/`, the `archive` folder, and a slug whose folder is gone |
| F3 | `check-run.py` sits beside `hooks.py` in every copy, so B5's missing `check-run.py` only happens when the stub finds no `hooks.py` | B5 is the stub's not-found branch: it lists every searched path and exits 0 |
| F4 | The brief does not say what pre-push does when the stub finds no `hooks.py` | Decided 2a: refuse the push and list the searched paths |
| F5 | `git rev-parse --git-path hooks` returns the shared `.git/hooks` from a run worktree, checked in a temp repo; `core.hooksPath` changes that path | Install writes there, so one install covers every worktree. A set `core.hooksPath` refuses, per B6 |
| F6 | gitleaks 8.30.1 with `--log-opts="<sha> --not --remotes=<remote>"` scans only commits no remote ref holds. A planted `ghp_` token exits 1 with `RuleID: github-pat`, `File:` and `REDACTED`; an empty range exits 0. Checked in a temp repo | Pre-push scans that range per pushed ref. It skips a delete, whose local sha is all zeros, which `run-worktree.py land` sends (run-worktree.py:171) |
| F7 | checkup's `config.md` says to quote `config-scan.py` lines and never open settings files, because they may hold secrets | B8 becomes a `config-scan.py` check with unit tests. This corrects the brief's grep-only seam for B8 |
| F8 | 5 of the 8 `config-scan.py` tests assert exact output with Claude settings present (test_config_scan.py:39-114) | The new line prints only in a repo with `.workflow/`, where the hooks matter, so no existing test changes |
| F9 | Claude deny rules match `*` anywhere and catch subcommands of a compound command. They miss `git -C . push`, `sh -c` and `git commit -n` (Claude Code permissions docs, Bash rule limits) | The printed rules are `Bash(git commit *--no-verify*)` and `Bash(git push *--no-verify*)`. They stop the usual form only |
| F10 | `ROUTING.md` puts every execute seat on Codex, whose command rules match an exact token prefix and are marked experimental | Decided 3a: Claude rule only. The hooks still run under any harness, because git runs them |
| F11 | `secret-scan.md` offers "push unscanned", and README.md:213 says "Without it the agent asks before pushing". Both assume no hook | T2 rewords both: the human pushes unscanned with `--no-verify` |
| F12 | Reuse: test_config_scan.py:9-10 builds secret strings at runtime; test_run_worktree.py:14-46 builds a repo with a bare origin; no script has an install, marker or skill-path helper | `test_hooks.py` builds its token the same way and keeps its own short repo setup, because tests.md bans importing a test module |
| F13 | Lightest shape: one `hooks.py` with `install`, `pre-commit` and `pre-push`, two shell stubs of about 10 lines, one `config-scan.py` check. Cost: about 0.1 s per run-file commit, about 0.3 s per push, one install per clone per machine | No brief decision adds a deploy, a pin or an approval |
| F14 | D1 searches the repo's own copy first | F15 puts the folder `install` ran from first, so a repo copy runs only when that folder is gone. Listed in Risks |
| F15 | The workflow README's Install section puts the skill in the repo's `.agents/skills/workflow`, linked from `.claude/skills` and `.codex/skills`. Its table adds `~/.codex/skills`, `$CODEX_HOME/skills` and `~/.copilot/skills`. D1's three paths miss all of them, so a README install would warn on every commit and, with 2a, refuse every push | Corrects D1 for any harness: the stub searches the folder `install` ran from first, then each folder in the README table, repo before home. Hook text in SKILL.md names no harness (MAINTAINING.md, Vendors) |

## Tickets

### T1 — Install the hooks and gate run-artifact commits on check-run
Delivers: B4, B5, B6 · Blocked by: none · Lane: logic
Budget: code +95 · tests +100 · why: each case builds a temp repo and commits through real git
Seam: `hooks.py install` and `git commit` in a temp repo with HOME set to an empty temp folder
Accept:
- [ ] Install in a repo with no hooks → `pre-commit` and `pre-push` written, executable, marker line in each; a second install leaves both files byte-identical (B6)
- [ ] A foreign `pre-push` hook, and separately a set `core.hooksPath` → exit 1, output names it, no hook file written (B6)
- [ ] Commit staging `.workflow/r/brainstorm.md` without a provenance header → refused, output holds check-run's `ERROR` line (B4)
- [ ] Commit staging a drafting brief that only warns → allowed; commits staging `src.py` alone and `.workflow/.gitkeep` alone beside a committed broken run → allowed (B4)
- [ ] Install folder deleted, copy linked at the repo's `.agents/skills/workflow` → a broken run's commit is refused; no copy anywhere → allowed, stderr lists every searched path (B5)
- [ ] SKILL.md's artifact rule is one line naming the pre-commit hook; bootstrap.md step 5 runs `hooks.py install` (grep count 1 each)
Verify: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests -p test_hooks.py -k PreCommit -k Install && grep -c 'pre-commit hook' .github/skills/workflow/SKILL.md && grep -c 'hooks.py install' .github/skills/workflow/references/bootstrap.md` (pre: new file, NO TESTS RAN exit 5 · greps 0)
Skills: .github/skills/agent-docs/SKILL.md
Status: todo

### T2 — Refuse a push that carries a secret or skips the scan
Delivers: B1, B2, B3 · Blocked by: T1 · Lane: logic
Budget: code +35 · tests +50 · why: each case pushes through real git to a bare origin
Seam: `git push` from a temp repo with the hooks installed to a bare origin
Accept:
- [ ] Push of a commit holding a `ghp_` token built at runtime → refused; output has `RuleID: github-pat` and `File:`, and lacks the token (B1)
- [ ] Secret already on origin, then a new branch with one clean commit and no upstream → push exits 0; deleting that branch on origin → exits 0 (B2)
- [ ] PATH without gitleaks → push refused, output says to install gitleaks (B3)
- [ ] Stub finds no `hooks.py` → push refused, stderr lists every searched path (2a)
- [ ] SKILL.md's scan rule is one line naming the pre-push hook; secret-scan.md and README.md say the human pushes unscanned with `--no-verify`
Verify: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests -p test_hooks.py -k PrePush && grep -c 'pre-push hook' .github/skills/workflow/SKILL.md README.md && grep -c 'no-verify' .github/skills/workflow/references/secret-scan.md` (pre: new file, NO TESTS RAN exit 5 · greps 0)
Skills: .github/skills/agent-docs/SKILL.md, .github/skills/plain/SKILL.md
Status: todo

### T3 — checkup reports missing hooks and an open --no-verify
Delivers: B7, B8 · Blocked by: T1 · Lane: logic
Budget: code +35 · tests +45 · why: one case per deny key plus the repo and no-repo cases
Seam: `hooks.py install --check` and `config-scan.py` run as subprocesses in temp repos and homes
Accept:
- [ ] `install --check` in a repo missing both hooks → prints `would install pre-commit, pre-push` and writes nothing; with both installed → prints `installed` (B7)
- [ ] `config-scan.py` in a repo with `.workflow/` and Claude settings denying neither command → one ⚠️ line holding both exact rules (B8)
- [ ] Deny list with only the commit rule, then only the push rule → the line prints; both rules, then `Bash(git *--no-verify*)` alone → no line (B8)
- [ ] A repo without `.workflow/` and the same settings → no line, and the existing 8 config-scan tests pass unchanged (B8)
- [ ] checkup `workspace.md` runs `hooks.py install --check`, `config.md` names the `--no-verify` line, SKILL.md's safe-fix list has the hook install (B7)
Verify: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests -p test_hooks.py -k HookCheck && python3 -m unittest discover -s .github/skills/checkup/scripts/tests -k NoVerify && grep -c 'hooks.py install --check' .github/skills/checkup/references/workspace.md && grep -c 'no-verify' .github/skills/checkup/references/config.md && grep -c 'hooks.py install' .github/skills/checkup/SKILL.md` (pre: new file, NO TESTS RAN exit 5 · greps 0)
Skills: .github/skills/agent-docs/SKILL.md
Status: todo

## Coverage
- Outcome → T2 refuses the push and names the cause, T1 refuses the commit and makes bootstrap install, T3 makes checkup report, T1 and T2 shrink the two SKILL.md rules
- B1 → T2 · B2 → T2 · B3 → T2 · B4 → T1 · B5 → T1 · B6 → T1 · B7 → T3 · B8 → T3
- Out of scope: `retire-on-no-signal` and `correction-mining` → untouched · CI job → untouched · chaining onto existing hooks → T1 refuses instead · editing user settings → T3 prints the rule only · gitleaks configuration → untouched

## Risks
T1 is riskiest: its stub runs on every commit in every repo that installs it, so a bug blocks commits. Its tests drive real git.
With hooks installed, `run-worktree.py land` pushes the primary branch and deletes `run/<slug>` through pre-push (run-worktree.py:169-171). T2's delete case covers the second push.
Not taken: a Codex rule (3a), chaining onto foreign hooks (D4). `git commit -n`, `git -c core.hooksPath=` and `git -C` still skip the hooks (F9).
Trust: the stub searches the README's install folders as well as the brief's three; the folder `install` ran from goes first (F15).

## TODO impacts
none: the brief came from ROADMAP.md row 1, not TODO.md

## Product doc impacts
- PRODUCT.md, DESIGN.md: not in this repo
- ROADMAP.md: row 1 `git-hooks` is done at wrap; its open question, how a hook finds `check-run.py` on both machines, is answered by D1
- README.md:211-213: "Without it the agent asks before pushing" becomes untrue; T2 replaces it with "the pre-push hook refuses the push"

## Deviations
- T1: corrected the new warning assertion from `WARN` to `warnings`, matching the checker output. No existing assertion changed.
