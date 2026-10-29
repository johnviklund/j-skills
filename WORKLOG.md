# Worklog

A bounded, rolling, git-pointing index of what was built or changed in this repo, newest first.
Not a source of truth and not an archive — canonical docs and the git history own
that; entries only point at commits. Cap: keep roughly the 15 most recent entries; delete the
oldest when appending would exceed that.

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

## 2026-10-25 · checkup-next-actions · checkup reports questions, three action cards and a fixed ending · GPT-6.1 Sol
- Checkup's report format moved to `references/report.md`: numbered questions, at most three cards with a fresh-session prompt, the line `Safe fixes: none applied.`. Model lines come from ROUTING.md; unknown facts become questions with evidence paths.
- Proven on a synthetic fixture, not the live repo: the ending, card shape and question clauses passed. The model lines failed four paid attempts and the fresh-session proof never ran; a script for the model lines is in TODO.md.
- Commits: bc2a0e2 51a1e53 ee4c44e bfa6d38 b68c1ad
- Review: ship to wrap, two approved P1 deferrals (cycle 1, 2 open P1) @ 659d054
- Run: 5 tickets · 4 sessions · 1 review cycles · 6 deviations · 0 findings overturned · net code +0 · tests +0
- Seats: 0 Opus 5.5 · 2 Opus 5.5 · 3 GPT-6.1 Sol · 4 Opus 5.5
- Skills: workflow@b222ba534b11, checkup@a9b74b6e2ae5
- Why: checkup ended in a summary with no way to act on it, and a copied action had no tested path.

## 2026-10-23 · run-ratio-and-retire · check-run judges test growth once per run · GPT-6.1 Sol
- `check-run.py` errors when tests net exceed 1.5× code added across the whole run, checked once every ticket is done; `Ratio waived: run — <reason>` turns it into a warning. The per-ticket ratio is now a warning. `checkup` reports test growth next to code growth and points at `workflow improve` when tests outgrow code.
- Replaying the new gate over P1's 26 runs flags one (`live-run-guardrails`). Review cycle 1 found the gate skipped plans whose done status carries a note after the sha (6 such plans in work-repo); fixed with a red test first. Three P3s deferred.
- Commits: 577a33a b8c24ce 40f9e4f
- Review: ship as-is (cycle 2, 0 open) @ 52e7b3b
- Run: 3 tickets · 2 sessions · 2 review cycles · 2 deviations · 0 findings overturned · net code +16 · tests +1
- Seats: 0 Opus 5.5 · 2 Opus 5.5 · 3 GPT-6.1 Sol · 4 Opus 5.5
- Skills: workflow@e712b74ba5ce
- Why: 7 of 16 per-ticket ratio hits were false and absorbed by waivers while nothing judged growth at run level.

## 2026-10-22 · threat-model-review · briefs name trust boundaries and review runs a threat pass on each · GPT-6.1 Sol
- A brief that touches outside input, credentials, writes, shell or permissions gets an optional `## Trust boundaries` section. Review answers six fixed questions per boundary in a `Threats:` line, rated on the existing severity bar. A run with no trigger writes `Threats: none`.
- `check-run.py` needed no change; one test pins that the section is optional. A trial row sits in `SKILL-IMPACT.md`.
- Review found 3 P3s (completion line, `Threats:` line shape, unwrapped lines), all deferred.
- Commits: b4866b1 2460066
- Review: ship as-is (cycle 1, 0 open) @ 5e5abe1
- Run: 2 tickets · 1 sessions · 1 review cycles · 0 deviations · 0 findings overturned · net code +0 · tests +7
- Seats: 0 Sonnet 5.5 · 2 Opus 5.5 · 3 GPT-6.1 Sol · 4 Opus 5.5
- Skills: workflow@1da975d
- Why: review's only security check was one clause, so a run that added a trust boundary got no systematic question about it.

