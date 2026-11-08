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
