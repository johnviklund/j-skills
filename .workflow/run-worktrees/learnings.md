Command: workflow review run-worktrees
Created: 2026-10-27
Base:    f445741
Inputs:  .workflow/run-worktrees/review.md @ f445741
Status:  complete

- [durable→memory] A new guard shipped with no test that fails when it is removed (C1-4: 7 mutations of `run-worktree.py` guards survived 61 green tests). The exam set already holds this class twice (`missed-assistant-privacy-guard-has-no-test`, `missed-retirement-flips-positive-filter-tests`). Each guard key needs a test that goes red when that key is mutated, and a repeated call (a second `open`) has to actually reach the code it claims to test.
- [durable→memory] A script that pushes a shared branch must not push commits it did not scan (C1-1). `land` pushed `main` including another run's unpushed commits; the scan covered only the run branch. When code pushes for a run, it scans or refuses the full outgoing range of the branch it pushes.
- [durable→eval] code-review — C2-1: swapping a hand-rolled section regex for the shared `Doc` parser (C1-T2) also changed where the section ends (`## ` only, no longer `# `), so shell fences from a later top-level section run as setup. Missed by the writer, and by the cycle 1 patch plan that prescribed the swap; caught in cycle 2. When a fix reuses a helper, check that the helper's boundaries match the code it replaces.
