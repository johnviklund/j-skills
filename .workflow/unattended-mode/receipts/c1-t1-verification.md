# C1-T1 verification

Writer: GPT-6.1 Sol · high
Reuse: the existing Always stop UI bullet owns the approval rule. No new helper or section.
Skills read: agent-docs and plain. Invocation names and trigger description are unchanged.
The existing SKILL-IMPACT row now includes the UI-stop rule.

Planned content command, from the repo root:
```sh
U=.github/skills/workflow/references/unattended.md; grep -c "the ticket's code stays uncommitted" $U; grep -c "not the human's edits" $U; awk '/^## Always stop/{f=1;next} /^## /{f=0} f&&/^- /' $U | wc -l
```
Before: 0 · 0 · 5. Both grep checks exit 1.
After: 1 · 1 · 5. All three checks exit 0.
The replacement matches the patch plan exactly. Its relative phase reference resolves.

Baseline command and result:
```text
python3 -m unittest discover -s .github/skills/workflow/scripts/tests && python3 -m unittest discover -s .github/skills/checkup/scripts/tests
Ran 111 tests in 54.988s
OK
Ran 8 tests in 0.416s
OK
exit 0
```

Final result from the same command:
```text
Ran 111 tests in 46.861s
OK
Ran 8 tests in 0.394s
OK
exit 0
```
Mutation: none; documentation ticket. Existing assertions changed: 0.
Noticed: the skill change also updates its existing SKILL-IMPACT row.
