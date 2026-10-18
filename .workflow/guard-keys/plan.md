Command: workflow plan guard-keys
Created: 2026-10-18
Base:    bbf2d45
Inputs:  .workflow/guard-keys/brainstorm.md @ 29c49c7
Status:  complete

Docs read: none in scope (j-skills has no PRODUCT.md or DESIGN.md)
Size: code 0 · tests 0 · ratio n/a (doc-only run; every touched file is `*.md`, a receipt by rule) · docs touched: phase-4-review.md 170, phase-3-execute.md 137, tests.md 87, SKILL-IMPACT.md 50 · over 1,000: none
Decisions: 1a — one ticket approved as listed, with the 100-character line limit (2026-10-18)

## Execution state
Current: T1 done; all tickets complete; next review
T1 @ e478a17
writer: GPT-6.1 Sol
Session 1: T1
Baseline: human chose 1a, T1 content checks and `check-run.py --all`; 0 errors.
Existing warning: archived slop-guards plan has 127 lines against ~120.
Verification: receipts/t1-verification.md
Uncommitted files: none after this record is committed; pending decision: none.

## Findings
| # | What is true | What it changes |
|---|---|---|
| F1 | The files live under `.github/skills/workflow/`; `skills/workflow` is a symlink to it. The installed copy `~/.agents/skills/workflow` is older than the repo and differs in all three references. | Edit the repo copy only. Wrap runs `npx skills update -g`. |
| F2 | Reuse: `tests.md:39-40` already says "A guard that requires several lines gets one case per line missing alone", inside the deny-list paragraph. | B1 extends that sentence to keys. No new paragraph. |
| F3 | Reuse: `phase-4-review.md:46-50`, the "Verify the verification" bullet, holds the reviewer's one mutation. Reachability (`:44-45`) already says "every new guard or check is shown failing once". | B2 goes into the Verify-the-verification bullet. |
| F4 | `phase-3-execute.md:92-97` is the trimmed paragraph. Its lost wording is in `9974505^`: "Build what its acceptance lines describe, at its seam" and "a nearby bug, a tempting refactor, a missing feature — is one line under `## Deviations` and the ticket continues". | T1 restores those phrases word for word. |
| F5 | B4's text today, `phase-3-execute.md:95-96`: "For plans created from 2026-10-19", "`Ratio waived: T# — <reason>`", "`Budget waived: T# — <reason>`" (1 each). | Each phrase must stay on one line so `grep` still finds it. |
| F6 | C1-2 met its line cap by unwrapping: `phase-3-execute.md:92` is 157 characters. The three files wrap at about 100. A line count alone can be met the same way again (`MEMORY.md`, guard-key entry). | B5 also requires every added line to be ≤ 100 characters. |
| F7 | `check-run.py` excludes `*.md` from ticket-commit budgets (`check-run.py:407`). `--all` today: 0 errors, exit 0. | Budget below counts doc lines; only `--all` and the net-line count enforce size. |
| F8 | `SKILL-IMPACT.md` rows are `\| Date \| Skill \| Change \| From \| Trial until \| Outcome \|`, newest first, with no guard-keys row today. | B6 adds one row at the top of the table. |

## Tickets

### T1 — writer and reviewer get the guard-key rule; execute regains its lost wording
Delivers: B1, B2, B3, B4, B5, B6 · Blocked by: none · Lane: mechanical
Budget: code +7 · tests +0
Seam: the three reference files and `SKILL-IMPACT.md`, read by `grep`, `git diff` and `check-run.py --all`
Accept:
- [x] `grep -c 'one case per key'` in `references/tests.md` → 1, in the sentence about guards that require several lines (B1)
- [x] `grep -c` in `references/phase-4-review.md` for `every key the guard matches on` → 1 and for `mutate each` → 1 (B2)
- [x] `grep -c` in `references/phase-3-execute.md` for `Build what its acceptance lines describe`, `a nearby bug, a tempting refactor, a missing feature`, `the ticket continues` → 1 each (B3)
- [x] `grep -c` in `references/phase-3-execute.md` for `Ratio waived: T# — <reason>`, `Budget waived: T# — <reason>`, `plans created from 2026-10-19` → 1 each (B4)
- [x] the three references since bbf2d45 → net ≤ +6 lines, 0 added lines over 100 characters; `check-run.py --all` → exit 0 (B5)
- [x] `SKILL-IMPACT.md` → 1 row matching `guard-keys`, then `cycle 2` in its judge, ending `| trialing |` (B6)
Verify: `W=.github/skills/workflow; R=$W/references; grep -c 'one case per key' $R/tests.md; grep -c 'every key the guard matches on' $R/phase-4-review.md; grep -c 'mutate each' $R/phase-4-review.md; for p in 'Build what its acceptance lines describe' 'a nearby bug, a tempting refactor, a missing feature' 'the ticket continues' 'Ratio waived: T# — <reason>' 'Budget waived: T# — <reason>' 'plans created from 2026-10-19'; do grep -c -- "$p" $R/phase-3-execute.md; done; git diff --numstat bbf2d45 -- $R/tests.md $R/phase-3-execute.md $R/phase-4-review.md | awk '{n+=$1-$2} END {print "net", n+0}'; git diff -U0 bbf2d45 -- $R/tests.md $R/phase-3-execute.md $R/phase-4-review.md | grep '^+[^+]' | awk 'length>101' | wc -l; grep -c '^| .*guard-keys.*cycle 2.*| trialing |$' $W/SKILL-IMPACT.md; python3 $W/scripts/check-run.py --all >/dev/null; echo "exit $?"` (pre: 0 · 0 · 0 · 0 · 0 · 0 · 1 · 1 · 1 · net 0 · 0 · 0 · exit 0)
Skills: .github/skills/agent-docs/SKILL.md
Status: done @ e478a17
Writer: GPT-6.1 Sol

## Coverage
- Outcome → T1: the three references carry the rule and the restored wording within +6 net lines; the trial row is logged
- B1 → T1 · B2 → T1 · B3 → T1 · B4 → T1 · B5 → T1 · B6 → T1
- Out of scope: a guard-and-key parser in `check-run.py` → untouched · waiver code and its tests → untouched · `WORKLOG.md`, `ROUTING.md`, plan and wrap references → untouched

## Risks
- The +6 cap is tight for three additions plus restored wording; F6's width line stops it being met by unwrapping, so the executor may need to cut a word elsewhere in the same paragraph.
- Rewrapping `phase-3-execute.md:92-97` could split a B4 phrase across lines; the B4 greps catch that.
- Option not taken: two tickets (rule, then restore). Both are doc edits with one Verify, and either alone is under 40 lines.

## TODO impacts
- growth-ratchets C1-2 review deferral → completed by T1; wrap drops it from `TODO.md` (D3).
- `.github/skills/workflow/MEMORY.md` guard-key entry → stays; wrap marks it promoted (D4).

## Product doc impacts
- `ROADMAP.md` (workflow skill) → no changes. No `PRODUCT.md` or `DESIGN.md` in this repo.
