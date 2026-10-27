Command: workflow brainstorm run-worktrees
Created: 2026-10-27 · claude-opus-5-5
Base:    c3a29f1
Inputs:  none
Status:  complete

## Problem
Every run works in one folder on `main`. Two runs executing at once mix uncommitted edits, so tests,
commits, wrap's clean-tree check and freshness checks break. The human wants parallel runs, started
by hand or by an orchestrator such as T3, without learning git worktrees.

## Outcome
From the repo folder, `workflow execute <slug>` on a second run quietly gives it its own
`.worktrees/<slug>`; every later phase of that run finds it from the slug, and wrap merges it into
`main` and removes it. The human types the same commands as today. Surface: the phase commands,
`workflow status`, and the closing card.

## Behaviours
- B1 — `execute B` while run A has a started ticket and is not wrapped, or the repo folder has uncommitted code → `.worktrees/B` exists on branch `run/B` from `main` (`.worktrees/` is added to `.gitignore` if missing), the `AGENTS.md` `## Worktree setup` commands ran (none: a one-line note), B's ticket commits land on `run/B`, and the repo folder's files are unchanged
- B2 — `execute B` with no other run executing and a clean repo folder → no worktree; commits land on `main` as today
- B3 — `run-worktree.py where B` from the repo folder → prints `.worktrees/B` when it exists, else `.`; `workflow status` and every phase read B's artifacts from that folder, so status shows B's real phase
- B4 — `check-run.py` inside `.worktrees/B` on `run/B` → no worktree or branch warning; any other linked worktree or branch still warns as today
- B5 — wrap B, `main` not moved → fast-forward; `main` moved, no conflict → a merge commit; either way every `done @` sha in B's plan is an ancestor of `main`, `main` is pushed, the worktree and local and remote `run/B` are deleted
- B6 — wrap B with a conflicting change on `main` → the merge is aborted, `main` is merged into `run/B` in the worktree, tests run, and the state table sends B to review, scoped to the merge commit's diff
- B7 — a closing card in a worktree run → `run/B` is pushed after the gitleaks scan; the card's command is `workflow <phase> B`, unchanged
- B8 — `checkup` on a repo with a run worktree and no `## Worktree setup` block → one finding naming the block; a `.worktrees/` folder with no run behind it → one finding naming it

## Decisions
- D1 — j-skills owns the git side: a git-only script opens and lands a run's worktree, and the phase rules say where a run lives. An orchestrator (the optional conductor skill, T3 or other) only starts sessions there; j-skills names no orchestrator — product call (v3 split)
- D2 — A run lives in its worktree from execute through wrap; wrap merges it once — product call
- D3 — A run gets a worktree automatically at execute only when another run is already executing; a lone run works on `main` as today — product call
- D4 — Worktrees live in `.worktrees/<slug>` inside the repo, ignored by git — product call; git status, git grep, rg, pytest and node --test do not see them (prototype: P1)
- D5 — Wrap lands by fast-forward when `main` has not moved, else a merge commit; never rebase, so every cited sha stays valid — product call (prototype: P1)
- D6 — The human always starts the CLI in the repo folder; the phase finds `.worktrees/<slug>` from the slug and works there, no `cd` — product call
- D7 — "Another run is executing" = a run not wrapped has a ticket started, or the repo folder has uncommitted code — product call
- D8 — Setup lives in an optional `## Worktree setup` block in `AGENTS.md`, run when a worktree opens; missing → a note, and checkup flags it — product call
- D9 — A conflict at wrap is resolved inside the worktree by merging `main` in, tested, and reviewed for the merge commit only — product call
- D10 — Two runs starting the app at once stays out of scope: `verify-APP up` refuses a busy port and the agent waits or asks — product call
- D11 — A worktree run's artifacts are committed on `run/<slug>` with its code, so one branch holds the run; `where` points readers at them — code: SKILL.md state table reads the run folder
- D12 — The run branch is pushed at every closing card, keeping today's "committed and pushed" rule; wrap deletes it — code: SKILL.md closing card

## Test seams
- `scripts/run-worktree.py open|where|land <slug>` — observes B1, B2, B3, B5, B6 (new; unittest on temp git repos in `scripts/tests/`)
- `check-run.py` `checkout_warnings` — observes B4 (existing; `test_check_run.py`)
- the phase references and checkup's report, run on a scratch repo with two live runs — observe B7, B8 (receipt)

## Trust boundaries
- `AGENTS.md` `## Worktree setup` block → shell commands the script runs unasked; read only from the committed file on `main`, printed before they run
- run branch → remote push; the existing gitleaks scan runs first

## Out of scope
- Own ports per worktree — D10
- The conductor skill and any T3 launching — D1; it calls this script later
- GitHub pull requests as the landing step — the cross-vendor review already checks the code
- Worktrees for brainstorm and plan — they write only run files and do not collide (D2)
- Rebasing a run branch — breaks cited shas (D5)

Docs read: none in scope (j-skills has no PRODUCT.md or DESIGN.md); TODO.md and ROADMAP.md have no matching item
