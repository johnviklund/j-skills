Command: workflow brainstorm run-worktrees
Created: 2026-10-27 · claude-opus-5-5
Base:    c3a29f1
Inputs:  none
Status:  drafting

## Problem
Every run works in one folder on `main`. Two runs executing at once mix uncommitted edits, so tests,
commits, wrap's clean-tree check and freshness checks break. The human wants parallel runs, started
by hand or by an orchestrator such as T3, without learning git worktrees.

## Decisions
- D1 — j-skills owns the git side: a git-only script opens and lands a run's worktree, and the phase rules say where a run lives. An orchestrator (the optional conductor skill, T3 or other) only starts sessions there; j-skills names no orchestrator — product call (v3 split)
- D2 — A run lives in its worktree from execute through wrap; wrap merges it once — product call
- D3 — A run gets a worktree automatically at execute only when another run is already executing; a lone run works on `main` as today — product call
- D4 — Worktrees live in `.worktrees/<slug>` inside the repo, ignored by git — product call; git status, git grep, rg, pytest and node --test do not see them (prototype: P1)
- D5 — Wrap lands by fast-forward when `main` has not moved, else a merge commit; never rebase, so every cited sha stays valid — product call (prototype: P1)