## 2026-10-22 · retire-date-gates · check-run applies one rule set to every run not yet done · GPT-6.1 Sol
- `check-run.py` no longer picks rules by `Created:` date: the four `*_SINCE` gates, `LEGACY_TEST_RATIO`, `deviated()` and the behaviour minimum are gone. Done runs keep header, sha and layout checks only; parked runs are checked like live ones, except a drafting brief.
- The docs that said "earlier plans keep their rules" now state the universal rules.
- Review cycle 1 found two P1s (done runs lost their sha walk, parked drafts failed section checks), both fixed with red tests first. Two P3s deferred.
- Commits: fc99027 281f4a9 fbb1fdc 2aac08b
- Review: ship as-is (cycle 2, 0 open) @ dbccc12
- Run: 2 tickets · 2 sessions · 2 review cycles · 3 deviations · 0 findings overturned · net code -9 · tests +59
- Seats: 0 Sonnet 5.5 · 2 Opus 5.5 · 3 GPT-6.1 Sol · 4 Opus 5.5
- Skills: workflow@416076a3ef59
- Why: a rule shipped today silently skipped today's runs, and the date gates confused the user.

## 2026-10-18 · guard-keys · writers and reviewers test every key a guard matches on · GPT-6.1 Sol
- The test, review and execute references now say: one case per guard key, a reviewer who finds one untested key lists and mutates all of them, and execute regains its acceptance-seam and scope wording. A trial row sits in `SKILL-IMPACT.md`.
- Review found 3 P3s (Verify greps one phrase per rule, rule placement, conditional reviewer trigger), all deferred.
- Commits: e478a17
- Review: ship as-is (cycle 1, 0 open) @ b98bb26
- Run: 1 tickets · 1 sessions · 1 review cycles · 0 deviations · 0 findings overturned
- Seats: 0 Sonnet 5.5 · 2 Opus 5.5 · 3 GPT-6.1 Sol · 4 Opus 5.5
- Skills: workflow@e478a17
- Why: three growth-ratchets findings were one untested guard key each, and the cap was met by unwrapping.

## 2026-10-18 · growth-ratchets · check-run counts tests net and honours only keyed waivers · GPT-6.1 Sol
- `check-run.py` compares net test growth with code additions, so rewrites and moves no longer trip the ratio. Only a keyed `Ratio waived: T#` or `Budget waived: T#` line with a reason skips its check, and the output repeats the numbers. Plans created before 2026-10-19 keep the old rules. `WORKLOG.md` moved to the repo root, so `check_worklog` finds the entries.
- Cycles 1 and 2 each found a P1 test gap (waiver ticket key, then waiver kind), both fixed by tests only.
- Commits: 1a65a10 9974505 ee191dc cfa48ca
- Review: ship as-is (cycle 3, 0 open) @ a9bb5fe
- Run: 2 tickets · 4 sessions · 3 review cycles · 0 deviations · 0 findings overturned
- Seats: 0 Sonnet 5.5 · 2 Opus 5.5 · 3 GPT-6.1 Sol · 4 Opus 5.5
- Skills: workflow@cfa48ca
- Why: the added-line test ratio flagged rewrites, and any mention of a waiver skipped the check.

## 2026-10-17 · lean-runs · workflow caps run size and test growth · GPT-6.1 Sol
- `check-run.py` errors on briefs over 8 behaviours, plans over 20 acceptance lines (unless a split
  was declined) and tickets whose tests exceed 1.5× code; warns on a high Budget with no `why:`.
  Runs created before 2026-10-18 keep the old rules. Docs now ask for one test per behaviour.
- Cycle 1 found one P1 (old-run lane gate untested), fixed in cycle 2.
- Commits: 3c64d1b c07710e 2b6835a e92cdbe
- Review: ship as-is (cycle 2, 0 open) @ 4a085e5
- Run: 3 tickets · 3 sessions · 2 review cycles · 1 deviations · 0 findings overturned
- Seats: 0 Opus 5.5 · 2 Opus 5.5 · 3 GPT-6.1 Sol · 4 Opus 5.5
- Skills: workflow@e92cdbe
- Why: workflow runs grew the test suite and took too many sessions.

