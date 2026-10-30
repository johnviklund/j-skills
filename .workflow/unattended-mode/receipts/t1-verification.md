# T1 verification

Writer: GPT-6.1 Sol · high
Reuse: moved the existing routing table parser into check-run.py; routing and decisions share it.
Existing test assertions changed: 0. The fixture helper can also return the subprocess result.

Baseline command and result:
```text
python3 -m unittest discover -s .github/skills/workflow/scripts/tests && python3 -m unittest discover -s .github/skills/checkup/scripts/tests
Ran 109 tests in 47.783s
OK
Ran 8 tests in 0.432s
OK
exit 0
```

Red: the two new parametrized tests failed in eight subcases before implementation.
They exposed rejected valid files, accepted invalid modes/statuses/rows, and ignored waiting decisions.

Green, same full-suite command:
```text
Ran 111 tests in 51.749s
OK
Ran 8 tests in 0.437s
OK
exit 0
```

Mutation checks ran on temporary script copies. Each change failed the new CLI tests:
- Invert the mode length guard, field guard, or rejection guard.
- Remove attended, then unattended, from accepted modes.
- Remove the decision artifact, its header exemption, or its validation entry.
- Invert status rejection; remove assumed, waiting, then answered from accepted statuses.
- Skip the decision file; invert waiting selection; take the last waiting row instead of the first.
Result: 15/15 mutations rejected. Production files restored unchanged.

Waiting D2 returns exactly `{"decision": "D2", "action": "Which port?"}`, nulls the model,
and renders `**Model:** human · Which port?`. It replaces an existing operator blocker.
Assumed and answered files return the entire baseline JSON unchanged.
Both modes accept the headerless table without warnings. Invalid mode, status and short row exit 1.
