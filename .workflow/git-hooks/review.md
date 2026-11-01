Command: workflow review git-hooks
Created: 2026-11-01 · Claude Opus 5.5
Base:    a152e3e
Inputs:  .workflow/git-hooks/plan.md @ 90b7bd1
Status:  done

## Coverage
- [x] T1 — acceptance 6/6 tested and passing; `grep -c 'pre-commit hook'` SKILL.md 1, `hooks.py install` bootstrap.md 1
- [x] T2 — acceptance 5/5 tested and passing; B1 fails for one input after C1-T1, see C2-1
- [x] T3 — acceptance 5/5 tested and passing
- [x] C1-T1 — spaced-target test passes; reverting the fix fails it; M14 now killed. The fix opens C2-1 and adds an untested guard, C2-2
- [x] C1-T2 — M7, M10, M11, M22 each killed in a throwaway worktree
- [x] C1-T3 — greps 2 · 1 · 0 as accepted; no other prose site names the old hub scan (`design/SKILL.md:95` keeps its own scan, out of scope)
- [x] C1-T4 — grep 1
- [x] C1-T5 — narrow subtest passes; each probe string reverted on its own survives, see C2-3
- [x] C2-T1 — new two-remote test passes; M1 plain `--remotes`, M2 always `--remotes=<name>`, M4 gitleaks range plain, M5 condition inverted each fail a PrePush test
- [x] C2-T2 — unknown-sha test passes; M3 guard disabled fails it
- [x] C2-T3 — each probe reverted alone at `config-scan.py:181` fails the NoVerify test
- [x] Red commits 860ebb2, 5d4f0a8, 4e10116 touch tests only; fix commits a2d308f, 1c09a05, 0cf89fa touch no test file
- [x] B1…B8 delivered · Outcome observed via manual run, no verify skill: real `git push` through the installed stub in `test_PrePush_secret_on_other_remote_is_refused` (two bare remotes) refuses, token absent, `origin` lacks the ref · out of scope untouched
- [x] .workflow/ dependency check: no new hits · escape-hatch scan: no hits · new dependencies: none
- [x] Full suites at a152e3e: workflow `Ran 124 tests` OK, checkup `Ran 9 tests` OK, exit 0
Size: +157 code · +246 tests · ratio 1.57 · net +402 · over 1,000: none · `Ratio waived: run` accepted: each added case guards a regression a review reported
Reachability: `hooks.py` → the installed stubs; `no_verify()` → `config-scan.py main()` · guards shown failing: M7, M10, M11, M14, M22, C1-T1 revert, M1–M5, both probe members
Independence: cross-vendor (writer GPT-6.1 Sol / OpenAI · reviewer Claude Opus 5.5 / Anthropic)
Threats: hook stub → hooks.py · git sends ref lines on stdin and the remote name or URL as `$1`; `$1` no longer enters any command · it reaches `python3`, `check-run.py`, `git rev-list` and `gitleaks` · it only allows or refuses the commit or push · gitleaks prints redacted output · fails open only for a push to a URL or path (all remotes excluded, as agreed in C2-T1) or a nested remote name, C3-1 · worst case: a secret already on a private remote reaches a public one
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
| C2-1 | P1 | pre-push skips commits that are already on another remote | fix now | @ 0cf89fa (cycle 3) |
| C2-2 | P1 | The new rev-list guard has no test | fix now | @ ffc3856 (cycle 3) |
| C2-3 | P1 | Each --no-verify probe can regress alone unseen | fix now | @ 3368007 (cycle 3) |
| C2-4 | P3 | Manual fallback scan passes silently with no upstream (`SKILL.md:157`) | defer — stays here | settled (cycle 3) |

## Cycle 3 findings
### P3 — Minor, deferred (C3-1)
- `--remotes=<name>` is a glob with `/*` implied, so a push to `origin` also excludes commits held only by a remote named `origin/sub` (git allows `/` in remote names; checked with `git rev-list HEAD --not --remotes=origin` → 0 lines). Rare naming.
- A push to a URL or path still excludes every remote, as C2-T1 agreed; `git push <url>` with a secret already on a private remote passes.
- Both rest on remote-tracking refs, which can be stale; predates this cycle.
- Disposition: defer — stays here
- Resolved: —

## Pre-existing / environmental
- This repo has no hooks installed yet. Installing them is checkup's opt-in fix, D3, and is the human's call.

## Cycle 2 verdict
Cycle 3 approved by human: 2026-11-01, answer "1a" to the cycle-bound question. `patch_plan.md` holds C2-T1 to C2-T3.

## Cycle 3 verdict
Ship as-is. C2-1, C2-2 and C2-3 are fixed at every site: `hooks.py:95` builds the one range that both the guard and gitleaks use, and every mutation of the new condition fails a test. No regression in the fix diff; 1 new P3, deferred. Next: wrap.
