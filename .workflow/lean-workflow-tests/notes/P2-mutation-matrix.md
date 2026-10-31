P2 — Which tests are the only ones to catch some bug that line coverage cannot see?

- Tool: `scripts/mutation/`. `mutate.py` makes one-node bugs ("mutants": flipped comparisons, and/or, any/all, dropped `not`, int +1, bool flip, negated `if`) on lines P1 says a test reaches. It runs only those tests and records which test and subtest case fails. `analyse.py` lists mutants that only one test catches. `cover.py` finds the fewest tests or cases that keep every P1 line, branch arm and caught mutant.
- Rerun: `python3 mutate.py <scripts> /tmp/covmap <out>.json --only <script> --workers 4` per script, about 45 min for all three on 4 workers.
- Result @ aefd430: 665 mutants on reached lines. check-run.py 392 caught, 57 survive, 70 on unreached lines. next-step.py 95 caught, 10 survive. run-worktree.py 89 caught, 9 survive.
- 45 of 120 tests reach no unique line or branch arm and catch no unique mutant. A greedy cover keeps all coverage with 81 tests, or with 133 of the 274 cases spread over 86 tests.
- Limit: the mutants never change strings or the one float, `1.5`. So a case that only checks a message's wording, or the 1.5× limit exactly, looks redundant here. A first run missed kills by `subTest(msg)` cases. That was fixed by rerunning those 3 tests.

- T1 correction: the prototype omitted ROUTING.md in temporary copies. Its caught counts are superseded by receipts/mutants-base.txt; see receipts/t1-mutation-fixture.md.
