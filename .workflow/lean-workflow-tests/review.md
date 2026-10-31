Command: workflow review lean-workflow-tests
Created: 2026-10-31
Base:    3de9155
Inputs:  .workflow/lean-workflow-tests/plan.md @ 9a77cd3 · patch_plan.md @ 6c5a986
Status:   done

## Coverage
- [x] T1 — acceptance 5/5: `covmap-base.txt` totals 630·673 / 204·229 / 188·170, 120 tests · 266 cases; `mutants-base.txt` ids unique, ratio 1.4/1.6 killed, message mutants per script; `time-base.txt` median 52.312 s
- [x] T2 — acceptance 3/3: `test_run_worktree.py` 34 tests · 549 lines · `grep -c check-run` 0; `CheckoutTests` 5 cases in `test_check_run.py`; mapping rows present
- [x] T3 — acceptance 4/4: `test_check_run.py` 49 tests · 563 lines; F10 cases and the three named tests gone; one-entry WORKLOG is a case of `test_wrap_worklog_entry_with_seats_is_clean`; override validation keeps one valid and one bad row
- [x] T4 — acceptance 3/3: `test_next_step.py` 29 tests · 453 lines · `grep -c Traceback` 1, inside `fails()`
- [x] T5 — acceptance 4/4: re-ran `compare.py base final` → `lost 0` for every script and kind, exit 0; ROADMAP row 4 `Done 2026-10-31`; AGENTS.md `about 51 s`; three scripts unchanged since aefd430
- [x] C1-T1 — acceptance 3/3: `grep` finds no `created` parameter and 0 `expected_code`; AST scan of all three test files finds no unread parameter, local or never-passed default; `Ran 112 tests` OK; assertion calls 87 · 78 · 126, same as before
- [x] B1–B8 delivered · Outcome observed via manual run, no verify skill: `Ran 112 tests in 50.382s OK` + checkup `Ran 8 … OK`, exit 0; test lines 1,630 → 1,565 · out of scope untouched (scripts and checkup suite: empty diff since aefd430)
- [x] .workflow/ dependency check: hits are pre-existing (`next-step.py:119-181` names run artifacts by design; fixture strings in `test_run_worktree.py`); this run adds none
- [x] Escape-hatch scan: no hits · new dependencies: none
- [x] Mapping (B6) spot-checked: `test_budget_plan_with_size_and_budgets_is_clean` → `test_brief_trust_boundaries_are_optional` empty-section case asserts the same `0 errors · 0 warnings` on `plan()` (test_check_run.py:153-158); dropped check-run override rows are in `test_override_bad_rows_name_key_without_json` (test_next_step.py:113-119)
Size: +0 code · +107 tests · ratio n/a (code 0) · net -65 · over 1,000: none
Reachability: `scripts/compare.py` → the plan's Verify commands (run tool, D5) · `fails()` 9 callers · `run_command(expected=)` 14 callers · `check(checkout=)` 1 caller, an existing helper extended · guards shown failing: hand mutants in a throwaway worktree, each caught: M1 drop effort-None raise in `overrides()` (`next-step` suite 1 failure), M2 one-entry WORKLOG end arm → `start + 1` (1 failure), M3 drop `branch == run/{slug}` in `checkout_warnings` (2 failures), M4 drop the `.worktrees/<slug>` path match (1 failure); `compare.py` with one killed→survived mutant and one deleted arm planted → exit 1 naming both; cycle 2: M5 `--key review` returns 2, M6 drop the missing-key raise, each fails `test_key_prints_model_lines_without_a_run`, unmutated copy OK
Independence: cross-vendor (writer GPT-6.1 Sol / OpenAI · reviewer Claude Opus 5.5 / Anthropic)
Threats: mutated script copies → `mutate.py:111-124` copies scripts, tests and ROUTING.md into a `TemporaryDirectory` and runs unittest with `cwd` inside it; input comes only from this run's own tool; it reaches temp copies and temp fixture repos; it changes nothing in the real checkout; raw JSON goes to `/tmp`; nothing fails open; worst case a mutant fixture errors in `/tmp`

## Resolved
| Finding | Sev | Title | Disposition | Resolved |
|---|---|---|---|---|
| C1-1 | P2 | Folded tests leave dead parameters and bindings | fix now | @ 961deed (cycle 2) |
| C1-2 | P3 | The suite-time gain is inside run-to-run spread | defer — stays here | settled (cycle 2) |

## Cycle 2 findings
None. Scope: the fix diff `433f504..961deed`, 3 test files, +16 −16 lines, plus the C1-1 class in every workflow test file. The fix touches tests only and no script, so no Red commit applies. The edits remove only bindings and parameters; every expected value stays the same. The `nope` row still fails through `fails()`, which checks exit code 1. The full suite gives `Ran 112 tests in 50.754s OK` and the checkup suite `Ran 8 tests … OK`, exit 0. The fix diff adds no `.workflow/` reference.

## Pre-existing / environmental
- `.workflow/` grep hits in `next-step.py` are the workflow tool reading run folders by design, not a product dependency.

## Cycle 1 verdict
Acceptance holds: every ticket's lines are tested and pass, B1–B8 are delivered, and the coverage map plus the mutation run lose nothing (re-run, and four hand mutants agree). One small P2 (dead test parameters and bindings) goes to patch cycle 1 as C1-T1. One P3 is deferred.

## Cycle 2 verdict
Ship as-is. C1-1 is fixed at every site of its class, and the scan finds no more dead parameters or bindings. Two new mutants show the rewritten `--key` test still catches a broken exit code. No new findings.
