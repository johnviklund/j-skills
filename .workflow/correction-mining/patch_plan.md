Command: workflow review correction-mining · patch cycle 1
Created: 2026-11-01 · Claude Opus 5.5
Base:    1806a43
Inputs:  .workflow/correction-mining/review.md @ 1806a43
Status:  complete

Three tickets for cycle 1. C1-T1 is a bug fix: a red test commit first, then the fix. C1-T2 and C1-T3 change tests only: the code is correct, so they have no red commit.

## Execution state
Current: all patch tickets done; ready for review; no pending decision.
C1-T1 @ 9911caa
C1-T2 @ c3a6606
C1-T3 @ f7c04bf
writer: GPT-6.1 Sol
Baseline reused: review at 1806a43, workflow 126 OK; checkup 33 OK; only review records changed.
C1-T1 full suite: workflow 126 OK; checkup 34 OK; exit 0.
Red test commit: eecbc49, both cases fail with No closing quotation.
Mutation: remove fallback → red in isolated worktree; control 9 tests OK.
C1-T2: workflow 126 OK; checkup 36 OK; 6/6 mutants red; control 11 tests OK.
C1-T3: workflow 126 OK; checkup 39 OK; 7/7 mutants red; control 14 tests OK.
Receipt: receipts/cycle-1-verification.md. No code or test changes remain uncommitted.

## Tickets

### C1-T1 — A quote-unbalanced command still gets a key
Delivers: B2 · Blocked by: none · Lane: logic
Fixes: C1-1 (P1)
Budget: code +3 · tests +8
Seam: `corrections.py` as a subprocess on a Claude fixture, like `test_StoreTests_denials`
Change: in `command_head` (`corrections.py:38-43`), catch `ValueError` from `shlex.split` and fall back to `command.split()`. Site search: `shlex.split` at `:39` is the only call that parses free text with a grammar; `json.loads` at `:18` already catches `ValueError`.
Accept:
- [x] A denied Bash `cat > f <<'EOF'\nit's fine\nEOF` → exit 0, `denial · Bash · cat` counted (C1-1)
- [x] A denied Bash `echo don't` → exit 0, `denial · Bash · echo` counted (C1-1)
- [x] Red: the test commit alone fails with `No closing quotation` on stderr; the fix commit touches no test file (C1-1)
Verify: `python3 -m unittest discover -s .github/skills/checkup/scripts/tests -p test_corrections.py -k StoreTests` (pre: red test exits 1)
Skills: .github/skills/workflow/references/tests.md
Status: done @ 9911caa
Writer: GPT-6.1 Sol

### C1-T2 — Kill the Claude and Codex survivors
Delivers: B1, B4, B6 · Blocked by: C1-T1 · Lane: logic
Fixes: C1-2 (P1)
Budget: code +0 · tests +30
Seam: the same command on Claude and Codex fixtures; reuse `Fixture.write`, `user`, `tool`
Change: tests only, in `test_corrections.py`. `cl-asst` and `cl-tr` are equivalent and need no test.
Accept (each mutant from `review.md` C1-2, applied alone in a throwaway worktree, turns the file red):
- [x] `cx-um`: Codex `item_completed` `Reasoning` and `AgentMessage` items between the abort and the `UserMessage` → redirect is still the `UserMessage` text, key still `interrupt · exec` (C1-2)
- [x] `cx-tool-reset`: Codex tool call, `UserMessage`, then an abort → `interrupt · no tool` (C1-2)
- [x] `cl-user`: a Claude assistant `text` block between `tool_use` and the interrupt → key `interrupt · Bash`, and the assistant text is on no line (C1-2)
- [x] `cl-tu`: an assistant `thinking` block after the `tool_use` → key still `interrupt · Bash` (C1-2)
- [x] `nocwd`: a Claude file with no `cwd` → not read by default (C1-2)
- [x] `root-rc`: run from `repo/sub` → a session whose cwd is the repo root is kept (C1-2)
Verify: `python3 -m unittest discover -s .github/skills/checkup/scripts/tests -p test_corrections.py` (pre: OK, and each mutant above also passes)
Skills: .github/skills/workflow/references/tests.md
Status: done @ c3a6606
Writer: GPT-6.1 Sol

### C1-T3 — Kill the Copilot, report and parser survivors
Delivers: B2, B3, B7 · Blocked by: C1-T2 · Lane: logic
Fixes: C1-2 (P1)
Budget: code +0 · tests +30
Seam: the same command on Claude and Copilot fixtures; reuse `Fixture.write`, `user`, `tool`
Change: tests only, in `test_corrections.py`.
Accept (each mutant from `review.md` C1-2, applied alone in a throwaway worktree, turns the file red):
- [x] `cp-um`, `cp-clear`: each Copilot case asserts its exact `- copilot` lines: one line for the kept denial, none for the two dropped cases, none for a second user message (C1-2)
- [x] `once1`, `sortkey`: a key in 3 sessions, a key in 2 and a key in 1 → repeats print the 3-session key first, and `once: 1 key(s)` (C1-2)
- [x] `cd-amp`: a denied Bash `cd /r` → exit 0, `denial · Bash · cd` (C1-2)
- [x] `records-dict`: a line holding a JSON list → skipped, exit 0 (C1-2)
- [x] `nl`: a redirect holding a newline → printed on one line (C1-2)
Verify: `python3 -m unittest discover -s .github/skills/checkup/scripts/tests -p test_corrections.py` (pre: OK, and each mutant above also passes)
Skills: .github/skills/workflow/references/tests.md
Status: done @ f7c04bf
Writer: GPT-6.1 Sol
