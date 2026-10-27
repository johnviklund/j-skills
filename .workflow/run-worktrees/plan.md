Command: workflow plan run-worktrees
Created: 2026-10-27 · Opus 5.5
Base:    743eb2e
Inputs:  .workflow/run-worktrees/brainstorm.md @ c3a29f1
Status:  complete

Docs read: none in scope (j-skills has no PRODUCT.md, DESIGN.md or AGENTS.md)
Size: code 801 · tests 503 · ratio 0.63 · largest touched check-run.py 801, test_check_run.py 503 · over 1,000: none (new: run-worktree.py, test_run_worktree.py, references/worktrees.md)
Decisions: 1a · 2a · 3a · machine switch: a run's worktree is rebuilt from `origin/run/<slug>` on any clone (asked 2026-10-27) · tickets 1a approved, plus the `SKILL.md` live-run grep fix in T4
Split declined by human: 2026-10-27 (26 acceptance lines; neither half works alone)

## Execution state
Current: T1 done; T2 ready
T1 @ 81aa880
writer: GPT-6.1 Sol
Baseline: 49 tests passed at c626d11; user approved suite plus ticket Verify commands.
Session 1: T1
Uncommitted: none · Pending decision: none
## Findings
| # | What is true | What it changes |
|---|---|---|
| F1 | `SKILL.md` is 212 lines, 12.7 KB: already over its ~180-line, ~10 KB hub budget (`MAINTAINING.md`) | worktree rules go in a new `references/worktrees.md`; `SKILL.md` gets a pointer and edits to the state-table and card lines, net ≤ +3 lines |
| F2 | `check-run.py` has `Doc`, `parse_tickets`, `field` (100–276), `git_out` (669), and primary-branch detection inside `checkout_warnings` (682–685) | `run-worktree.py` loads `check-run.py` by importlib and reuses them; the branch lines move into `primary_branch(repo)` — no second copy |
| F3 | `test_check_run.py`'s `check()` builds temp repos, but `tests.md:20` bars a test importing a test | `test_run_worktree.py` gets its own small repo + bare-remote fixture |
| F4 | `checkout_warnings` (674) has no test today | T3 adds the first and keeps both existing warnings asserted |
| F5 | B1's `.gitignore` edit changes a tracked code file in the repo folder: it breaks B1's "repo folder unchanged", trips D7's own uncommitted-code test and wrap's clean-tree gate | 2a: `open` writes `.worktrees/` once to `.git/info/exclude`; no tracked file changes |
| F6 | Land merges into `main`, checked out in the repo folder, where another run may have uncommitted work; git refuses a merge that would overwrite a dirty file and allows one that doesn't | land relays git's refusal with the paths, exits 1, `main` unmoved; no stash |
| F7 | Every wrap appends to `WORKLOG.md` (step 8), often `TODO.md` and memory pages; two worktree runs wrapping in turn conflict there nearly every time | 3a: a conflict only in `*.md`/`*.txt` is resolved in the worktree keeping both sides and landed again, no review; a code conflict follows B6 |
| F8 | Wrap 9a marks the run `done`; landing after it would send a done, not-live run to review on a code conflict | land becomes wrap step 9; the archive becomes step 10, run in the repo folder, committing only `.workflow/<slug>/` |
| F9 | `git show --remerge-diff <merge>` shows only how a merge's conflicts were resolved (git 2.36+; here 2.56.0) | the review cycle after a B6 merge reads that output plus the full suite |
| F10 | P1 probe: `grep -r` and `find` see `.worktrees/`; `wrap.md:172` and `phase-4-review.md:135` grep the repo with `grep -rn` | both gain `--exclude-dir=.worktrees` |
| F11 | j-skills has no verify skill; the surface is skill text an agent follows | no `verify.create` prefactor: a scratch-repo dry run (T5) proves the Outcome, as `checkup-next-actions` did |
| F12 | D7 counts a run already in its own worktree as executing, so a third run gets a worktree even when the repo folder is free | 1a: only a run working in the repo folder (no worktree of its own) with a started ticket, or uncommitted code there, sends the next run to a worktree |
| F13 | `Doc.status()` splits on whitespace, so `Status:  complete` (two spaces, as this brief has) parses; `SKILL.md:54`'s live-run grep does not (`TODO.md` P2) | `run-worktree.py` uses `Doc.status()`; the grep fix is in TODO impacts |
| F14 | B8 as checkup prose needs a checkup session to observe it | `run-worktree.py doctor` prints both findings and checkup §4 runs it, so B8 is unit-tested |
| F15 | gitleaks is installed; `SKILL.md`'s scan with no upstream already covers `origin/<primary>..HEAD`, so `run/B`'s first push is scanned | no scan change; land pushes `main` only after wrap's scan |
| F16 | `.worktrees/` and `.git/info/exclude` are per clone; on another machine `where` would print `.` and read `main`'s stale copy of the plan, redoing done tickets | `where` rebuilds `.worktrees/<slug>` from `origin/run/<slug>` when that branch exists, and fast-forwards a worktree that is behind it |
| F17 | A conflicting merge run in the repo folder would leave another run's uncommitted files mid-merge; `git merge-tree --write-tree` (git 2.38+) finds conflicts without touching any checkout | land checks with `merge-tree` first; only a clean merge runs in the repo folder |
## Tickets
### T1 — A second run gets its own worktree, and any clone finds it
Delivers: B1, B2, B3 · Blocked by: none · Lane: logic
Budget: code +130 · tests +170 · why: every case builds a temp repo with a bare `origin`
Seam: `run-worktree.py open|where <slug> --repo <dir>` run as a subprocess on temp repos; `primary_branch(repo)` moves out of `check-run.py`'s `checkout_warnings`
Accept:
- [x] run A on `main` with a `done @` ticket, no `.worktrees/A`, `open B` → prints `.worktrees/B`, on `run/B` at `main`'s sha; repo folder `git status --porcelain` empty (B1)
- [x] clean repo folder, the only started run has its own `.worktrees/A` → `open B` prints `.`, `git worktree list` gains no line (B2)
- [x] uncommitted `src.py` in the repo folder, no run started → `open B` creates `.worktrees/B`; after two opens `.git/info/exclude` holds `.worktrees/` exactly once (B1)
- [x] `AGENTS.md` on `main` with `## Worktree setup` running `touch ready` → output shows `touch ready` and `.worktrees/B/ready` exists; no block → output has `no ## Worktree setup in AGENTS.md` (B1)
- [x] `where B` → `.` before `open B`, `.worktrees/B` after (B3)
- [x] a second clone with `origin/run/B` and no worktree → `where B` creates `.worktrees/B` at `origin/run/B`'s sha; a worktree behind it is fast-forwarded to that sha (B3)
Verify: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests -p 'test_run_worktree.py' -k Open -k Where` (pre: new file — NO TESTS RAN)
Skills: none
Status: done @ 81aa880
Writer: GPT-6.1 Sol
### T2 — Wrap lands a worktree run on `main` and cleans it up
Delivers: B5, B6 · Blocked by: T1 · Lane: logic
Budget: code +90 · tests +150 · why: one temp repo with a bare `origin` per merge shape
Seam: `run-worktree.py land <slug> --repo <dir>` run as a subprocess on temp repos
Accept:
- [ ] `main` not moved → `main` equals `run/B`'s tip, `origin/main` equals `main`, no `.worktrees/B`, no `run/B` branch here and none on `origin` (B5)
- [ ] `main` moved by a non-conflicting commit → `main`'s tip has 2 parents and every `done @` sha in B's plan is an ancestor of `main` (B5)
- [ ] `main` changed `src.py` against `run/B` → exit 3, `main`'s sha unchanged, `.worktrees/B` mid-merge of `main` with `src.py` conflicted, output names `workflow review B` (B6)
- [ ] the only conflict is in `WORKLOG.md` → exit 4, `main`'s sha unchanged, output says resolve keeping both sides, commit, land again (B6)
- [ ] repo folder has an uncommitted edit to a file `run/B` changes → exit 1, `main`'s sha unchanged, output names that file (B5)
Verify: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests -p 'test_run_worktree.py' -k Land` (pre: new file — NO TESTS RAN)
Skills: none
Status: todo
### T3 — Checks know a run's own worktree
Delivers: B4, B8 · Blocked by: T1 · Lane: logic
Budget: code +40 · tests +80 · why: each case builds a repo with a linked worktree
Seam: `check-run.py` and `run-worktree.py doctor --repo <dir>` run as subprocesses in temp repos
Accept:
- [ ] `check-run.py` inside `.worktrees/x` on `run/x` → no `linked worktree` warning and no `on branch` warning (B4)
- [ ] `check-run.py` inside `.worktrees/x` on branch `feature` → the `on branch` warning (B4)
- [ ] `check-run.py` inside a linked worktree outside `.worktrees/` → the `linked worktree` warning (B4)
- [ ] `doctor` with `.worktrees/B` and no `## Worktree setup` in `main`'s `AGENTS.md` → one line naming `## Worktree setup` (B8)
- [ ] `doctor` with `.worktrees/old` holding no live `.workflow/old/brainstorm.md` → one line naming `.worktrees/old` (B8)
Verify: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests -k Checkout -k Doctor` (pre: NO TESTS RAN)
Skills: none
Status: todo
### T4 — The phase rules send each step to the run's worktree
Delivers: B1, B3, B5, B6, B7, B8 · Blocked by: T1, T2, T3 · Lane: mechanical
Budget: code +0 · tests +0
Seam: the text of `SKILL.md`, a new `references/worktrees.md`, `phase-3-execute.md`, `phase-4-review.md`, `wrap.md`, checkup's `SKILL.md`, the workflow `README.md`
Accept:
- [ ] `grep -o 'run-worktree.py \(open\|where\|land\|doctor\)' references/worktrees.md | sort -u | wc -l` → 4, and the workflow `README.md` links `references/worktrees.md` (B3)
- [ ] `SKILL.md` names `references/worktrees.md`, its live-run grep reads `Status: *\(drafting`, and it is at most 215 lines (`wc -l`) (B3, B7)
- [ ] `grep -c 'run-worktree.py open' references/phase-3-execute.md` → 1 (B1)
- [ ] `grep -c 'run-worktree.py land' references/wrap.md` → 1; `--exclude-dir=.worktrees` in `wrap.md` and `phase-4-review.md` → 2 in total (B5)
- [ ] `grep -c 'remerge-diff' references/phase-4-review.md` → 1 (B6)
- [ ] `grep -c 'run-worktree.py doctor' ../checkup/SKILL.md` → 1 (B8)
Verify: `cd .github/skills/workflow && grep -o 'run-worktree.py \(open\|where\|land\|doctor\)' references/worktrees.md | sort -u | wc -l` (pre: new file — 0)
Skills: .github/skills/agent-docs/SKILL.md
Status: todo
### T5 — Two runs side by side on a scratch repo, end to end
Delivers: B7 · Blocked by: T4 · Lane: logic
Budget: code +40 · tests +0
Seam: the phase commands on a scratch repo with a local bare `origin`, built by `.workflow/run-worktrees/scripts/make-fixture.sh`
Accept:
- [ ] run A executing on `main`, `workflow execute B` from the repo folder → B's ticket commit is on `run/B`; the repo folder's `git status --porcelain` is unchanged
- [ ] `workflow status` from the repo folder after B's ticket → B's line reads `review` and `workflow review B`
- [ ] the closing card after B's ticket → command `workflow review B`; `origin/run/B` equals local `run/B` (B7)
- [ ] wrap B after A wrapped → `main` contains B's ticket sha; `.worktrees/B` and `run/B` are gone
Verify: `grep -c '^ok ' .workflow/run-worktrees/receipts/t5-dry-run.md` → 4 (pre: new file — exit 2)
Skills: none
Status: todo

## Coverage
- Outcome → T5 (the phase commands and status on a scratch repo with two runs)
- B1 → T1, T4 · B2 → T1 · B3 → T1, T4 · B4 → T3 · B5 → T2, T4 · B6 → T2, T4 · B7 → T4, T5 · B8 → T3, T4
- Out of scope: own ports per worktree → untouched · conductor skill and T3 launching → untouched · GitHub PRs as landing → untouched · worktrees for brainstorm and plan → untouched · rebasing a run branch → untouched

## Risks
- T2 is riskiest: it moves `main` in a folder another run may be editing; `merge-tree` first and git's dirty-file refusal bound it. Outside its files: every card step reads `check-run.py`'s checkout warnings (T3). Not taken: a pull request as the landing step.

## TODO impacts
- `TODO.md` P2 "`SKILL.md:54` live-run grep misses `Status:  complete`" → completed by T4 (human asked, 2026-10-27).

## Product doc impacts
- PRODUCT.md, DESIGN.md: none exist. Workflow `ROADMAP.md`: no statement on worktrees or parallel runs; no changes.
