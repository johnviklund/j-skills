# Execution verification

Writer: GPT-6.1 Sol

| Check | Workflow suite | Checkup suite | Result |
|---|---|---|---|
| Baseline | 112 tests, 50.118s | 8 tests, 0.385s | both OK, exit 0 |
| T1 | 116 tests, 56.552s | 8 tests, 0.472s | both OK, exit 0 |
| T2 | 118 tests, 53.704s | 8 tests, 0.445s | both OK, exit 0 |
| T3 | 119 tests, 53.942s | 9 tests, 0.882s | both OK, exit 0 |

Commands: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests && python3 -m unittest discover -s .github/skills/checkup/scripts/tests`.
Every ticket's Verify command passed; content greps each returned 1.
Focused tests: T1 4, T2 2, T3 1 hook check and 1 settings check with 10 subcases.

T1: real commits reject invalid runs and allow warning-only runs and unrelated files.
Install is executable and idempotent; foreign configuration refuses without writing.
Fallback finds the repo skill link; missing copies list searched folders and allow commits.
Six mutations went red: configured hooks path, foreign marker, checker failure propagation,
workflow prefix, archive exclusion, missing-copy commit exit.

T2: real pushes reject a generated GitHub token and redact its value.
Clean new branches exclude remote history; branch deletion passes.
Missing scanner and missing script refuse the push.
Five mutations went red: scanner presence, deletion skip, remote-history exclusion,
redaction, missing-copy push exit.

T3: dry-run install writes nothing and reports missing or non-executable hooks.
Claude deny checks pass with both exact rules or the broad git rule.
Either rule missing warns once; no workflow folder suppresses the warning.
Five mutations went red: dry-run branch, executable check, workflow-folder check,
both-command requirement, Claude-only settings filter.
Two initially surviving mutations led to the executable and Copilot-setting cases.

Reuse: searched workflow scripts; no install, marker or skill-path helper existed.
No existing assertions changed. New-test fixture corrections are recorded in plan deviations.
Try it: no screen change; the real-git tests above prove the behaviour.
Skill trigger descriptions are unchanged; instruction changes are verified by ticket content greps.
