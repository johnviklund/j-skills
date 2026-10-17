Command: workflow review lean-runs
Created: 2026-10-17
Base:    aafea80
Inputs:  .workflow/lean-runs/plan.md @ b675349
Status:  complete

## Coverage
- [x] T1 — acceptance 5/5 tested and passing (`LimitTests`, 2 tests, 8 subtests)
- [ ] T2 — acceptance 4/4 pass, but the B5 line's values cannot see the lane gate (C1-1)
- [x] T3 — acceptance 5/5 by content: stale-number count 0, net −2 doc lines (`receipts/t3-net-lines.txt`)
- [x] B1–B4, B6–B8 delivered · B5 delivered, test gap C1-1 · Outcome observed on check-run output over real cx-intelligence runs, manual (CLI, no user screen) · out of scope untouched
- [x] .workflow/ dependency check: 0 hits · escape-hatch scan: 0 hits · full suite 38/38 pass
Size: +31 code · +62 tests · ratio 2.00 · net +88 · over 1,000: none (check-run.py 746)
Reachability: no new file, export or function · guards shown failing: B1–B4 red in T1/T2 receipts; review mutations M1, M3, M4, M5 red, M2 green (C1-1)
Independence: cross-vendor (writer GPT-6.1 Sol, OpenAI · reviewer Claude Opus 5.5, Anthropic)
Blind first: partial. plan.md's one `## Deviations` line was read with the tickets, since they share a file.

Outcome evidence:
- B5 on real data: old (b675349) and new check-run print the same summary on all 29 cx-intelligence runs.
- Forward: with `Created:` moved to 2026-10-18 in a /tmp copy, workspace-topic-ownership errors at 11 behaviours and 25 acceptance lines; 19 ticket commits across 9 runs error at 1.5×.

## Cycle 1 findings
### P1 — C1-1 The lane gate for old runs survives mutation
- Evidence: B5, T2 line 4. Dropping `if lean else ("logic",)` at `check-run.py:414` leaves 38/38 green (M2, throwaway worktree). The B5 case uses tests +76 over code +50, and the legacy 3× ratio already passes that, so the case cannot tell whether contract is gated.
- Failing input under M2: a contract ticket, plan created 2026-10-16, code +50, tests +151. It errors although B5 says older runs keep their rules.
- Remedy: add that case to `test_committed_test_ratio`, `test_check_run.py:131`. Test only, no code change.
- Disposition: fix now
- Resolved: —

### P3 — C1-2 Two predicates repeat
- Evidence: the `Split declined by human:` scan is at `check-run.py:214-215` and `:484-485`. The acceptance-line regex at `:483` repeats `:311`, so a format change there leaves the run total behind.
- Remedy: a `declined(doc)` helper with two callers, and `t["accepts"]` saved at `:311`.
- Disposition: defer — P3, stays in review.md

### P3 — C1-3 A list-item refusal is not read
- Evidence: `re.match` at `:215` and `:484` needs the line to start with `Split declined`, so `- Split declined by human: …` still errors. It fails loudly, not silently.
- Disposition: defer — P3, stays in review.md

### P3 — C1-4 The Budget check reads one order only
- Evidence: `check-run.py:365` matches only `code +N · tests +N`. A Budget written `tests +N · code +N` is never checked for a reason.
- Disposition: defer — P3, stays in review.md

## Pre-existing / environmental
- The Codex copy `~/.agents/skills/workflow/scripts/check-run.py` has 0 `LEAN_SINCE` hits; the Claude link has the change. A Codex executor on the next cx-intelligence run gets the old checks until `npx skills update -g` runs after push.
- `scripts/tests/__pycache__/` is untracked, as at plan time.

## Cycle 1 verdict
Fix one P1, then re-review. C1-1 is a missing test case: the code is right today, but nothing stops a later edit from making old contract tickets error. Three P3s stay here. No P0 and no P2.
