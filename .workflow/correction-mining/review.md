Command: workflow review correction-mining
Created: 2026-11-01
Base:    1806a43
Inputs:  .workflow/correction-mining/plan.md @ 83c2f24
Status:  complete

## Coverage
- [x] T1 — acceptance 6/6 tested and passing; live line holds (`--days 30` → `- interrupt · no tool · 2 sessions · 3 times`)
- [x] T2 — acceptance 5/5 tested and passing; B2 crashes on a quote-unbalanced Bash command (C1-1)
- [x] T3 — acceptance 2/2; the planned grep exits 0
- [x] B1…B8 delivered · Outcome observed on the terminal via manual run, no verify skill (CLI, no user screen) · out of scope untouched: no file written, no committed transcript text
- [x] .workflow/ dependency check: no hit in this diff; the hits are the workflow skill's own scripts, which predate the run
- [x] Full suite: workflow 126 OK · checkup 33 OK · exit 0. Real stores, `--all-repos --days 3650`: 458 files, exit 0, 5.0 s
Size: +179 code · +169 tests · ratio 0.94 · net +348 · over 1,000: none
Reachability: `corrections.py` ← `checkup/references/seats.md:32`, `retro/SKILL.md:60` · guards shown failing: 33 of 48 mutants red; 15 survive (C1-2)
Independence: cross-vendor (writer GPT-6.1 Sol, OpenAI · reviewer Opus 5.5, Anthropic)
Threats: transcripts → stdout · input: any text the CLIs saved, including tool output from files and web pages · reaches: stdout only; no write, no network (`corrections.py:13-24`, `main`) · changes: nothing · logged: redirect text goes to the terminal by design (D4) · fails open: no; a bad record fails closed and kills the whole report (C1-1) · worst case: the report is missing, or a control character reaches the terminal (P3 below)
Escape hatches: none added

## Cycle 1 findings
### P1 — C1-1 A denied Bash command with an unmatched quote crashes the whole report
- Evidence: B2 · `corrections.py:39` `shlex.split` raises `ValueError: No closing quotation` for `cat > f <<'EOF'\nit's fine\nEOF` and for `echo don't`. A one-denial fixture exits 1 with a traceback, so checkup's Corrections section and retro's recurrence check get nothing for the next 14 days. Same class as two exam cases: a parser raises on outside text and the whole report dies.
- Disposition: fix now
- Resolved: —

### P1 — C1-2 15 of 48 mutants survive the whole-file sweep; 13 of them hide real-data paths
- Evidence: every mutant below leaves `test_corrections.py` green. Real Codex rollouts hold 3,022 non-user `item_completed` items in 80 files (`Reasoning`, `CommandExecution`, `AgentMessage`), so `cx-um` would key and quote them all.
  - `cx-um` `:61` `UserMessage` check → always true · `cx-tool-reset` `:65` tool not reset after a user turn
  - `cl-user` `:101` assistant records read as user text · `cl-tu` `:98` `tool_use` → any non-text block (a `thinking` block clears the tool)
  - `cp-um` `:83` a user message with no denial printed as a redirect · `cp-clear` `:85` a second user message also printed
  - `nocwd` `:156` a file with no cwd counted as this repo · `root-rc` `:29` a run from a subdirectory drops sessions at the root
  - `once1` `:173` `== 1` → `>= 1` · `sortkey` `:170` repeats unordered, so "first 5" is not the top 5
  - `cd-amp` `:41` `'&&' in parts` → true (bare `cd /r` crashes) · `records-dict` `:21` a non-object line crashes · `nl` `:166` newline kept in a redirect
  - Equivalent, no test needed: `cl-asst` `:96` (only assistant records carry `tool_use`) · `cl-tr` `:105` (a human never types the denial sentence)
- Disposition: fix now
- Resolved: —

### P3
- `command_head` keys `cd /r&&git push` as `cd`, `FOO=1 npm test` as `FOO=1`, `sudo rm x` as `sudo`: the key splits across sessions.
- `in_repo` skips sessions started in a subfolder of the repo (`repo/.github`); B6 does not say whether they count.
- Codex `function_call` (`wait`, 65 in 80 files) does not update the tool, so an interrupt during `wait` is keyed as the previous `exec`.
- B2's fixture shape is unobserved live (F3). Claude 2.1.314 maps an interrupt at a permission prompt to the denial text (`TW.interrupt.content = Nh`). If a plain rejection is also followed by `[Request interrupted by user for tool use]`, it counts as both a denial and an interrupt, and the redirect goes to the interrupt. Check the first real denial.
- Redirect text replaces CR and LF only; other control characters (ESC) reach the terminal and the reading agent.

## Pre-existing / environmental
- The `.workflow/` grep hits `next-step.py`, `check-run.py` and `test_skill_trials.py`. They are the workflow skill reading its own runs and predate this run.

## Cycle 1 verdict
Patch cycle: 2 × P1 fix now (C1-1, C1-2) · 0 P0 · 0 P2 · 5 P3 deferred and kept here. Patch plan: C1-T1, C1-T2, C1-T3.
