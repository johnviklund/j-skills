# T2 verification

Writer: GPT-6.1 Sol · high
Reuse: one new reference holds unattended rules; the hub and README point to it.
Skills read: agent-docs and plain. Invocation names and trigger description are unchanged.

Planned grep checks, from the repo root:
```sh
W=.github/skills/workflow; grep -c 'references/unattended.md' $W/SKILL.md; grep -rl '^## Always stop' $W; grep -c '^| ID | Phase | Question | Default | Status | Answer |$' $W/references/unattended.md; grep -c '^Mode:' $W/references/phase-0-brainstorm.md; grep -c 'Version 3.0.0' $W/README.md
```
Before: counts 0; no stop section; missing reference; 0; 0. Exit 1.
After: 1; .github/skills/workflow/references/unattended.md; 1; 1; 1. Exit 0.
Additional content checks pass: exactly five stop bullets; no Version 2.1; all changed relative
links resolve; the example table parses through the shared validator as D1 assumed.
The hub has 180 lines. Copilot's skill list reports workflow enabled.
Relative pointers and the words above, below, step N and this file were checked in changed docs.
The maintenance guide now names the same header exemptions as the checker and hub.
A SKILL-IMPACT row schedules evaluation on three unattended runs; live model trials remain future evidence.

Final baseline command and result:
```text
python3 -m unittest discover -s .github/skills/workflow/scripts/tests && python3 -m unittest discover -s .github/skills/checkup/scripts/tests
Ran 111 tests in 52.677s
OK
Ran 8 tests in 0.466s
OK
exit 0
```
Mutation: none; documentation ticket. Existing assertions changed: 0.
ROADMAP completion stays with wrap step 5, per plan F7.
