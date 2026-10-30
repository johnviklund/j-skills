# TODO

Archived items: see TODO_ARCHIVE.md (grep it).

## Simplify
- Worktree setup as a script — run a committed `.worktree-setup` instead of parsing `## Worktree setup` from AGENTS.md; the parser drew 5 of 17 run-worktrees findings

## Review deferrals
- unattended-mode C3-1 (P1, 2026-10-30) — `test_run_worktree.py:149-152` fixture holds one `decisions.md` row, so `any`→`all` at `run-worktree.py:100` survives; add a `plan` row before the execute row (human approved deferral)
- unattended-mode C3-2 (P2, 2026-10-30) — `run-worktree.py:213` catches `RuntimeError, OSError, CalledProcessError` but `checks.decisions` raises `ValueError` on a bad row, so `open` can crash on a malformed `decisions.md`
