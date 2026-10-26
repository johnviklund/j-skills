Command: workflow review memory-patterns-and-budget
Created: 2026-10-26 · claude-opus-5-5
Base:    e4df252
Inputs:  .workflow/memory-patterns-and-budget/plan.md @ 2d3a44a
Status:  complete

## Coverage
- [x] T1 — acceptance 6/6: 10 Verify greps print 1 each (0 at 2d3a44a), 17,119 B ≤ 17,446, 94f353b holds SKILL.md + SKILL-IMPACT.md only, receipt present
- [x] T2 — acceptance 6/6: cost-test count 2, other 7 greps print 1 (0 at 2d3a44a), 27,400 B ≤ 27,720, 43588b3 holds SKILL.md + SKILL-IMPACT.md only, receipt present
- [x] B1–B3, B5, B6 delivered · B4 delivered, operating rules included since fec0e26 (C1-1) · out of scope untouched: no script, no README or skill cap, ~40-page ceiling and agent-docs unchanged
- [x] Outcome, manual, no verify skill (doc run): reviewer re-ran compact's new steps by hand on the 7 real `learnings.md` files and agrees with the T1 receipt: 0 new pages, retire-date-gates joins the guard-key entry, the grep pair has different fixes, slop-guards is one run. Desk check of the cost test finds C1-1
- [x] Installed copies: `~/.agents/skills/memory.{compact,remember}/SKILL.md` match the repo since the C1-T1 refresh (`diff -q` exit 0); in cycle 1 they lacked both rules
- [x] .workflow/ dependency check — 0 hits outside `.workflow/`
- [x] Mutations in a throwaway worktree: M1 "If no, route it" → "If yes" keeps T2 Verify at exit 0; M2 "leave its count alone" → "bump its count again" keeps T1 Verify at exit 0 (C1-2)
Size: +0 code · +0 tests · ratio n/a (doc run: +23 −1 lines of *.md) · net +0 · over 1,000: none
Reachability: no new files · the cost test is reached from step 2 (remember:182) · *Unpaged repeat* from step 3 and the summary line (compact:116, 196) · guards shown failing: every Verify grep prints 0 at 2d3a44a
Escape hatches: none · dependencies: none added · full suite: not run, receipt-rule diff 2d3a44a..HEAD is empty
Independence: cross-vendor — writer GPT-6.1 Sol (OpenAI), reviewer Claude Opus 5.5 (Anthropic), both cycles
Threats: none — the brief and the diff add no boundary; compact reads repo files it already read and writes only `memory.proposed/`

## Resolved
| Finding | Sev | Title | Disposition | Resolved |
|---|---|---|---|---|
| C1-1 | P1 | the cost test sends a low-value operating rule nowhere | fix now | @ fec0e26 (cycle 2) |
| C1-2 | P3 | doc Verify greps miss the words that decide each rule | defer, stays here; `[durable→memory]` in learnings.md | settled (cycle 2) |
| C1-3 | P3 | the page-bump rule sits inside a class defined as "no page yet" | defer, stays here | settled (cycle 2) |
| C1-4 | P3 | the trial judges cannot tell "never fired" from "broken" | defer, stays here | settled (cycle 2) |
| C1-5 | P3 | compact proposes `AGENTS.md` moves without the cost test | defer, stays here | settled (cycle 2) |

Cycle 1 also counted 1 unlisted P3: the T2 receipt, case 1, says no owner covers the live-run defect while `TODO.md:7` tracks it.

## Cycle 2 findings
Scope: the fix diff d0066ee..e4df252 (one added line, `memory.remember/SKILL.md:150`) and the C1-1 class.
- C1-1 re-verified. Item 2 now passes for a rule the cost test rejects, so the licence rule reaches a page. Items 3 and 4 still apply, as the receipt shows. A transferable principle still fails item 3 and goes to a skill.
- Class sweep: the admission test is defined once (`remember:127-143`). compact:117 reuses it for repeats and runs no cost test, so B2's "name `AGENTS.md` matches in the report" is unchanged. Wrap and retro reach `AGENTS.md` through remember. No other site has the gap.
- Fix commit fec0e26 holds `.github/skills/memory.remember/SKILL.md` only, +1 line, 27,506 B ≤ 27,720. No test files exist to touch. The patch Verify exits 0. Its grep phrase carries the deciding words, so C1-2's weakness does not repeat. Removing the sentence turns it red (0 at d0066ee).
- Installed copies: `diff -q` of both `~/.agents/skills/memory.{remember,compact}/SKILL.md` against the repo exits 0.
- Regressions: none. Receipt-rule diff d0066ee..HEAD is empty. Outside `.workflow/`, 0 lines reference it.

### P3 — C2-1 "What to Save" does not name a rule the cost test kept out of `AGENTS.md`
- Evidence: the list at `remember:240-250` names gotchas, preferences and open gaps, and `:257` still routes "stable operating rules" to `AGENTS.md`. A reader who starts there can miss the new home. The cost test's own "Before any addition" scope covers it, and the receipt reads the licence rule as an operating preference.
- Disposition: defer (stays in `review.md`), wording only
- Resolved: —

## Pre-existing / environmental
- Installed skill copies on this server were one change behind in cycle 1. C1-T1 ran `npx skills update -g` after its push, and both copies now match the repo.
- `workflow` live-run grep misses `Status:  complete` with two spaces, this run's brief included (`TODO.md:7`, P2, already deferred).

## Cycle 1 verdict
Patch cycle 1: fix C1-1 (P1) in one ticket, C1-T1. Four P3s stay in `review.md`. No human approval is owed.

## Cycle 2 verdict
Ship as-is. C1-1 is fixed at fec0e26 and no site of its class stays open. Cycle 2 adds one P3, C2-1, which stays in `review.md`. No open fix-now finding and no human approval owed.
