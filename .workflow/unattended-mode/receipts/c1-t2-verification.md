# C1-T2 verification

Writer: GPT-6.1 Sol · high
Reuse: add one assertion to the existing decision-state test. No new helper or test method.
The ready and awaiting-human ticket cases both assert that a waiting decision names decisions.md
in Reads. The assumed and answered cases retain their whole-result baseline comparisons.

Targeted command and result:
```text
python3 -m unittest discover -s .github/skills/workflow/scripts/tests -p test_next_step.py -k test_unattended_decision_states
Ran 1 test in 0.728s
OK
exit 0
```

Mutation: copy next-step.py, check-run.py and test_next_step.py to a temporary scripts directory.
Delete only `step["reads"].append(f".workflow/{slug}/decisions.md")` from that copy.
Run the targeted command there. It exits 1 with `FAILED (failures=2)`.
The first failure is the new assertion for the ready ticket:
```text
AssertionError: '.workflow/x/decisions.md' not found in ['.workflow/x/plan.md']
```
The second failure is fixture carry-over after the first failure skips cleanup, not an independent
mutation proof. The first failure kills the mutation. The temporary copy is removed.
The production next-step.py diff is empty.

Final required command and result:
```text
python3 -m unittest discover -s .github/skills/workflow/scripts/tests && python3 -m unittest discover -s .github/skills/checkup/scripts/tests
Ran 111 tests in 46.638s
OK
Ran 8 tests in 0.415s
OK
exit 0
```
Existing assertion changes: 0. Assertion calls in test_next_step.py: 75 before, 76 after.
No red commit. No deviation from the ticket.
