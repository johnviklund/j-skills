Command: workflow review correction-mining
Created: 2026-11-01 · cycle 2 2026-11-02 · Claude Opus 5.5
Base:    77efe6d
Inputs:  .workflow/correction-mining/plan.md @ 83c2f24
Status:  done

## Coverage
- [x] T1 — acceptance 6/6 tested and passing; live line holds (`--days 30` → `- interrupt · no tool · 2 sessions · 3 times`)
- [x] T2 — acceptance 5/5 tested and passing; C1-1 fixed @ 9911caa
- [x] T3 — acceptance 2/2; the planned grep exits 0
- [x] C1-T1 — acceptance 3/3: red commit eecbc49 touches only the test file; fix 9911caa touches only `corrections.py`; `cat … it's fine`, `echo don't` → exit 0 with `cat`, `echo`
- [x] C1-T2 — acceptance 6/6: each mutant red in a throwaway worktree (reviewer's own sweep)
- [x] C1-T3 — acceptance 5/5: each mutant red in a throwaway worktree (reviewer's own sweep)
- [x] B1…B8 delivered · Outcome observed on the terminal via manual run, no verify skill (CLI, no user screen) · out of scope untouched: no file written, no committed transcript text
- [x] .workflow/ dependency check: no hit in this run's files; the hits are the workflow skill's own scripts, which predate the run
- [x] Full suite at 77efe6d: workflow 126 OK · checkup 39 OK · exit 0. Real stores, `--all-repos --days 3650`: 461 files, exit 0
Size: +182 code · +218 tests · ratio 1.20 · net +400 · over 1,000: none
Reachability: `corrections.py` ← `checkup/references/seats.md:32`, `retro/SKILL.md:60` · guards shown failing: 22 of 22 mutants red at 77efe6d (the 13 C1-2 survivors, the C1-1 fallback, and 8 controls: `cx-abort-reason`, `cp-unatt`, `cl-sidechain`, `cl-said`, `cl-lt`, `worktrees`, `repeat2`, `cap200`)
Independence: cross-vendor (writer GPT-6.1 Sol, OpenAI · reviewer Opus 5.5, Anthropic)
Threats: transcripts → stdout · input: any text the CLIs saved, including tool output from files and web pages · reaches: stdout only; no write, no network (`corrections.py:13-24`, `main`) · changes: nothing · logged: redirect text goes to the terminal by design (D4) · fails open: no; an unexpected record shape still fails closed and kills the whole report (C2-1) · worst case: the report is missing, or a control character reaches the terminal (P3)
Escape hatches: none added

## Resolved
| Finding | Sev | Title | Disposition | Resolved |
|---|---|---|---|---|
| C1-1 | P1 | A denied Bash command with an unmatched quote crashes the whole report | fix now | @ 9911caa (cycle 2) |
| C1-2 | P1 | 15 of 48 mutants survive the whole-file sweep | fix now | @ f7c04bf (cycle 2) |

## Cycle 1 deferred P3
- `command_head` keys `cd /r&&git push` as `cd`, `FOO=1 npm test` as `FOO=1`, `sudo rm x` as `sudo`: the key splits across sessions.
- `in_repo` skips sessions started in a subfolder of the repo (`repo/.github`); B6 does not say whether they count.
- Codex `function_call` (`wait`, 65 in 80 files) does not update the tool, so an interrupt during `wait` is keyed as the previous `exec`.
- B2's fixture shape is unobserved live (F3). Claude 2.1.314 maps an interrupt at a permission prompt to the denial text (`TW.interrupt.content = Nh`). If a plain rejection is also followed by `[Request interrupted by user for tool use]`, it counts as both a denial and an interrupt, and the redirect goes to the interrupt. Check the first real denial.
- Redirect text replaces CR and LF only; other control characters (ESC) reach the terminal and the reading agent.

## Cycle 2 findings
### P2 — C2-1 Record shapes the parsers don't expect still crash the whole report
- Evidence: same class as C1-1, at the record level rather than the shell grammar. Three synthetic Claude records exit 1: `"message": null` and a string inside a `content` list raise `AttributeError` on `.get` (`corrections.py:98`, `:100`, `:106`); a Bash `tool_use` with `"command": null` makes `shlex.split` raise `ValueError` and the fallback `command.split()` raise `AttributeError` (`:40-42`). None of these shapes appear in 461 real files, so no B# or Outcome breaks today. Remedy: one `try`/`except (AttributeError, TypeError, ValueError)` around each file's events loop in `main` that skips the file, about 5 lines, plus one test.
- Disposition: defer — new and outside cycle 2's scope → `TODO.md` at wrap
- Resolved: —

## Pre-existing / environmental
- The `.workflow/` grep hits `next-step.py`, `check-run.py` and `test_skill_trials.py`. They are the workflow skill reading its own runs and predate this run.

## Cycle 1 verdict
Patch cycle: 2 × P1 fix now (C1-1, C1-2) · 0 P0 · 0 P2 · 5 P3 deferred and kept here. Patch plan: C1-T1, C1-T2, C1-T3.

## Cycle 2 verdict
Clean. C1-1 and C1-2 resolved · 0 P0 · 0 P1 · 1 P2 deferred (C2-1 → `TODO.md` at wrap) · 5 P3 kept from cycle 1. Next: wrap.
