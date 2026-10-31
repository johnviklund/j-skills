P1 — Which tests reach script lines or branches that no other test reaches?

- Tool: `scripts/covmap/`. `sitecustomize.py` records `sys.monitoring` LINE and BRANCH events in every Python process the suite starts. `run.py` tags each test and subtest. `analyse.py` prints totals, how many items each test alone reaches, and the tests whose coverage sits wholly inside one other test's.
- Rerun: `python3 run.py <scripts/tests> /tmp/covmap && python3 analyse.py /tmp/covmap [--subtests]`
- Result @ aefd430: the suite reaches check-run.py 630 lines · 673 branch arms, next-step.py 204 · 229, run-worktree.py 188 · 170.
- 55 of 120 tests reach no line or branch arm that another test misses, and 29 of those sit wholly inside a single other test.
- Limit: a test can reach the same lines and still assert something new (an exit code, a message). P2 checks for that.
