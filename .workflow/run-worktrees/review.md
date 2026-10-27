Command: workflow review run-worktrees
Created: 2026-10-27 · claude-opus-5-5
Base:    f445741
Inputs:  .workflow/run-worktrees/plan.md @ 743eb2e
Status:  complete

## Coverage
- [x] T1 — acceptance 6/6 tested and passing; line 3's "exactly once" assertion is vacuous (C1-4)
- [x] T2 — acceptance 5/5 tested and passing
- [x] T3 — acceptance 5/5 tested and passing
- [x] T4 — 6/6 greps re-run: 4 · README 1 · 2 names, grep fixed, 215 lines · 1 · 1 and 2 · 1 · 1
- [x] T5 — receipt has 4 `ok` lines; its `/tmp/run-worktrees.CNO2aW` evidence matches (merge `e457d52` holds B's `c4c53b5`; no `run/B`, no worktree)
- [x] B1–B8 delivered, except B1 on a setup fence that opens with a comment (C1-2) and B2/B3 offline (C1-3) · Outcome observed on scratch repos: T5's evidence plus 7 probes of my own (manual, no verify skill) · out of scope untouched (no port, conductor, PR or rebase code)
- [x] .workflow/ dependency check — 0 hits; `run-worktree.py` reads run folders as workflow tooling, like `check-run.py`
- [x] Full suite 61/61 pass · `test_check_run.py` untouched (no assertion drop) · escape-hatch scan 0 hits · no new dependencies
Size: +177 code · +260 tests · ratio 1.47 · net +431 · over 1,000: none
Reachability: `run-worktree.py` → `worktrees.md`, execute, wrap step 9, checkup §4; `primary_branch` → `checkout_warnings` and `run-worktree.py` · guards shown failing: busy rule, done/parked skip, fast-forward, own-run branch/path/slug · not shown: 7 (C1-4)
Independence: cross-vendor (writer GPT-6.1 Sol, OpenAI · reviewer Opus 5.5, Anthropic)
Threats: `AGENTS.md` setup → shell — who: anyone who commits `## Worktree setup` to the primary branch (the human, or a landed run) · reaches: a shell under the human's account in the new checkout · changes: anything that account can · logged: printed before it runs (`run-worktree.py:45`), read only via `git show <primary>:AGENTS.md` (`test_Open_runs_only_committed_primary_setup`) · fails open: a fence opening with a comment runs nothing (C1-2) · worst case: no worse than the repo's own test commands
Threats: pushes → origin — who: any run's commits · reaches: the public remote · logged: cards scan the run branch (`worktrees.md:44-47`) · fails open: `land` pushes primary commits no one scanned (C1-1) · worst case: a token in another run's receipt goes public
Threats: slug → paths and refs — the regex plus `check-ref-format` (`run-worktree.py:143-148`) allow only `[A-Za-z0-9._-]`; no traversal · worst case: none found

## Cycle 1 findings
### P1 — C1-1 · Landing pushes other runs' unscanned commits on the primary branch
- Evidence: `run-worktree.py:113-114` merges, then pushes `main` with no check of `origin/main..main`; wrap step 9 and `worktrees.md:53` scan only the run checkout's outgoing commits. Probe: run A on `main` commits `a_receipt.txt` holding `SECRET=abc`, unpushed; `land B` exits 0 and `origin/main` now holds A's commit. Breaks the hub's "secret scan before every push" and the brief's trust boundary "run branch → remote push; the existing gitleaks scan runs first". A run on `main` commits per ticket and pushes only at its card, so this window is open during every parallel execute session.
- Disposition: fix now
- Resolved: —
### P1 — C1-2 · A setup block whose fence opens with a shell comment runs nothing
- Evidence: B1 ("the `## Worktree setup` commands ran"). `run-worktree.py:24` ends the section at any `^#{1,2} ` line, fences included, so `## Worktree setup` + fenced `# install deps` / `touch ready` captures only the opening fence line; `open B` exits 0, prints a blank line and `.worktrees/B/ready` is missing. Same-run waste too: `check-run.py:100-127` `Doc.section()` already cuts `## ` sections outside code fences and is loaded by this script.
- Disposition: fix now
- Resolved: —
### P1 — C1-3 · Every phase stops when origin cannot be fetched
- Evidence: B2 ("commits land on main as today") and the Outcome ("the same commands as today"). `run-worktree.py:52-53` raises on a failed `git fetch`; `worktrees.md:14` stops the phase on a nonzero exit, and the hub sends every phase and `status` through `where`. Probe: lone run, origin unreachable → `where B` exits 1. Offline, with expired credentials or in a sandbox without network, even a lone run on `main` can no longer run `status`, review or wrap.
- Disposition: fix now
- Resolved: —
### P1 — C1-4 · Seven mutations of new guards survive the suite
- Evidence: in a throwaway worktree, each change below leaves all 61 tests green:
  `run-worktree.py:106` `all`→`any`, and the `.txt` key dropped. A code conflict paired with a `WORKLOG.md` conflict (F7: nearly every parallel wrap) would get exit 4 and land with no review. Today it correctly exits 3 (probe), but no test pins that.
  `:81` `not in (None, "todo")`→`is not None`: a planned, unstarted run on `main` would force isolation (B2, D7).
  `:33` exclude dedupe forced on: T1's "after two opens … exactly once" test is vacuous, because the second `open` returns early via `where`.
  `:94` dirty run checkout, `:88` primary not on `main`, `:59` run checkout off `run/<slug>`: none of these guards is shown failing.
- Disposition: fix now
- Resolved: —
### P2 — C1-5 · `open` moves a run already executing on `main` into a worktree, leaving its own edits behind
- Evidence: D2 (a run's home is fixed at execute, through wrap), D3 ("another run"). B on `main` with T1 done, T2 todo and `t2.py` half-written (an interrupted session) → `open B` prints `.worktrees/B`; `t2.py` stays untracked in the repo folder, missing from B's checkout. It also keeps every later `open` busy. Small: B's own plan in the primary checkout having a started ticket → stay at `.`.
- Disposition: fix now
- Resolved: —
### P3 — C1-6 · Four minor notes
- Disposition: defer — P3s stay in review.md
- Resolved: —
- `worktrees.md:19-24`: `status` resolves remote-only `run/*` refs through `where`, so a read-only command builds worktrees and runs setup on a second clone, with one fetch per run.
- Exit 4 says "keep both sides" for every `*.md`/`*.txt` conflict. In j-skills a `SKILL.md` is the product, and two edits to one rule kept side by side contradict each other with no review (decision 3a; noted, not reopened).
- A setup block with no fence runs its whole body as shell, prose included.
- check-run: T2/T3 tests slightly over 1.5× code (73 vs 60 allowed, 56 vs 54); run-level 1.47. The tests are not redundant; accepted.

## Pre-existing / environmental
- none

## Cycle 1 verdict
Fix first: 4 P1 and 1 small P2, all fix now; 4 P3 deferred here. Patch cycle 1 (`patch_plan.md`): C1-T1 fixes C1-1, C1-T2 fixes C1-2, C1-T3 fixes C1-3, C1-T4 fixes C1-5, C1-T5 fixes C1-4.
