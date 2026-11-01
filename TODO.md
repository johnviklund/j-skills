# TODO

Archived items: see TODO_ARCHIVE.md (grep it).

## Simplify
- Worktree setup as a script — run a committed `.worktree-setup` instead of parsing `## Worktree setup` from AGENTS.md; the parser drew 5 of 17 run-worktrees findings

## Review deferrals
- correction-mining C2-1 (P2, 2026-11-02) — `corrections.py` `main`: wrap each file's events loop in `try/except (AttributeError, TypeError, ValueError)` and skip the file, plus one test (null `message`, string content block, null Bash `command`).
