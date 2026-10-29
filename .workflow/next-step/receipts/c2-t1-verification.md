Command: workflow execute next-step · C2-T1
Created: 2026-10-29 · GPT-6.1 Sol
Base: eac69f8
Inputs: .workflow/next-step/patch_plan.md @ 688e443
Status: complete

Reused review_findings, the shared parser used by check_review and next_step. No new helper.

- Baseline: C2-T2's final suites passed before the reproducing test. Workflow 108 tests, `OK`; checkup 8 tests, `OK`; exit 0.
- Red: 0a0f06d commits only the new parametrized CLI test. Its two cases fail: C2-1 instead of C2-2 after folding a leading ID; C2-2 instead of C2-3 after folding an interior ID. The suite runs 25 tests and exits 1.
- Verify: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests -p test_next_step.py`. Runs 25 tests, `OK`, exit 0.
- The planned detached historical checkout at 68cbf30 first reports `Resolve C2-1, C3-1 before continuing.` After the fix, its blocker action is exactly `Resolve C2-2, C3-1 before continuing.` Its Why is `Patch cycle 3 · fix C2-2, C3-1`. The planned grep returns 1; the checkout is removed afterward.
- `python3 -m unittest discover -s .github/skills/workflow/scripts/tests -p test_check_run.py`: 51 tests, `OK`, exit 0. The file stays unchanged from C2-T2.
- Four isolated mutations fail: ignore table rows; stop excluding resolved IDs; read the title cell instead of the first cell; remove the absent-table fallback. Each exits 1 with failing CLI assertions.
- Full: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests && python3 -m unittest discover -s .github/skills/checkup/scripts/tests`. Workflow 109 tests, `OK`; checkup 8 tests, `OK`; exit 0.
- The fix commit leaves every test file untouched. Next-step assertion lines increase from 69 to 71 only in the red commit; existing assertions remain unchanged. Code added +4, net +3; tests net +14. Both budgets hold.
- Completed-run gate, plan Base 19533a5 to eac69f8: code added 272, code net 261, tests net 407; ratio 1.496, below 1.5. No waiver.
- Session recording raised plan.md to 121 lines. Removed its duplicate no-product-docs read line and shortened the matching impact note; it now has 120 lines. No acceptance line changed. No behavioural deviation.
