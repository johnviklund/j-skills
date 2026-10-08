Command: workflow review slop-guards
Created: 2026-10-08
Base:    5c8f68a5e673e5fbc493060d8283fbe5bd2fb868
Inputs:  plan.md @ 85b5b9e
Status:  complete

## Coverage
- [x] T1: 4/4 acceptance lines pass; its filter runs 5 tests because it also matches a T2 test.
- [x] T2: 4/4 acceptance lines pass; 4 tests.
- [x] T3: 4/4 acceptance lines pass; 3 tests and document counts 4, 1.
- [x] T4: 4/4 acceptance lines pass; 2 tests and document counts 4, 3.
- [x] T5: 4/4 acceptance lines pass; 3 tests and document counts 0, 2.
- [x] T6: 4/4 acceptance lines pass; counts 1, 176 lines, 3, 3; wording inspected against B11/B13.
- [x] T7: 4/4 acceptance lines pass; counts 7, 69 lines, 0, 2; wording inspected against B12.
- [x] T8: 4/4 acceptance lines pass; counts 1, 1, 1, 1; complete MIT notice present.
- [x] B1, B4–B5, B7–B15 delivered; out-of-scope work untouched.
- [ ] B2, B3, B6: nominal inputs pass; empty fields and zero budgets fail as recorded below.
- [ ] Outcome: observed through the CLI on temporary Git repositories; two guard failures remain. Manual, no verify skill.
- [x] Full suite: 16 tests pass. No pre-existing test assertions changed. No added escape hatches or same-run waste found.
- [x] Dependency scan: zero tracked non-receipt files outside run folders contain a literal run-folder path.
Size: +89 code · +186 tests · ratio 2.09 · net +272 · over 1,000: none
Reachability: unittest discovery loads the new test file; CLI dispatch reaches all new checks. Fixtures trigger B2–B10 diagnostics.
Mutation: `check-run.py:370`, `tests > TEST_RATIO * code` inverted to `<=`; the B4 test fails, 1/1, in a disposable Git worktree.
Independence: cross-vendor. All tickets name Anthropic Opus 5.5; reviewer is OpenAI.
Evidence: `receipts/c1-verification.md` contains commands, counts and reproductions.

## Cycle 1 findings

### P1 — C1-1: An empty Risk field crashes the checker
- Evidence: B6; `.github/skills/workflow/scripts/check-run.py:347` indexes `risk.split()[0]`. A gated operator ticket with `Risk:` produces `IndexError`, without a run summary.
- Remedy: treat an empty value as missing and emit the existing ticket warning before inspecting its class.
- Disposition: fix now
- Resolved: —

### P1 — C1-2: A zero Budget disables the overrun guard
- Evidence: B3; `.github/skills/workflow/scripts/check-run.py:367` tests budget truthiness. A done ticket with `Budget: code +0 · tests +0` and +101 code lines reports `0 errors · 0 warnings`.
- Remedy: distinguish a parsed zero from an absent budget; compare positive net additions against zero. An empty Budget also bypasses B2's missing-value warning.
- Disposition: fix now
- Resolved: —

## Pre-existing / environmental
- No root AGENTS.md, PRODUCT.md or DESIGN.md. Workflow MEMORY.md read.
- The installed skill predates this diff. Review also checks the repository's updated review instructions.
- The model picker is unavailable through this session's tools; no model switch was performed.
- CLI config names `gpt-6-astra`, effort `high`; no exact in-session model record is exposed. This differs from ROUTING.md's reviewer choices.
- The private reviewer exam set is absent from the documented sibling location. The repeat check covers MEMORY.md only.
- The existing plan is 131 lines against ~120. This is the checker's only warning before patching.
- These artifacts are dated 2026-10-08, before SLOP_SINCE. The new checks were exercised with 2026-10-09 fixtures.
- The writer's learnings were read during grounding before the updated blind-first instruction was loaded. This review does not claim blind-first independence.

## Cycle 1 verdict
Fix before wrap: 0 P0, 2 P1, 0 P2, 0 P3. Patch cycle 1 covers C1-1 and C1-2 with four tickets.
The existing suite and document checks pass, but the CLI still crashes or skips a promised warning on the reproduced inputs.
Consider `verify.create` for this CLI; no persistent verify skill exists.
