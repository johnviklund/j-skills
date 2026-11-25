# Applying `jflow.py`'s `secret()` regex to paths, SHAs, or URLs triggers multi-round fix loops
Applies when: specifying or implementing a `jflow` CLI flag or argument checked by `no_secrets` or `secret()` in `.github/skills/jflow/scripts/jflow.py`.
Root cause: `secret()` rejects any 40-character `[A-Za-z0-9_+/=]{40,}` run, which collides with nested filesystem paths (`--repo`), 40-hex commit SHAs, GitHub commit and compare URLs (`--ref`), and `argparse` error messages that echo invalid arguments.
Fix: define every allowed input shape before coding: check filesystem paths per path segment, parse URLs with `urllib.parse.urlsplit` (wrapping `ValueError`, rejecting userinfo, and matching commit/compare revisions explicitly), and suppress secret-like text in `argparse` error output.
Evidence: jflow-config · escaped-defects
Occurrences: 2 · Last confirmed: 2026-11-25 · Status: active
Enforced by: judgement
