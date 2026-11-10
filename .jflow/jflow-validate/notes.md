# Build notes

- This builder is gpt-6.1-sol, high, on OpenAI. The configured build seat is
  claude-opus-5-5, medium, on Anthropic. The session continues under jflow's wrong-vendor rule.
  The closing card uses `--builder-vendor openai` so check goes to another vendor.
- The human allowed fixture updates with "Allow fixture updates; preserve assertions".
  The legacy fixtures now have the required spec sections, real commit SHAs and numbered defects.
  The wait-point fixture removes its default Gate before adding the case's Gate.
  An AST comparison confirms all 36 existing assertion calls stay unchanged.
- Diagnostics name the relative file and physical line. Missing items point to line 1.
  Only the newest receipt is validated. Check reads Proof row IDs and Accepted references from
  the spec; it leaves unrelated spec fields and older receipts alone.
- Evidence length counts characters in the stripped Markdown cell, including backticks and escapes.
  Defect evidence starts at the first `Evidence:` marker. Escaped pipes stay inside their cell.
- Existing comments and docstrings are shorter to keep the skill below 50,000 bytes.
  No existing reader or seat logic changes, and the artifact templates stay unchanged.
- Extra cases cover duplicate IDs that would overwrite rows, unnumbered defects that lack stable
  references, missing files that need diagnostics, and a second Evidence marker hiding an overlong
  first part. The Accepted case also rejects a receipt reference whose acceptance lacks its SHA.

## Verification

- The historical corpus passes all 21 cases: five specs and sixteen receipts, unchanged.
- Planted faults cover all eight spec cases, ten receipt cases and three Accepted cases.
  Both 240-character boundaries pass; 241 characters fail for cells and defect evidence.
- Broken spec, check and accept records leave `run.jsonl` byte-identical; a valid check records.
  Build still records with a broken receipt present.
- Next and summary match Base byte for byte on all five finished runs.
- The record-guard mutation has a passing control. Removing that guard makes its test fail.
- Copilot lists jflow as enabled. Invocation and seat routing are unchanged.
- Final baseline command exits 0: workflow 137 tests OK, checkup 41 tests OK, jflow 26 tests OK.
- Python 3.9 runs all 26 jflow tests offline and ends OK.
- Skill files excluding tests total 49,986 bytes. The documentation grep returns one validation line.
