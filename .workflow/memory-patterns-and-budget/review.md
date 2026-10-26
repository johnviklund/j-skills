Command: workflow review memory-patterns-and-budget
Created: 2026-10-26 · claude-opus-5-5
Base:    d0066ee
Inputs:  .workflow/memory-patterns-and-budget/plan.md @ 2d3a44a
Status:  complete

## Coverage
- [x] T1 — acceptance 6/6: 10 Verify greps print 1 each (0 at 2d3a44a), 17,119 B ≤ 17,446, 94f353b holds SKILL.md + SKILL-IMPACT.md only, receipt present
- [x] T2 — acceptance 6/6: cost-test count 2, other 7 greps print 1 (0 at 2d3a44a), 27,400 B ≤ 27,720, 43588b3 holds SKILL.md + SKILL-IMPACT.md only, receipt present
- [x] B1–B3, B5, B6 delivered · B4 delivered for gotcha-shaped rules, not operating rules (C1-1) · out of scope untouched: no script, no README or skill cap, ~40-page ceiling and agent-docs unchanged
- [x] Outcome, manual, no verify skill (doc run): reviewer re-ran compact's new steps by hand on the 7 real `learnings.md` files and agrees with the T1 receipt: 0 new pages, retire-date-gates joins the guard-key entry, the grep pair has different fixes, slop-guards is one run. Desk check of the cost test finds C1-1
- [x] Installed copies: `~/.agents/skills/memory.{compact,remember}/SKILL.md` lack both rules (`grep -c` 0), so a pass on this server still runs the old text (see Pre-existing)
- [x] .workflow/ dependency check — 0 hits outside `.workflow/`
- [x] Mutations in a throwaway worktree: M1 "If no, route it" → "If yes" keeps T2 Verify at exit 0; M2 "leave its count alone" → "bump its count again" keeps T1 Verify at exit 0 (C1-2)
Size: +0 code · +0 tests · ratio n/a (doc run: +22 −1 lines of *.md) · net +0 · over 1,000: none
Reachability: no new files · the cost test is reached from step 2 (remember:182) · *Unpaged repeat* from step 3 and the summary line (compact:116, 196) · guards shown failing: every Verify grep prints 0 at 2d3a44a
Escape hatches: none · dependencies: none added · full suite: not run, receipt-rule diff 2d3a44a..HEAD is empty
Independence: cross-vendor — writer GPT-6.1 Sol (OpenAI), reviewer Claude Opus 5.5 (Anthropic)
Threats: none — the brief and the diff add no boundary; compact reads repo files it already read and writes only `memory.proposed/`

## Cycle 1 findings
### P1 — C1-1 the cost test sends a low-value operating rule nowhere
- Evidence: B4 says a rule that fails the cost test goes to a memory page or a skill reference. `memory.remember/SKILL.md:148-149` sends it to "a memory page that passes the admission test". Admission item 2 (`:133-135`) refuses any "operating rule / command contract (`AGENTS.md`)" and says "route it there". Step 2 (`:182`) sends exactly those rules to `AGENTS.md`, so they always fail item 2.
- Failing input: in j-skills, "when copying code from another repo, add its license to `THIRD-PARTY-NOTICES.md`". Copying code is not a typical task, so the cost test says no. No skill owns the rule, and item 2 refuses the page. The text leaves two outcomes: keep it in `AGENTS.md`, which defeats B4, or drop it by `:141-143`, which breaks D2.
- Why the receipt passed: T2 case 1 recast its rule as an open gap (item 3), so item 2 never fired.
- Disposition: fix now — patch ticket C1-T1, one sentence in the cost test
- Resolved: —

### P3 — C1-2 doc Verify greps miss the words that decide each rule
- Evidence: M1 and M2 in Coverage stay green. The shipped words are correct, read at `memory.remember/SKILL.md:148` and `memory.compact/SKILL.md:120`. Second occurrence of guard-keys P3-1, recorded in the guard-key entry of `skills/workflow/MEMORY.md`; no plan reference carries that lesson yet.
- Why P3: a doc grep runs once and guards no later reader, as guard-keys P3-1 ruled. The repeat is the useful signal.
- Disposition: defer (stays in `review.md`); `[durable→memory]` line in `learnings.md`
- Resolved: —

### P3 — C1-3 the page-bump rule sits inside a class defined as "no page yet"
- Evidence: decision 1a's sentences (compact:120-121) sit in the *Unpaged repeat* bullet, which opens "with no page yet", inside step 3's per-page list. The one live case, retire-date-gates, matches an existing page from one run, so a literal reader can skip it.
- Disposition: defer (stays in `review.md`) — wording only; the writer's dry run applied it correctly
- Resolved: —

### P3 — C1-4 the trial judges cannot tell "never fired" from "broken"
- Evidence: SKILL-IMPACT.md rows 13-14 pass only on a positive event. Real data has 0 repeats (F4) and j-skills has no `AGENTS.md` (F8), so 3 quiet runs prove nothing either way. The brief fixed these judges (B6).
- Disposition: defer (stays in `review.md`) — checkup can read "no input" as inconclusive
- Resolved: —

### P3 — C1-5 compact proposes `AGENTS.md` moves without the cost test
- Evidence: compact:152-155 (*Doctrine-misfiled*) and :220 (*Promotion candidates for `AGENTS.md`*) propose additions with no cost check. Wrap (`wrap.md:60`) and retro (`retro/SKILL.md:126`) go through remember, so this is the one path left. The brief scoped only remember.
- Disposition: defer (stays in `review.md`)
- Resolved: —

1 more P3 not listed: the T2 receipt, case 1, says no owner covers the live-run defect while `TODO.md:7` tracks it.

## Pre-existing / environmental
- Installed skill copies on this server are one change behind: `npx skills update -g` was not run after the T1/T2 push. C1-T1 runs it after its own push, so the fix lands with them.
- `workflow` live-run grep misses `Status:  complete` with two spaces, this run's brief included (`TODO.md:7`, P2, already deferred).

## Cycle 1 verdict
Patch cycle 1: fix C1-1 (P1) in one ticket, C1-T1. Four P3s stay in `review.md`. No human approval is owed.
