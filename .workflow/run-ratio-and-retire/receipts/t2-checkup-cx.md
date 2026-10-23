Command: workflow execute run-ratio-and-retire
Created: 2026-10-23 · GPT-6.1 Sol
Base: fb48d73
Inputs: .workflow/run-ratio-and-retire/plan.md @ cafdfaa
Status: complete

The Python block in checkup §6 was extracted unchanged to /tmp/run-ratio-checkup.py. It reuses check-run's growth function and receipt/test-file definitions. It reads tracked text for the current ratio and prints one line; no provider call or model analysis is needed for the calculation.

Ran from `/home/john/cx-intelligence`:

```sh
python3 /tmp/run-ratio-checkup.py /home/john/j-skills/.github/skills/workflow/scripts/check-run.py '50ef5321^' a5f0f341
```

Exit 0:

```text
tests net +3535 · code net +2885 · tracked tests/code 0.09 · ⚠️ workflow improve tests - goal: fewer tests, same coverage
```

The same command with the range endpoints reversed exited 0 and printed:

```text
tests net -3535 · code net -2885 · tracked tests/code 0.09 · ✅
```

Content verification: each of tests.md, phase-2-plan.md, phase-3-execute.md and phase-4-review.md has exactly one `Ratio waived: run`. The forbidden-text grep over references/, MAINTAINING.md and check-run.py returned no matches. checkup/SKILL.md has one Test growth bullet containing the required recommendation. `git diff --check` passed. T1's 49-test full suite remains the executable baseline; T2 changes its docstring only.

No trigger/frontmatter changed; no trigger trials were added. SKILL-IMPACT.md records the change for three real runs. PRODUCT.md and DESIGN.md are absent. Wrap retirement and per-ticket budget rules are unchanged. The two reference repos were read only.
