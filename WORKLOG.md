# Worklog

A bounded, rolling, git-pointing index of what was built or changed in this repo, newest first.
Not a source of truth and not an archive — canonical docs and the git history own
that; entries only point at commits. Cap: keep roughly the 15 most recent entries; delete the
oldest when appending would exceed that.

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

## 2026-11-18 · check-scope · check proves and reports; validate refuses reruns without input and receipts over 3 KB · claude-opus-5-5
- Check writes no unblock plans or cap requests, Maybes hold only suspected defects with a named input, and spec rules cover graded and keep rows; check cost the most time and 3.4 Maybes a check.
- Commits: edf6deb 75643a3 a6b37fe f833813 b9d49c8 a2656fa
- jflow: 9 sessions · 5 fix rounds · 8 rows · 2 accepted · check 10 defects · net code +48 · tests +83 · docs +13

## 2026-11-17 · jflow-size-room · jflow caps each step's reading and the script separately · gpt-6.1-sol
- The size guard allows 14,000 bytes for SKILL.md plus one step reference and 30,000 bytes for jflow.py, with the reason beside the limits.
- Commits: 0abe6bd d6c2ab1 b2169fd 18fdf49 026b1a0
- jflow: 4 sessions · 1 fix rounds · 5 rows · 0 accepted · check clean · net code +0 · tests +6 · docs +4

## 2026-11-12 · spec-why · jflow spec starts from the why and names the PRODUCT.md outcome it serves · Claude Opus 5.5
- spec reads PRODUCT.md, DESIGN.md and the roadmap item, asks the why first and never reopens what the item settled, and makes its Solved when Proof row 1; specs carry `Serves:`, which `validate` checks against PRODUCT.md's `###` outcomes; done reports row 1 and asks before editing PRODUCT.md or DESIGN.md. Workflow's brainstorm was the only step that asked why.
- Commits: 1361409 e9539bd 9b436c4 6171cae
- jflow: 6 sessions · 3 fix rounds · 5 rows · 0 accepted · check 7 defects · net code +8 · tests +34 · docs +1

## 2026-11-10 · jflow-validate · jflow rejects malformed run artifacts · GPT-6.1 Sol
- `validate` checks specs, newest receipts and Accepted lines; `record` refuses malformed output before changing the run log.
- Commits: 17afb7a 4d109e8 df19d36
- jflow: 5 sessions · 2 fix rounds · 10 rows · 0 accepted · check 2 defects · net code +106 · tests +236 · docs +4

## 2026-11-09 · wait-points · `jflow.py next` stops at the approach, the live gate and before done · Claude Opus 5.5
- `next` now stops for the human at an approach posted for an Ask first item, at the live `Gate:`, and before done when there are Human checks or Maybes, until `notes.md` has `Yes: approach`, `Yes: gate` or `Yes: done`; a conductor reading only the JSON can no longer run past them. Also stops `section` dropping a real line that starts with "None".
- Commits: f329eaa 4121af0 2f8aaa8
- jflow: 4 sessions · 1 fix rounds · 9 rows · 0 accepted · check 1 defects · net code +27 · tests +27 · docs +9

## 2026-11-09 · jflow-next · `jflow.py next` decides a run's next step · Claude Opus 5.5
- `next <slug>` reads the run folder and git and prints the closing card, or with `--json` the step, seat, role, session and any blocker for the human, so a driver needs no prose table; it applies the check cap and `Checks allowed: N`, and an acceptance closes only the item and check it names. Also fixes `summary` ending a run at Base when its spec quotes `Status: done`.
- Commits: ecac1d8 38b1e04 f6fb039 046bb7e 7acdd9b
- jflow: 7 sessions · 4 fix rounds · 11 rows · 0 accepted · check 5 defects · net code +111 · tests +95 · docs -5

## 2026-11-08 · jflow-config · JSON seats and flow metadata for jflow · GPT-6.1 Sol
- Seat lookup merges defaults, repo and explicit config, applies the vendor default and prints locked rules. Config and record model/effort values reject key-like data.
- Commits: e08114c f376c4b 1a8708a 832708f 1f0389c
- jflow: 7 sessions · 4 fix rounds · 10 rows · 0 accepted · check 4 defects · net code +83 · tests +101 · docs +11

## 2026-11-08 · drive-py-at-done · jflow deletes a run's drive.py at done · Claude Opus 5.5
- Done step 6 removes the checker's one-off driver with `git rm`; a reusable verb becomes one `TODO.md` line for `verify.maintain`, and a receipt's driver reruns from the receipt's own commit.
- Commits: 61860aa 04beb5f 1ddb4aa 651c81f c193232
- jflow: 4 sessions · 1 fix rounds · 8 rows · 0 accepted · check 1 defects · net code +0 · tests +0 · docs +10

## 2026-11-08 · receipt-evidence-cap · jflow caps receipt evidence at 240 characters · GPT-6.1 Sol
- Evidence keeps the command and decisive output line within 240 characters; defect references avoid repetition.
- Commits: 2cd2359 3ad0bd2 458473c 03e783e a2e921d
- jflow: 4 sessions · 1 fix rounds · 6 rows · 0 accepted · check 1 defects · net code +0 · tests +0 · docs +6

## 2026-11-04 · corrections-bad-records · `corrections.py` skips a malformed transcript instead of losing the whole report · Opus 5.5
- One catch per transcript across Claude, Codex and Copilot keeps the report alive and the readable transcripts counted; a lone surrogate now prints as `?`. Closes correction-mining C2-1.
- Commits: 90b326c e771ae9 24e45af ed8dbbf
- jflow: 4 sessions · 0 fix rounds · 4 rows · review clean · net code +5 · tests +30
