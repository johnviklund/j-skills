# TODO

Archived items: see TODO_ARCHIVE.md (grep it).

## Simplify
- Worktree setup as a script — run a committed `.worktree-setup` instead of parsing `## Worktree setup` from AGENTS.md; the parser drew 5 of 17 run-worktrees findings

## Review deferrals
- `spec-why`: the jflow skill is at 49,962 of the 50,000 bytes its size test allows. Before the next jflow change, decide whether to raise the limit or split the text.
- `jflow-config`: Unsupported flags or invalid `--session` values can echo key-like text in stderr; nothing is recorded. The human kept this existing behavior on 2026-11-08.
- `receipt-evidence-cap`: Measure the next three trial runs. Every Evidence cell and defect `Evidence:` part must be at most 240 characters, and each receipt under 3 KB.
- `jflow-validate`: Revisit non-template BROKEN citation lists and leading-zero defect IDs if needed; check-3 records the limits kept at done on 2026-11-10.
