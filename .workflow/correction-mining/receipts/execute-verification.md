# Execute verification

Writer: GPT-6.1 Sol · high

T1 · Claude interrupts become a repeat report · Commit: 00623b1
Changed: Reports repeated interrupts and the first human redirect, filtered by repository and age.
Proof: ClaudeTests ran 5 tests, OK; live 30-day repeat matched 2 sessions and 3 times.
Mutation: 16 individual parser mutations went red; unchanged control passed 5 tests.
Try it: Run corrections.py from the repository; no screen changes.
Noticed: none. Reuse search found config-scan's home overrides and subprocess fixtures; no transcript reader.

T2 · Denials and the other two stores · Commit: a5cd7fc
Changed: Reads Claude denials, Codex interrupts, and human Copilot denials; skips subagents and unattended denials.
Proof: StoreTests ran 3 tests, OK; both required suites passed on the final code.
Mutation: 11 individual mutations went red; unchanged control passed 3 tests.
Try it: Run corrections.py; synthetic transcripts prove denial handling without publishing private text.
Noticed: code net +71 exceeds +65 budget; waiver recorded in plan. No existing assertions changed.

Command: python3 -m unittest discover -s .github/skills/workflow/scripts/tests && python3 -m unittest discover -s .github/skills/checkup/scripts/tests
Result: workflow Ran 126 tests in 54.746s, OK; checkup Ran 33 tests in 7.002s, OK; exit 0.

T1 mutations: sidechain, assistant type, tool-use type, isMeta, interrupt prefix, command turn,
pending reset, tool reset, modification time, days override, all-repos, cwd filter,
sibling exclusion, worktree inclusion, repeat session threshold, truncation.
T2 mutations: denial prefix, inline reason, command head, Bash key, subagent exclusion,
abort reason, event type, redirect consumption, permission result, unattended source, request join.
Two surviving T2 mutations prompted additional near-miss and second-user-turn fixtures; rerun caught both.

Live report: stores claude 129 files, codex 121 files, copilot 0 files.
Live repeat: interrupt · no tool · 2 sessions · 3 times.
No redirect text or transcript paths are retained in this receipt.

T3 remains todo. Workflow requires a reset when the next ticket changes effort, from high to medium.
