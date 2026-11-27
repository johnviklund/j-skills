# Worklog

A bounded, rolling, git-pointing index of what was built or changed in this repo, newest first.
Not a source of truth and not an archive — canonical docs and the git history own
that; entries only point at commits. Cap: keep roughly the 15 most recent entries; delete the
oldest when appending would exceed that.

## 2026-11-28 · #24 diff-triggered-reliability-checklist · jflow.py checklist prints the RELIABILITY.md items a run's diff triggers · claude-opus-5-5
- New `jflow.py checklist <slug>` or `--base <sha>` reads an optional `RELIABILITY.md`, matches each item's `Paths:` globs and `Match:` regex against `Base..HEAD`, and prints only the items that fire. A bad item fails and names its line. `references/check.md` has the checker run it during Attack, so past-incident rules no longer need room in the size-capped prompt. The code is in `scripts/jflow_checklist.py`.
- Commits: 31a0c1b 88b0195
- jflow: 4 sessions · 1 fix rounds · 7 rows · 0 accepted · check 4 defects · net code +128 · tests +133 · docs +3

## 2026-11-27 · #4 retro-reads-scores · retro and memory.compact read each run's run.jsonl and optional hq scores · claude-opus-5-5
- `retro` treats `run.jsonl` as its first source and opens a run's report with a `Run:` line of measured sessions, checks, fix rounds, defects, accepted, escaped, hours and seat models; a bare session with no `run.jsonl` omits the line. `memory.compact` picks the 10 newest done runs by their `done` line and reads `escaped` lines as signals; a `done` line counts only after the run's last `spec` line. Both read GitHub-mode runs through `jflow.py show` and run `hq scores` only when `hq` is on `PATH`.
- Commits: 691f55b dd332e9
- jflow: 4 sessions · 1 fix rounds · 7 rows · 0 accepted · check 1 defects · net code +0 · tests +0 · docs +20

## 2026-11-27 · #20 issue-card-confidence · Next cards state who they help, their sources and confidence, and Next prints in start order · claude-opus-5-5
- `roadmap check --github` now reports a Next card without `Helps`, `Moves` or `Challenges`, `Grounded in`, `Confidence` or an `Order` from 1 to 5, plus bad `Confidence` values, duplicate `Order`s and `After` inversions. All of these are `stale:` findings. A `challenges` card needs no `Serves:`, and `next --github` sorts Next by `Order`. The roadmap docs define the fields and a three-tier source rank. `jflow spec` opens on the weakest field, `jflow done` writes an `Impact check` line, and `bootstrap` has an optional `Weighs more:` line.
- Commits: 9aa7474 017afe9
- jflow: 4 sessions · 1 fix rounds · 9 rows · 0 accepted · check 3 defects · net code +69 · tests +49 · docs +56

## 2026-11-26 · #13 jflow-size-headroom · room under jflow's size caps for the next changes · claude-opus-5-5
- `jflow.py` drops from 30,179 to 26,895 of its 30,200 bytes: the seat, config and secret code moved unchanged into `scripts/jflow_seats.py`. `SKILL.md` plus `references/check.md` drops from 13,999 to 12,971 of 14,000 bytes by cutting repeated prose, with every rule kept. Three `TODO.md` items were waiting for this room.
- Commits: 48c1506
- jflow: 3 sessions · 0 fix rounds · 5 rows · 0 accepted · check clean · net code +8 · tests +0 · docs -14

## 2026-11-26 · #11 jflow-wrong-branch-error · GitHub mode names a wrong checkout instead of asking for a draft PR · claude-opus-5-5
- With no linked pull request and code past `Base`, `jflow_gh.py` now says `HEAD is on <branch>` (or `HEAD is detached`), `not jflow/<issue>`, and tells the user to check out `Base` or `jflow/<issue>`. Before this, it asked for a draft PR, which led agents to open blank pull requests from the wrong branch.
- Commits: 08c436f
- jflow: 3 sessions · 0 fix rounds · 6 rows · 0 accepted · check clean · net code +6 · tests +18 · docs +0

## 2026-11-26 · #14 jflow-build-fast-lint · builders run the fast static checks AGENTS.md lists and never silence them · claude-opus-5-5
- `references/build.md` now tells builders to run the lint and typecheck commands `AGENTS.md` lists before each `build` and `fix` commit, and to leave slow suites to `jflow done`. They may not silence a rule, weaken its severity or launder a type with an unsafe cast unless the exception has both an inline justification and a note in `notes.md`. Before this, lint errors first showed up at done, after check had passed.
- Commits: 760afc1
- jflow: 3 sessions · 0 fix rounds · 6 rows · 0 accepted · check clean · net code +0 · tests +0 · docs +6

## 2026-11-26 · #10 pr-mode-autopilot · issue and pull request mode stops only for real blockers · claude-opus-5-5
- In pull request mode, `jflow next` goes to done instead of stopping for `[edge]`-only defects, Human checks, Maybes or proposed edits, because the pull request is the review gate. Every stop now shows a Checker view and a Builder view line above its options (`scripts/jflow_views.py`). `done.md` and `github.md` say doc edits go in the PR diff, `[edge]` defects become caveats, and the PR body uses `plain` under What changed, What was proved and What you need to do.
- Commits: 7479e05 c6b5fcc
- jflow: 4 sessions · 1 fix rounds · 8 rows · 0 accepted · check 1 defects · net code +32 · tests +44 · docs +14

