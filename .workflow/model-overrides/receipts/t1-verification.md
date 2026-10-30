# T1 verification

Writer: GPT-6.1 Sol

- Baseline: workflow 112 tests OK; checkup 8 tests OK; exit 0.
- Red: four next-step tests produced 11 failing cases; checker test produced four failing cases.
- Focused green: next-step 30 tests OK; check-run 53 tests OK; exit 0.
- Reuse search: existing `table`, `decisions`, `model` and `EFFORTS` cover the parsing shape. Shared model validation moved into check-run; no second parser.
- Mutation: disabling unknown-key, effort-scale or required-model validation fails the override cases.
- Mutation: disabling the moved parser's part-count or empty-part condition fails existing routing cases.
- Mutation: removing model replacement, same-vendor warning or blocker-marker removal fails the override cases.
- Existing test assertions changed: none. Five test methods added; acceptance variants use subTest.
- One-part model cells need the extra parsed-effort guard described in plan F4 and Deviations.
- Final baseline command: workflow 117 tests OK; checkup 8 tests OK; exit 0.
- `check-run.py model-overrides`: 0 errors, 0 warnings. `git diff --check`: exit 0.
