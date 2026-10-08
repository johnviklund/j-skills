Command: workflow review slop-guards
Created: 2026-10-08
Base:    5c8f68a5e673e5fbc493060d8283fbe5bd2fb868
Inputs:  review.md @ 5c8f68a5e673e5fbc493060d8283fbe5bd2fb868
Status:  complete

## Findings
- C1-1: empty Risk crashes `check_risk()` at check-run.py:347. Its dispatcher at :307 covers plan.md and patch_plan.md.
- C1-2: empty Budget passes the presence check at :305; valid zero totals bypass the comparison at :367.
- Reuse: `field()` already returns stripped values; `plan()`, `check()` and `lines()` provide fixture construction and CLI execution.
- Scope: change these field checks only. Preserve the date gate, deviations, receipt exclusions, ratio floor and supported risk classes.

Size: check-run.py 649 lines · tests 186 lines · over 1,000: none
Decisions: both P1 findings are fix now under the review rule; each reproducing test is committed before its fix.

## Execution state
- Next: review (all C1 tickets done). Re-review both field checks and their dispatcher paths.
- C1-T1 @ 6e8efc9
- C1-T2 @ bc114fc
- C1-T3 @ dd167fe
- C1-T4 @ 0e888de
- writer: Opus 5.5 (routed GPT-6.1 Sol not used; same writer vendor as T1–T8, so the OpenAI review stays cross-vendor)
- Baseline: 16 tests OK. 17 OK after C1-T2; after C1-T3, 17 OK + 3 red; after C1-T4, 20 OK.
- Uncommitted: none · Pending decision: none

## Tickets

### C1-T1 — Reproduce empty Risk without changing the checker
Delivers: B6 · Blocked by: none · Lane: logic · Budget: code +0 · tests +25
Seam: CLI output from temporary repositories using the existing fixture helpers
- [x] Gated plan.md and patch_plan.md operator tickets with empty Risk expect `T3: operator ticket has no Risk:`; parametrized cases fail on today's traceback.
- [x] The existing 16 tests remain green before the test-only commit.
Verify: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests -k risk_empty` (pre: no matching tests; receipt reproduces IndexError)
Skills: none · Status: done @ 6e8efc9
Writer: Opus 5.5

### C1-T2 — Warn when Risk is empty
Delivers: B6 · Blocked by: C1-T1 · Lane: logic · Budget: code +5 · tests +0
Seam: check_tickets dispatch to check_risk for plan.md and patch_plan.md
- [x] C1-T1's empty Risk cases print the warning and a normal run summary, without a traceback.
- [x] The full suite passes; the commit changes no test file.
Verify: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests -v` (pre: C1-T1 cases fail; original 16 pass)
Skills: none · Status: done @ bc114fc
Writer: Opus 5.5

### C1-T3 — Reproduce zero and empty Budget handling
Delivers: B2, B3 · Blocked by: C1-T2 · Lane: logic · Budget: code +0 · tests +35
Seam: gated plan.md fixtures, ticket commits and CLI output
- [x] A zero budget with +101 code lines expects `T1: net +101 lines, over 2× budget +0`; the new assertion fails.
- [x] Empty Budget on logic and contract tickets expects `T2: no Budget:`; parametrized cases fail before the fix.
- [x] A zero budget with only receipt additions prints `0 errors · 0 warnings`.
Verify: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests -k budget_values` (pre: no matching tests; receipt shows zero warnings for both failing inputs)
Skills: none · Status: done @ dd167fe
Writer: Opus 5.5

### C1-T4 — Enforce zero budgets and warn on empty ones
Delivers: B2, B3 · Blocked by: C1-T3 · Lane: logic · Budget: code +12 · tests +0
Seam: Budget presence check and check_overrun numeric comparison
- [x] Every C1-T3 case passes, including logic and contract presence checks and receipt exclusion.
- [x] The full suite passes, including date-gate and deviation cases; the commit changes no test file.
Verify: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests -v` (pre: C1-T3 zero-budget and empty-budget assertions fail)
Skills: none · Status: done @ 0e888de
Writer: Opus 5.5

## Coverage
C1-1 → C1-T1, C1-T2. C1-2 → C1-T3, C1-T4. Re-review both field checks and their dispatcher paths after all four commits.

## Risks
Zero is a valid budget. Missing budget information must not become a numeric zero accidentally. Existing warnings and gate behavior remain the regression bar.
