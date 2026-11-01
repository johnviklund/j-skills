Command: workflow brainstorm git-hooks
Created: 2026-11-01 · Claude Sonnet 5.5
Base:    e3b8e98
Inputs:  none
Status:  complete
Mode: attended

## Problem
Two workflow ground rules are prose only: scan for secrets before every push, and commit a run artifact only after `check-run.py` passes. An agent that skips one is not stopped, and a review once went out citing files that did not exist. Git can enforce both, but hooks live outside the repo and `check-run.py` sits at different paths on the user's two machines.

## Outcome
In a repo with the hooks installed, `git push` with a secret in the outgoing commits fails, and `git commit` of a run artifact that fails `check-run.py` fails, both with a message naming the cause. `bootstrap` installs the hooks, `checkup` reports a repo without them and a machine that does not deny `--no-verify`, and the two prose rules in `workflow/SKILL.md` shrink to one line each pointing at the hooks.

## Behaviours
- B1 — `git push` with a planted secret in an outgoing commit → push refused, output names file and rule, the secret value is not printed
- B2 — `git push` of a clean new branch with no upstream → allowed, and only commits not already on the remote are scanned
- B3 — `git push` with `gitleaks` not installed → push refused, output says to install it
- B4 — `git commit` staging a file under `.workflow/<slug>/` whose run has a `check-run.py` error → commit refused with its errors; warnings only → allowed; no staged `.workflow/` path → `check-run.py` not run
- B5 — `git commit` staging a run file when no `check-run.py` is found → commit allowed, with a warning listing the paths searched
- B6 — install in a repo with no hooks → both hooks are stubs carrying a marker line; in a repo with a foreign hook or `core.hooksPath` → nothing changed and the output names it; a second install changes nothing
- B7 — `checkup` in a repo missing either hook → a finding with the install as an opt-in fix, one at a time
- B8 — `checkup` on a machine whose Claude settings lack a deny rule for `git commit --no-verify` and `git push --no-verify` → a finding that prints the exact rule

## Decisions
- D1 — hook stubs call `hooks.py` in the workflow skill, found in order: repo `.github/skills/workflow/scripts/`, `~/.agents/skills/workflow/scripts/`, `~/.claude/skills/workflow/scripts/` — logic updates with `npx skills update -g`, no hard-coded path (product call)
- D2 — pre-push blocks when `gitleaks` is missing; pre-commit warns and passes when `check-run.py` is missing — keeps today's no-unscanned-push rule without making a fresh clone uncommittable (product call)
- D3 — new repos get hooks from `bootstrap`, existing repos from `checkup`'s opt-in fix list — no new command (product call)
- D4 — install only when no hook exists or ours is there, marked by a comment line; never overwrite or chain (product call)
- D5 — `--no-verify` denial is a Claude settings rule per machine; `checkup` flags and prints it, the human applies it with `update-config` (product call)
- D6 — `check-run.py` warnings pass and errors block; a `drafting` brief with warnings exits 0 (code: workflow/scripts/check-run.py main, checked in a temp repo)
- D7 — pre-commit checks only the slugs of staged `.workflow/<slug>/` paths, not every live run (code: check-run.py accepts slugs)

## Test seams
- `hooks.py pre-push`, `pre-commit`, `install` run in temp git repos — exit code and output observe B1 to B6 (new)
- `checkup` reference text — B7, B8, verified by grep of the instruction, not by running (existing)

## Trust boundaries
- hook stub → `hooks.py` and `check-run.py` run from the home skill folders or the repo's own copy; shell execution on every commit and push, so only the three listed paths are searched, never `PATH` or the repo's other files

## Out of scope
- `retire-on-no-signal` and `correction-mining` — roadmap steps 2 and 3, own runs
- a CI job running the same checks — the hooks are the local half; CI is separate work
- chaining onto existing hooks or husky setups — D4 refuses instead
- editing user settings files from a skill — j-skills never does; D5 prints the rule
- gitleaks configuration changes — `secret-scan.md` already covers findings

Docs read: none in scope
