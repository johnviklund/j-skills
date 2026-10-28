# Secret scan

- **Secret scan before every push.** `gitleaks git --log-opts="@{u}..HEAD" --redact -v --no-banner`
  (no upstream: `origin/<primary>..HEAD`); `--redact` keeps the value out of the transcript.
  Receipts are the usual source: a live query or log with a token in it. Exit 0 → push. A finding
  → no push; name file, line and rule, and ask: ➡️ **a** remove it from the unpushed commits and
  rotate it (a real value has already been in the session) · **b** false positive: add its
  fingerprint to `.gitleaksignore`; a pattern that will recur (an ID field, a public token) gets an
  allowlist in `.gitleaks.toml` instead, extending the default rules, proven by a rescan where
  the pattern is gone and a planted key is still caught. Scanner missing → no push; ask: ➡️ **a** install it · **b** push
  unscanned, noted on the card.
