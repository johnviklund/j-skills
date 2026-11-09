# Worklog

A bounded, rolling, git-pointing index of what was built or changed in this repo, newest first.
Not a source of truth and not an archive — canonical docs and the git history own
that; entries only point at commits. Cap: keep roughly the 15 most recent entries; delete the
oldest when appending would exceed that.

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

## 2026-11-02 · correction-mining · a stdlib script lists repeated denials, interrupts and redirects from Claude, Codex and Copilot transcripts · GPT-6.1 Sol
- `checkup/scripts/corrections.py` prints repeated denials and interrupts and the redirect turns to stdout only; `checkup` reports the top 5 repeats and `retro` cites one in its *Recurring* test.
- Two review cycles found 2 P1 (an unmatched quote in a denied command crashed the report; 15 of 48 mutants survived the writer's sweep); both fixed, 1 P2 deferred to `TODO.md`, 5 P3 stay in `review.md`.
- Commits: 00623b1 a5cd7fc 5683806 eecbc49 9911caa c3a6606 f7c04bf
- Review: ship as-is (cycle 2, 0 open) @ 77efe6d
- Run: 3 tickets · 3 sessions · 2 review cycles · 4 deviations · 0 findings overturned · net code +182 · tests +218
- Seats: 0 Sonnet 5.5 · 2 Opus 5.5 · 3 GPT-6.1 Sol · 4 Opus 5.5
- Skills: workflow@11e805e2c25a, checkup@ef4000aec266
- Why: corrections the human gives are counted across sessions, so a repeat becomes visible without anyone running `retro` on each one.

## 2026-11-01 · retire-on-no-signal · skill trials end in keep, insurance or a removal candidate, counted from save tags · GPT-6.1 Sol
- `skill-trials.py` counts `[saved→skill]` tags per `SKILL-IMPACT.md` row and judges finished trials by saves and `Run:` numbers; `--sweep` labelled all 37 open rows, and the human confirmed each (no removal).
- Four review cycles found 1 P0 (archive rows with `\|` crashed the report) and 5 P1/P2 defects, mostly tests that missed one side of a guard; all fixed, 1 P3 group stays in `review.md`.
- Commits: 3aeab1c 1ad5a7d dcaedc4 953e4ac a8b72da 25a4739 2dc5056
- Review: ship as-is (cycle 4, 0 open) @ d1c3141
- Run: 3 tickets · 7 sessions · 4 review cycles · 1 deviations · 0 findings overturned · net code +112 · tests +219
- Seats: 0 Sonnet 5.5 · 2 Opus 5.5 · 3 GPT-6.1 Sol · 4 Opus 5.5
- Skills: workflow@ef6309467514, checkup@1d1808312d83
- Why: a skill rule now earns its place on a recorded save, and "no signal" no longer means keep.

## 2026-11-01 · git-hooks · pre-commit and pre-push hooks enforce the run check and the secret scan · GPT-6.1 Sol
- `hooks.py` installs a pre-commit hook (runs `check-run.py` on staged run files) and a pre-push hook (gitleaks over the commits the push adds); `bootstrap` installs them and `checkup` flags a repo without them or with an open `--no-verify`.
- Three review cycles found 9 defects (a secret passing a spaced push target, commits on another remote skipped, 3 untested guards); all fixed, 2 P3s stay in `review.md`.
- Commits: f1ed6eb 2556e51 cb2e649 a2d308f d6de8e2 8667607 0cf89fa ffc3856 3368007
- Review: ship as-is (cycle 3, 0 open) @ a152e3e
- Run: 3 tickets · 4 sessions · 3 review cycles · 5 deviations · 0 findings overturned · net code +157 · tests +246
- Seats: 0 Sonnet 5.5 · 2 Opus 5.5 · 3 GPT-6.1 Sol · 4 Opus 5.5
- Skills: workflow@83f608b20044, checkup@a71b8a916aee
- Why: the secret scan and the run check stop depending on an agent reading prose.

## 2026-11-01 · lean-workflow-tests · workflow test suites fold duplicate cases and lose no covered line or caught mutant · GPT-6.1 Sol
- Shared helpers (`fails()`, `run_command(expected=)`, `check(checkout=)`) and folded cases cut the workflow tests from 120 to 112 and 1,630 to 1,565 lines; the checkout test moved to check-run; median suite time 52.3 to 50.9 s.
- The coverage map and mutation run (with message-string and `1.5` mutants) from the run's own tool lose nothing: `compare.py base final` → `lost 0`, and four hand mutants agree.
- Commits: 6bdf81d e86f78a d508b3a 6c4b4ca a13c5a2 961deed
- Review: ship as-is (cycle 2, 0 open) @ 2a8e5fc
- Run: 5 tickets · 5 sessions · 2 review cycles · 5 deviations · 0 findings overturned · net code +0 · tests -65
- Seats: 0 Opus 5.5 · 2 Opus 5.5 · 3 GPT-6.1 Sol · 4 Opus 5.5
- Skills: workflow@306d1f188783, checkup@20651cbda779
- Why: stop the tests growing faster than the scripts, with proof that nothing covered was lost.

## 2026-10-30 · model-overrides · a run's routing.md overrides the model and effort for its own cards · GPT-6.1 Sol
- A headerless `routing.md` in a run folder sets that run's model and effort per key; `next-step.py` shows `(override)` and warns when writer and reviewer share a vendor, `check-run.py` validates the rows, and done runs skip the check.
- Review cycle 1 found 2 small P2s (done runs broke on a retired key; review and execute still read only `ROUTING.md`), both fixed; 3 P3s stay deferred in `review.md`.
- Commits: d9a0f8f 4db8014 4b37b24 5d2d876 a4135aa 4d53dcb
- Review: ship as-is (cycle 2, 0 open) @ 7689d09
- Run: 2 tickets · 3 sessions · 2 review cycles · 1 deviations · 0 findings overturned · net code +38 · tests +78
- Seats: 0 Sonnet 5.5 · 2 Opus 5.5 · 3 GPT-6.1 Sol · 4 Opus 5.5
- Skills: workflow@62d05781d2ed, checkup@20651cbda779
- Why: the human can try a model on one run without editing the shared mapping.

## 2026-10-30 · unattended-mode · a run can say it is unattended and its waiting questions reach the conductor as a blocker · GPT-6.1 Sol
- `Mode: unattended` in a brief, `references/unattended.md` (defaults, always-stop list), checked `decisions.md` tables, a `next-step` blocker for `waiting` rows, and an execute decision keeps a run in its original checkout; workflow is 3.0.0.
- Three review cycles found 3 defects fixed (UI code lost at an approval stop, resume in the wrong checkout) and left 2 deferred to `TODO.md` (a one-row fixture, an unhandled `ValueError`).
- Commits: 39fe912 b5b8642 23f4ec6 2e8ad60 056a042 f268f88
- Review: ship with 2 deferrals approved by the human (cycle 3) @ 91e6d9d
- Run: 5 tickets · 3 sessions · 3 review cycles · 1 deviations · 0 findings overturned · net code +27 · tests +63
- Seats: 0 Sonnet 5.5 · 2 Opus 5.5 · 3 GPT-6.1 Sol · 4 Opus 5.5
- Skills: workflow@9638c307782f, checkup@20651cbda779
- Why: an outside conductor needs fixed rules and a blocker for runs nobody watches.

## 2026-10-30 · next-step · a script decides each run's next step, and the cards print its output · GPT-6.1 Sol
- `next-step.py` reads a run's files and ROUTING.md (now keyed tables) and prints the closing card or schema-1 JSON; `workflow next` and `status` print it, patch tickets carry `Fixes:`, and checkup copies its model lines from `--key`.
- Four review cycles found 8 defects (open findings read from the latest cycle only, backticked receipt paths, shifted finding ids, 4 untested guards); all fixed. Four missed P1s went to the private exam set.
- Commits: 904f083 70fefa2 17c8020 53d959c a354025 e6a8e5d f2bba2b 0762b64 eac69f8 5c5e306 3b72722 0485880
- Review: ship as-is (cycle 4, 0 open) @ 91a5e68
- Run: 13 tickets · 7 sessions · 4 review cycles · 0 deviations · 0 findings overturned · net code +272 · tests +408
- Seats: 0 Sonnet 5.5 · 2 Opus 5.5 · 3 GPT-6.1 Sol · 4 Opus 5.5
- Skills: workflow@adfa1601a336, checkup@20651cbda779
- Why: a script, not model judgement, must pick the next step so an outside conductor can drive runs.

## 2026-10-28 · lean-skill-hubs · six large skill hubs now load only the branch a run needs · GPT-6.1 Sol
- `memory.remember`, `memory.compact`, `workflow`, `checkup`, `understand` and `verify` keep in `SKILL.md` only what every run needs; branch text sits in linked `references/` files (checkup one file per scope word, verify one per command). Hub sizes: workflow 13,238 to 11,499 bytes, checkup 23,975 to 6,058, verify 14,934 to 2,914.
- A sentence ledger (`.workflow/lean-skill-hubs/scripts/`) accounts for every removed sentence as moved, duplicate or unaccounted; all six end at 0 unaccounted. Installed copies match the repo. Cycle 1 found an untested ledger window (P1) and five stale pointers (P3); both fixed.
- Commits: 526f6a4 f7a16ad efc114a fb6a5d2 b640a54 6973783 076d68d 778f70f 2f648a8 be06046
- Review: ship as-is (cycle 2, 0 open) @ 3386bbf
- Run: 8 tickets · 4 sessions · 2 review cycles · 6 deviations · 0 findings overturned · net code +83 · tests +88
- Seats: 0 Opus 5.5 · 2 Opus 5.5 · 3 GPT-6.1 Sol · 4 Opus 5.5
- Skills: workflow@a7eb94288836, memory.remember@d8c8240e4b0d, memory.compact@2aeb788ce0b3, checkup@233d43b063f1, understand@dee283ef87c6, verify@af376476763a
- Why: seven skill files were over the ~10 KB budget, so every load paid for text most runs never used.

## 2026-10-28 · run-worktrees · parallel runs work in their own git worktrees · GPT-6.1 Sol
- Each run can execute in `.worktrees/<slug>` on `run/<slug>`; `run-worktree.py` opens, finds, lands and diagnoses them, every phase resolves its checkout from the slug, and wrap lands the branch without touching another run's files. A second clone rebuilds a worktree from `origin/run/<slug>`.
- Proved on scratch repos through the test harness, not a live parallel run. Seven review cycles found 11 P1/P2 defects (unscanned pushes at landing, setup parsing, offline lookup, 25 surviving mutations); all fixed. P3s stayed in review.md.
- Commits: 81aa880 c601aa0 7473b02 27f1f39 b7d369a b890db3 f61de07
- Review: ship as-is (cycle 7, 0 open) @ 4b43be1
- Run: 5 tickets · 10 sessions · 7 review cycles · 1 deviations · 0 findings overturned · net code +203 · tests +529
- Seats: 0 Opus 5.5 · 2 Opus 5.5 · 3 GPT-6.1 Sol · 4 Opus 5.5
- Skills: workflow@5921f6619095, memory.remember@4416cf26dc14
- Why: two runs at once mixed uncommitted edits and broke tests, clean-tree and freshness checks.

## 2026-10-26 · memory-patterns-and-budget · compact finds repeated lessons without a page; remember checks what an AGENTS.md rule costs · GPT-6.1 Sol
- `memory.compact` now reads the last ~10 done runs' `learnings.md` and proposes a page when two runs share a cause and a fix. `memory.remember` asks whether removing a new `AGENTS.md` rule would cause a mistake; a no routes it to a memory page or skill reference, and a rule near a stated line cap names one line to move.
- Proved by desk checks on the real `learnings.md` files, not live runs. Review cycle 1 found the cost test left an operating rule with no destination (the admission test refused a page for it); fixed in one line. Four P3s deferred.
- Commits: 94f353b 43588b3 fec0e26
- Review: ship as-is (cycle 2, 0 open) @ 0e9d13b
- Run: 3 tickets · 2 sessions · 2 review cycles · 0 deviations · 0 findings overturned · net code +0 · tests +0
- Seats: 0 Sonnet 5.5 · 2 Opus 5.5 · 3 GPT-6.1 Sol · 4 Opus 5.5
- Skills: workflow@b2bdc7fb117d, memory.remember@4416cf26dc14, memory.compact@6af004059efe
- Why: a lesson repeated across runs never got a page, and AGENTS.md took rules whose removal would cost nothing.
