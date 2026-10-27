Command: workflow execute run-worktrees
Created: 2026-10-27
Base: b05095f
Inputs: .workflow/run-worktrees/patch_plan.md @ f445741
Status: complete

Writer: GPT-6.1 Sol. No product code changes in C1-T5.
Method: clone the local repo under /tmp, create a detached throwaway git worktree, copy the four new test methods, then change one guard at a time. Restore the script after each full-suite run. The unmodified baseline passed all 69 tests; every mutant ran all 69 and exited 1 with exactly one failing subcase. The temporary worktree was removed; the primary production script still matches HEAD.
Command: `python3 -m unittest discover -s <temporary-worktree>/.github/skills/workflow/scripts/tests`

KILLED all-to-any: mixed src.py and WORKLOG.md conflicts returned 4 instead of 3; test_Land_routes_mixed_and_text_only_conflicts.
KILLED drop-txt: a notes.txt-only conflict returned 3 instead of 4; test_Land_routes_mixed_and_text_only_conflicts.
KILLED todo-counts-as-started: an unstarted run A isolated B instead of leaving it on main; test_Open_keeps_primary_free_for_an_unstarted_run.
KILLED exclude-dedupe-disabled: opening distinct isolated B and C duplicated .worktrees/; test_Open_excludes_multiple_isolated_runs_once.
KILLED dirty-run-guard-disabled: landing a dirty run moved main; test_Land_refuses_dirty_or_wrong_branch_checkouts, dirty run.
KILLED primary-branch-guard-disabled: landing from feature returned 0 instead of 1; test_Land_refuses_dirty_or_wrong_branch_checkouts, primary branch.
KILLED run-branch-guard-disabled: landing a run checkout on feature returned 0 instead of 1; test_Land_refuses_dirty_or_wrong_branch_checkouts, run branch.

Raw logs and results: `/tmp/run-worktrees-c1-t5.v528esnq/`, seven mutation records in results.json.
results.json SHA256: b827fd75297f7c65988d19cd1b2509e00e8d81fa3e5ac920a344e2ca10c6f611
Existing tests: all 76 assertion calls remain unchanged; four parametrized test methods added, 51 lines. Reused RepoTests and LandTests.run_branch; no helper added.
