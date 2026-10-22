Command: workflow review threat-model-review
Created: 2026-10-22 · Claude Opus 5.5
Base:    0abe05e
Inputs:  .workflow/threat-model-review/plan.md @ 4486102
Status: complete

Reviewed against the repo reference `.github/skills/workflow/references/phase-4-review.md` @ 0abe05e (the installed copy predates T2).

## Coverage
- [x] T1 — acceptance 5/5: suite 51 pass; greps = 1/1/1 (`phase-0-brainstorm.md:149-151`, template `:184`); 13,747 B ≤ 13,994; new test `test_check_run.py:101`
- [x] T2 — acceptance 6/6: trigger string, six questions, `Threats: none` line, `a trigger the brief does not list` each 1 (`phase-4-review.md:44-48, 103`); severity rows 4; SKILL-IMPACT.md:13 row; README.md:66; 13,729 B ≤ 13,953
- [x] B1…B6 delivered · Outcome observed on the reference docs (brief template + review Coverage template) by reading, no verify skill (doc-only repo, no user surface) · out of scope untouched: `phase-2-plan.md`, `check-run.py`, `TODO.md` diff empty; no new command
- [x] B6 extra probe: section placed where the template puts it (after `## Test seams`) → `0 errors · 0 warnings`
- [x] .workflow/ dependency check — 0 hits outside `.workflow/`
- [x] Escape-hatch scan — 0 hits · New dependencies — none
- [x] Verify the verification: in a throwaway worktree, adding `"Trust boundaries"` to `BRIEF_SECTIONS` (check-run.py:66) → `test_brief_trust_boundaries_are_optional` FAILS (1 failure). Worktree removed.
- [x] Existing tests: assertions removed 0 (diff to test file is +7/-0)
Size: +0 code · +7 tests · ratio n/a (doc run) · net +26 · over 1,000: none
Reachability: none new (the new test is collected by `unittest discover`) · guards shown failing: B6 test (mutation above)
Independence: cross-vendor (writer GPT-6.1 Sol, reviewer Claude Opus 5.5)
Threats: none — the brief and the diff add no boundary (Markdown and one unit test; no input, credential, write, shell or permission path added)

## Cycle 1 findings
### P3 — §4's completion line does not include the boundaries
- Evidence: `phase-0-brainstorm.md:153` — "the human confirms the outcome, behaviours and seams"; the new `Trust boundaries` bullet (`:149`) sits in the same final round, but nothing asks the human to confirm it.
- Disposition: defer (stays here)
- Resolved: —

### P3 — No line shape for a boundary's `Threats:` entry
- Evidence: `phase-4-review.md:45-46` asks for one `Threats:` line per boundary that answers six questions, but the template (`:103`) shows only the `none` form. Reviewers may write it in different shapes, which makes the B5 trial harder to judge.
- Disposition: defer (stays here)
- Resolved: —

### P3 — Unwrapped lines in both references
- Evidence: `phase-0-brainstorm.md:149`, `phase-4-review.md:44,46` run to ~150 chars; surrounding text wraps at ~100.
- Disposition: defer (stays here)
- Resolved: —

## Pre-existing / environmental
- `f3b2581` (root `README.md`, +4) landed between the plan and T1. It is not a ticket commit and is unrelated to this run, so it was not reviewed here.
- The installed workflow copy (`~/.agents/skills/workflow`) has neither change until `npx skills update -g` runs after push (plan Risks).

## Cycle 1 verdict
Ship as-is. P0 0 · P1 0 · P2 0 · P3 3 (deferred, stay in review.md). Every acceptance line is tested and passing, the B6 test catches its mutation, and out of scope is untouched.
