Command: workflow review git-hooks
Created: 2026-11-01 · Claude Opus 5.5
Base:    d3df91f
Inputs:  .workflow/git-hooks/plan.md @ 90b7bd1
Status:  complete

## Coverage
- [x] T1 — acceptance 6/6 tested and passing; `grep -c 'pre-commit hook'` SKILL.md 1, `hooks.py install` bootstrap.md 1
- [x] T2 — acceptance 5/5 tested and passing; B1 fails for one input after C1-T1, see C2-1
- [x] T3 — acceptance 5/5 tested and passing
- [x] C1-T1 — spaced-target test passes; reverting the fix fails it; M14 now killed. The fix opens C2-1 and adds an untested guard, C2-2
- [x] C1-T2 — M7, M10, M11, M22 each killed in a throwaway worktree
- [x] C1-T3 — greps 2 · 1 · 0 as accepted; no other prose site names the old hub scan (`design/SKILL.md:95` keeps its own scan, out of scope)
- [x] C1-T4 — grep 1
- [x] C1-T5 — narrow subtest passes; each probe string reverted on its own survives, see C2-3
- [x] Red commits 860ebb2, 5d4f0a8 touch tests only; fix commits a2d308f, 1c09a05 touch no test file
- [x] B1…B8 delivered, B1 with the C2-1 hole · Outcome observed via manual run, no verify skill: temp repo with two remotes, see C2-1 · out of scope untouched
- [x] .workflow/ dependency check: no new hits · escape-hatch scan: no hits · new dependencies: none
- [x] Full suites at d3df91f: workflow `Ran 122 tests` OK, checkup `Ran 9 tests` OK, exit 0
Size: +156 code · +223 tests · ratio 1.43 · net +378 · over 1,000: none
Reachability: `hooks.py` → the installed stubs; `no_verify()` → `config-scan.py main()` · guards shown failing: M7, M10, M11, M14, M22, C1-T1 revert; not shown: the rev-list guard (C2-2), each probe member (C2-3)
Independence: cross-vendor (writer GPT-6.1 Sol / OpenAI · reviewer Claude Opus 5.5 / Anthropic)
Threats: hook stub → hooks.py · git sends ref lines on stdin and the remote name or URL as `$1`; `$1` no longer enters any command · it reaches `python3`, `check-run.py`, `git rev-list` and `gitleaks` · it only allows or refuses the commit or push · gitleaks prints redacted output · fails open for commits already on any other remote, C2-1 · worst case: a secret reaches a public remote
Threats: config-scan → Claude settings · unchanged from cycle 1: reads only `permissions.deny` strings, prints a fixed line, fails closed

## Resolved
| Finding | Sev | Title | Disposition | Resolved |
|---|---|---|---|---|
| C1-1 | P1 | pre-push lets a secret through when the push target holds a space | fix now | @ a2d308f (cycle 2) |
| C1-2 | P1 | A repo without the hooks loses both rules | fix now | @ 8667607 (cycle 2) |
| C1-3 | P1 | Four more hooks.py mutations survive | fix now | @ d6de8e2 (cycle 2) |
| C1-4 | P2 | The --no-verify check accepts deny rules that block only the bare form | fix now | @ 1c09a05 (cycle 2) |
| C1-5 | P2 | SKILL.md dropped a rule the hook does not cover | fix now | @ fb9bf81 (cycle 2) |
| C1-6 | P3 | Minor, deferred (redundant `is_file()`, foreign-hook decode traceback, `git commit:*` false warning; the bare-URL item is fixed by C1-T1) | defer — stays here | settled (cycle 2) |

## Cycle 2 findings
### P1 — pre-push skips commits that are already on another remote (C2-1)
- Evidence: B1 · regression from C1-T1. `hooks.py:104` now excludes `--remotes` (every remote), where it used to exclude only the push target. Temp repo with remotes `work` and `origin`: a `ghp_` commit reaches `work` without the hook (another clone, a teammate's branch), then `git push origin HEAD:refs/heads/feature` exits 0 and the public remote holds the commit. The same push under the 6ea2df2 `hooks.py` exits 1. The `remote` parameter at `hooks.py:90` is now unused (same-run waste).
- Remedy: when `$1` is a name in `git remote`, exclude `--remotes=<name>` (git refuses remote names with spaces); for a URL or path, keep `--remotes`. Use the same range in the rev-list guard. One test: two remotes, secret on `work`, push to `origin` refused.
- Disposition: fix now — escalated, cycle bound reached
- Resolved: —

### P1 — The new rev-list guard has no test (C2-2)
- Evidence: `hooks.py:100-102` · disabling the guard keeps all 122 tests green. The guard matters: with it disabled, `hooks.py pre-push origin` given an unknown sha on stdin prints `scanned ~0 bytes`, `no leaks found` and exits 0; with it, exit 1. Same class as a case in the private reviewer exam set.
- Remedy: one `PrePush` test feeding an unknown sha to `hooks.py pre-push origin` → exit 1, stderr names the ref.
- Disposition: fix now — escalated, cycle bound reached
- Resolved: —

### P1 — Each --no-verify probe can regress alone unseen (C2-3)
- Evidence: `config-scan.py:181` · reverting only the commit probe to `Bash(git commit --no-verify)` survives, and so does reverting only the push probe: the `narrow` subtest narrows both rules, so the other probe still prints the line.
- Remedy: two more subtests in `test_config_scan.py`: `[narrow commit, wide push]` and `[wide commit, narrow push]`, each → the line prints.
- Disposition: fix now — escalated, cycle bound reached
- Resolved: —

### P3 — Minor, deferred (C2-4)
- The manual fallback `gitleaks git --log-opts="@{u}..HEAD"` (`SKILL.md:157`) exits 0 with `no leaks found` on a branch with no upstream, because gitleaks passes a failed git log. The rule says to switch ranges in that case; the text predates this run.
- Disposition: defer — stays here
- Resolved: —

## Pre-existing / environmental
- This repo has no hooks installed yet. Installing them is checkup's opt-in fix, D3, and is the human's call.

## Cycle 2 verdict
Cycle 1's five findings are fixed. Cycle 2 found 3 new P1 and 1 P3. C2-1 breaks B1. The two-cycle limit is reached, so the three P1s wait for the human: a third cycle or a deferral.