## 2026-10-10 · run-sizing · workflow plans bigger tickets, runs 3 per session, caps review at two cycles · Opus 5.5
- `check-run.py` warns on a low median code Budget, allows 6 acceptance lines, and errors on an
  unapproved third review cycle; plan, execute, review, wrap and README rules and counts updated.
- Cycle 1 found two P1s (no six-line boundary test; wrap missed patch sessions), both fixed.
- Commits: 1d56b03 d3ce44c f3d885e 36b844d 69370a6
- Review: ship as-is (cycle 2, 0 open) @ 38dea5d
- Run: 3 tickets · 2 sessions · 2 review cycles · 2 deviations · 0 findings overturned
- Seats: 0 Sonnet 5.5 · 2 Opus 5.5 · 3 Opus 5.5 · 4 GPT-6
- Skills: workflow@2820722, checkup@2820722
- Why: fewer, larger tickets and fewer review cycles cut the cost per run.

## 2026-10-08 · slop-guards · workflow guards against bloated plans, tests and patches · Opus 5.5
- `check-run.py` gained Budget/Risk/Size/Retired checks (2× code overrun warns, tests over 3× code
  errors); plan, execute, review and wrap references now teach proportional tests and retiring
  obsolete code; two review findings (empty Risk crash, zero Budget) fixed in cycle 2.
- Commits: d5289bd b9381ca fbe43c1 d6280d0 6484bb8 6e8efc9 bc114fc dd167fe 0e888de
- Review: ship as-is (cycle 2, 0 open) @ 752ad6b
- Run: 12 tickets · 2 review cycles · 2 findings fixed
- Why: stop AI-slop growth (long plans, oversized tests, dead code) with mechanical checks.

## 2026-10-01 · docs refresh, MIT license, workflow v2.1.1 context budget · Sonnet 5.5
- READMEs brought in line with the real wiring (direct symlinks into both CLIs, `j-skills` plugin
  name, lowercase paths, memory pages); MIT `LICENSE` added; the roadmap emptied (no
  planned work).
- v2.1.1 cut per-run grounding cost: tiered reads, short `wrap.md` for done runs, `review.md`
  `## Resolved` table, one-line TODO intake, `TODO_ARCHIVE.md`/`ROADMAP_ARCHIVE.md` convention with
  size flags, `ROUTING.md` split into card rows and `ROUTING-NOTES.md`. Trialing (see `SKILL-IMPACT.md`).
- Commits: 04fee86 e6cd6a0 090536f

## 2026-09-30 · routing to GPT-6.1 Sol / Opus 5.5 / Sonnet 5.5; card and model-naming fixes · Opus 5.5
- `ROUTING.md` restricted to the four models in use and `medium`–`xhigh` effort; GPT-6.1 Sol runs every
  execute lane, Opus 5.5 plan and review, Sonnet 5.5 brainstorm and wrap. Plugin manifest renamed
  to `j-skills` (Codex shows `j-skills:workflow`).
- No closing card on turns that wait for an in-chat answer; the writer's model is read from the
  harness or config and recorded as the model name only.
- Commits: b057e73 a3dbc08 df073d6 6c8098a 676e751 c82ccf3

## 2026-09-30 · workflow v2.1 released · Opus 5.5
- Spec phase retired; brainstorm is a grill ending in a brief with behaviours and test seams; plan
  writes ≤8 tracer-bullet tickets with literal acceptance lines; operator tickets for live steps;
  review checks the outcome on the surface users reach. Amended after a history review of real runs.
- Commits: f2507d0
- Why: v2.02 runs showed severity bars that couldn't escalate outcome failures and no lane for live
  steps (an archived v2.1 review, since removed).