## 2026-11-26 · #6 roadmap-github-mode · `roadmap` manages GitHub issues and the `next` label, and `roadmap tidy` scans a wiki · claude-opus-5-5
- In jflow's GitHub mode, `roadmap.py next` and `check` read open issues through `gh`: `next` marks Next, the jflow labels mark in flight, the rest is Backlog. `check` caps Next at five and flags loose bodies. The new `roadmap.py wiki` lists changed wiki pages no open issue names, for `roadmap tidy` to propose at most three updates after the human's yes.
- Commits: 5b1a7d2 9a644b7 278ef23
- jflow: 5 sessions · 2 fix rounds · 6 rows · 1 accepted · check 5 defects · net code +148 · tests +141 · docs +73

## 2026-11-26 · #7 retro-memory-github-mode · `retro` and `memory.remember` read GitHub-mode runs through `jflow.py show` · claude-opus-5-5
- The new read-only `jflow.py show <#N|issue URL|slug>` prints a GitHub-mode run's trusted comments under the `.jflow/` file names. It also works on a merged run whose commits were pruned, and on a run with a spec and no PR. `retro #N` reads a run through it. `memory.remember` uses `#N` as Evidence and posts its routing summary with `jflow.py note`, which also no longer needs old commits.
- Commits: 6f5998b 34d32d6 64d9e8d
- jflow: 4 sessions · 1 fix rounds · 6 rows · 0 accepted · check 2 defects · net code +27 · tests +59 · docs +13

## 2026-11-25 · escaped-defects · `jflow.py escaped` records post-done bugs in `run.jsonl` · claude-opus-5-5 / gemini-4-neon
- `jflow.py escaped <slug> "<one line>" [--ref R]` appends a `"step": "escaped"` line to `.jflow/<slug>/run.jsonl`, `summary --json` counts non-zero escaped bugs without changing session or fix counts, and accepted defects stay in `## Accepted`. One check-5 `[edge]` URL qualifier defect is accepted and logged in `TODO.md`.
- Commits: 5d516ca 1fd7a03 edcc27d 99423d8 cb5e063
- jflow: 8 sessions · 4 fix rounds · 6 rows · 2 accepted · check 12 defects · net code +122 · tests +172 · docs -6

## 2026-11-25 · delete-workflow · the workflow skill is deleted; jflow is the one dev loop · claude-opus-5-5
- What other skills still needed moved out: the gitleaks pre-push hook to `jflow/scripts/hooks.py`, which upgrades old stubs; `SKILL-IMPACT.md` to checkup; seat and run readers to `jflow.py seat` and `.jflow/`. The README leads with jflow. Row 1's 91 history lines in SKILL-IMPACT are accepted.
- Commits: 4f5cf0f 8610b41 9e9120b
- jflow: 5 sessions · 2 fix rounds · 7 rows · 1 accepted · check 3 defects · net code -1632 · tests -1839 · docs -2485

## 2026-11-24 · headless-done-wait-point · jflow next types its wait points and stops at an `edits` point for an unattended done · claude-opus-5-5
- `next --json` adds `wait_point` (`approach`, `gate`, `done`, `edits`) only at a wait point, so conductor can stop reading blocker text. An unattended `done` writes `## Proposed edits` to `notes.md` and stops until `Yes: edits`; GitHub mode posts it as a note. Three re-spec edge cases are accepted and listed in `TODO.md`.
- Commits: f0b82e2 489ea32 cfafa0a 6cb8938 d62ff93
- jflow: 6 sessions · 3 fix rounds · 6 rows · 3 accepted · check 9 defects · net code +5 · tests +86 · docs +9

## 2026-11-23 · jflow-issue-pr-mode · jflow runs on pull-request-gated GitHub repos through issue and pull request comments · claude-opus-5-5
- `#42`, an issue URL, or `git config jflow.mode github` keeps the run in comments instead of `.jflow/` files. The spec and Accepted lines go on the issue; notes, receipts and records go on a draft pull request. The new `jflow_gh.py` rebuilds the comments as a temporary git history, so `jflow.py` makes the same decisions as in `.jflow/` mode. Each step reference ends with a short section on the mode.
- Commits: b92c671 de709e7 6827ad7 86bd967 693c986
- jflow: 6 sessions · 3 fix rounds · 9 rows · 0 accepted · check 9 defects · net code +294 · tests +458 · docs +115

## 2026-11-22 · jflow-next-properties · property tests check jflow.py next on generated run folders · claude-opus-5-5
- `test_next_properties.py` builds 50 seeded random run folders in real git repos, one of 8 stories per seed, and checks the step or human stop `next` picks against an oracle built from the generated run; every reintroduced past `next` bug fails it, and `jflow.py` is unchanged.
- Commits: 0d8ab1c 43ee16a b782169
- jflow: 5 sessions · 2 fix rounds · 7 rows · 1 accepted · check 9 defects · net code +0 · tests +184 · docs +0

## 2026-11-18 · check-reach · checkers tag defects [use] or [edge]; edge-only receipts stop for the human, not a fix round · claude-opus-5-5
- In check-scope, 6 of 10 defects used inputs normal work never makes and cost two fix rounds; `next` now offers to accept them, and `validate` refuses unknown or repeated tags and defect numbers.
- Commits: c86ae51 88c6157 f2ae69e
- jflow: 5 sessions · 2 fix rounds · 7 rows · 0 accepted · check 5 defects · net code -14 · tests +21 · docs +5
