# Patch cycle 1, tickets 4 and 5

Writer: GPT-6.1 Sol

## C1-T4

- Restored the write-after-reads rule in workflow/SKILL.md.
- Exact acceptance grep: 0 before, exit 1; 1 after, exit 0.
- Commit: fb9bf81.
- No mutation applies to this Markdown-only ticket.

## C1-T5

- Reused the existing no_verify scanner and parametrized NoVerify test; no new helper.
- Red commit: 5d4f0a8. The narrow-rule subtest expected one warning but got zero.
- Green commit: 1c09a05. NoVerify: Ran 1 test, OK, exit 0.
- Both wildcard command rules and the single broad wildcard rule still suppress the warning.
- Mutation: replaced the realistic probe command tuple with the two bare commands.
  NoVerify failed on the narrow rules, exit 1. Restored the fix afterward.
- Existing test assertions: 4 before, 4 after. The expected-warning cases now include the narrow rules.
  No assertion was removed or weakened; the new case is required by C1-T5.

## Full suites

Command at each gate:
`python3 -m unittest discover -s .github/skills/workflow/scripts/tests && python3 -m unittest discover -s .github/skills/checkup/scripts/tests`

- Baseline: Ran 122 tests in 55.395s, OK; Ran 9 tests in 0.869s, OK; exit 0.
- C1-T4: Ran 122 tests in 55.515s, OK; Ran 9 tests in 1.004s, OK; exit 0.
- C1-T5: Ran 122 tests in 55.592s, OK; Ran 9 tests in 0.987s, OK; exit 0.
- git diff --check: exit 0.

No screen changes. No trigger description changed. The existing git-hooks SKILL-IMPACT row covers this patch cycle.
