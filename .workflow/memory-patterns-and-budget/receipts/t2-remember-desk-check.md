Command: workflow execute memory-patterns-and-budget · T2 desk check
Created: 2026-10-26 · GPT-6.1 Sol
Base: c9101fffd42ff5f7bc6e2f4fb4cc76e855c92309
Inputs: plan.md @ 2d3a44a
Status: complete

## Method and baseline
This is the approved writer's desk check, not a paid or independent agent trial.
Compare the old broad AGENTS.md classification with the new cost test for these three cases.
Baseline T2 Verify exits 1: all eight grep counts are 0 and the receipt is missing.
Reuse: the existing admission test selects memory pages; agent-docs defines Context load.
The new section refers to both instead of duplicating them. No code or helper is needed.
Scratch inputs and proposed outputs: /tmp/memory-patterns-and-budget-j5mwdz5i/remember/.

## Case 1: the live-run-finder rule
Candidate: workflow's live-run finder misses briefs with two spaces after Status:; allow whitespace when debugging a missing run.
Before: step 2 lists agent workflow boundaries and repeated gotchas as AGENTS.md material, with no typical-task test.
After: removing this narrow debugging instruction does not cause a mistake on a typical skill-editing task in this repo.
Result: routed to a memory page. The uncapped fixture has memory.proposed/live-run-finder.md with every page-shape field.
Admission passes: an open repo-specific gap, useful when debugging this finder, no existing owner covering the defect.
Its Fix names an exit check so it can leave memory when repaired. It gets no AGENTS.md pointer because none is needed.
The actual defect remains owned by the existing follow-up; this ticket changes no finder or TODO item.

## Case 2: installed skill refresh
Candidate: after pushing a skill edit, run npx skills update -g.
Removing this command causes a typical skill-editing task to leave the installed copies stale.
Result: kept in AGENTS.md in the fixture as a one-line command contract.
The explanation stays in README.md Change a skill; no duplicate memory page is created.
There is no stated cap in this fixture, so only the removal test runs and no default cap is invented.
This case is grounded in skills/workflow/MEMORY.md's disconnected-snapshot entry and README.md's update command.
The real j-skills repo has no AGENTS.md; no new contract file is created here.

## Case 3: stated line cap
Fixture AGENTS.md states Line cap: 40 and holds 37 lines, including its header and cap.
The file is 92.5% of the cap, inside its top 10%.
Result: names 1 line to move, line 12, For archived mockup screenshots, use the workflow screenshot settings.
Move it to workflow-reference.proposed.md before adding the retained update command.
Both the input and proposed AGENTS.md have 37 lines; the cap remains 40.
The old instructions have no reason to name or move the existing line; the new section requires both in the same pass.

## Limits
File assertions check the fixture line count and threshold arithmetic after manual classification.
They do not prove an independent agent follows the rule. Review should repeat one case.
No real AGENTS.md, memory page, installed skill or done run is changed.
Trigger/frontmatter wording is unchanged, so the approved desk checks cover this body-only edit.

## Green checks
T2 Verify exits 0. Cost-test heading/reference count is 2; the seven other counts are 1.
SKILL.md is 27,400 bytes, below 27,720. The skill commit 43588b3 contains only memory.remember/SKILL.md and SKILL-IMPACT.md.
