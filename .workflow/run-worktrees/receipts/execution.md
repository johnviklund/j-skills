Command: workflow execute run-worktrees
Created: 2026-10-27
Base: c626d11
Inputs: .workflow/run-worktrees/plan.md @ 743eb2e
Status: drafting

## T1
Writer: GPT-6.1 Sol
Commit: 81aa880
Reuse: searched workflow scripts; reused Doc, parse_tickets, field and git_out. Extracted primary_branch for both callers.
Red: all six Open/Where tests failed before the command existed.
Verify: Open/Where passed 6 tests; full suite passed 55 tests.
Mutation: inverted the busy decision; Open_isolates failed because it printed a dot. Restored afterward.
Checks: git diff --check passed. Existing test assertions unchanged.
