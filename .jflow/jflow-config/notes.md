# Builder notes

- GPT-6.1 Sol · high built this in a fresh session, rather than the configured vendor.
  The closing card uses `seat check --builder-vendor openai` to keep the check independent.
- The explicit build request supersedes the spec's earlier trial wait. The answer key is unchanged.
- Config replaces whole seats, including fallback; omitted steps retain lower layers.
  Fix, live and accept inherit build unless explicitly overridden. Every supplied file is validated.
- The three locked rules follow the roadmap decision. Public/paid approval and checker read-only
  are declarations for the session; this step adds no action runner or workflow gate.
- Secret detection rejects known key prefixes and uninterrupted tokens of at least 40 characters.
  It deliberately rejects some long identifiers too. Errors never include rejected values.
- `flow.json` gives spec the builder role because spec runs with the human, not as a separate agent role.
- Tests group Proof rows 1/7, 2/4, 3/5 and 6 by their shared inputs. Existing record tests cover row 9;
  the specified grep and size/diff measurements cover rows 8 and 10.
- Validation: baseline 137/41/8 tests OK; final 137/41/12 tests OK. All 12 jflow tests also pass
  on Python 3.9. Record/summary JSON keys match; the required prose grep finds no seat values.
  Script growth is 79 net lines; the skill is 49,932 bytes, excluding `__pycache__`.
  Removing either the config secret guard or the field-type guard fails its corresponding test.
- Fix check-1 defect 1: match key prefixes at a boundary and scan record arguments before parsing,
  excluding `--repo DIR` and `--repo=DIR`. Summary and seat arguments are not recorded.
  One regression table isolates `task-list` and a long repo path across record, summary and seat.
  It fails on the original code and when either fix is removed; secret rejection still passes.
- The receipt's private path was replaced with a synthetic path that reproduces the same refusal.
  No verdict or evidence result changed. Duplicate prose was pruned to keep the size budget.
- After the fix: 137 workflow, 41 checkup and 13 jflow tests OK; all 13 jflow tests pass on Python 3.9.
  Total script growth is 80 net lines; the skill is 49,962 bytes without `__pycache__`.
- Fix check-2 defect 1: generic `sk-` detection requires 20 payload characters instead of one,
  so a short name such as `sk-ui` remains valid. The specific key prefixes and 40-character rule stay.
  The regression table first failed on `sk-ui`, then passed after the code fix. A generic `sk-`
  token with 20 payload characters is also checked in config and record; removing its detection fails.
- Python 3.9 runs the exact reported `record sk-ui spec --model m --effort high` input and summary
  with exit 0. All 13 jflow tests pass there. The skill is 49,975 bytes; script growth stays 80 lines.
- Final repo verification after fix 2: 137 workflow, 41 checkup and 13 jflow tests OK; diff check clean.
- Human approval for fix 3 and check 4: "The human approved one more fix and a fourth check
  (option A): make the generic sk- rule stop refusing hyphenated names such as
  sk-onboarding-checklist, for example by needing a digit or no inner hyphen, while real keys
  are still refused." This permits a fourth check despite the normal three-check cap.
- Fix check-3 defect 1: generic `sk-` payloads still need 20 characters, plus either a digit or
  no inner hyphen. The reported name now records successfully. Specific key and bare-token rules stay.
  The regression first failed on the old code. Removing the new condition, either branch, or the
  no-hyphen endpoint makes a relevant test fail. Config and record reject both generic key forms.
- All 13 jflow tests pass on Python 3.9; the exact reported record command and summary exit 0.
  Pruned duplicate card/record prose. Script growth is 81 net lines; the skill is 49,886 bytes.
- Final repo verification after fix 3: 137 workflow, 41 checkup and 13 jflow tests OK; diff check clean.
- Human approval for fix 4 and check 5 (option A, 2026-11-08): stop scanning the run slug for
  secrets, as `--repo` already is, and keep scanning `--model` and `--effort`. A test covers
  `sk-onboarding-checklist-v2`. This permits a fifth check despite the normal three-check cap.
- Fix check-4 defect 1 implements that approval: the parser validates only record's `--model`
  and `--effort` values for secrets. Run slugs and repo paths are identifiers outside the scan.
  Config secret detection is unchanged. The versioned-name regression failed before the fix.
- Both fields reject key-like values, including `--option=value`, with no echo or log change in a
  real run. Removing either validator fails the test. Python 3.9 records and summarizes the reported
  name, both other names in check-4, and the long underscore name from check-3.
- Verification after fix 4: 137 workflow, 41 checkup and 13 jflow tests OK; all 13 also pass on
  Python 3.9. Script growth is 83 net lines; the skill is 49,905 bytes. Diff and skill checks pass.

- Closing preparation: all 10 rows are PROVED at the last check, with no code change since it.
  The driver contains fixture checks already covered by unit tests, so no reusable control verb remains.
  The done commit removes it and closes the corresponding TODO confirmation.
- Publication hygiene: a private path in an unpushed receipt revision was replaced with its synthetic
  equivalent before publication. Code is unchanged in every rewritten revision; embedded commit
  references were updated and resolve. The unsanitized history remains only in a local backup ref.
- memory.remember routed the human's field-scoping correction to its existing owners: jflow's
  locked-rule instructions, parser validators and tests. No duplicate memory page was added.
- Closing decision: the human chose "A. Keep existing behavior and finish" for check-5's
  parser-error Maybe. Unsupported flags and invalid session values may echo on stderr; nothing
  is recorded. The model/effort validators stay. This is a kept limitation, not an open defect.
- Final verification: 137 workflow tests OK, 41 checkup tests OK, 13 jflow tests OK. The code is
  unchanged since the proved commit; the completed full-suite run is reused for these closing docs.
