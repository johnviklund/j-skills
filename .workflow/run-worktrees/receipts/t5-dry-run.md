Command: workflow execute run-worktrees
Created: 2026-10-27
Base: 019d84c
Inputs: .workflow/run-worktrees/plan.md @ 743eb2e
Status: complete

Writer: GPT-6.1 Sol
Fixture: `bash .workflow/run-worktrees/scripts/make-fixture.sh` created `/tmp/run-worktrees.CNO2aW/repo` and a sibling bare `origin.git`. All values and commits are synthetic; pushes use that local remote.
Reuse: adapted the existing checkup-next-actions fixture pattern; reused the shipped open, where, land and checker commands. No product helper added.
Method: the main agent followed the execute, status, closing-card and wrap landing instructions. These are agent commands, not a standalone workflow executable. No separate review model ran; A's synthetic wrapped checkpoint prepares the landing case. This probe covers routing and git operations.

ok 1 isolation: A had T1 done and T2 todo on main. `where B` printed `.`; `open B` printed `.worktrees/B`. B's Python import failed before b.py existed, then passed with VALUE equal to B. Ticket c4c53b5351928ff1b33deb78c91e030fa1315793 committed on run/B. Primary HEAD stayed f63fecf67d7974595c69be9cb6bbfd40bd8de8d6 and porcelain status stayed empty.
ok 2 status: fetched run refs and resolved A to `.` and B to `.worktrees/B`. Reading those plans produced `A · execute · none · workflow execute A` and `B · review · none · workflow review B`. The primary copy of B still had T1 todo, proving the resolved copy matters.
ok 3 handoff: B's closing card contains `workflow review B`. After a passing gitleaks scan and push, local run/B and origin/run/B both equaled f05be7e20177d30078d97f7618363fbc7e4a6c3d.
ok 4 landing: A finished and reached its synthetic wrapped checkpoint at 40b2219. After scanning B's outgoing commits, wrap's land command exited 0. Main and origin/main both equaled e457d529c34101ed812d1bd99e2b58e3ed076702, a two-parent merge containing B's ticket sha. The B worktree, local branch and remote branch were absent; primary status was empty.

Checks: scratch check-run passed before B's ticket and after its state update, with 0 errors and 0 warnings. Imports, bash syntax, diff checks and all three local-remote secret scans passed.
Mutation: a temporary script copy returned the primary checkout instead of opening isolation. On a fresh fixture, open B printed `.` and the isolation probe exited 1. The tracked script stayed unchanged.
Evidence: `/tmp/run-worktrees.CNO2aW/` holds before.json, b-ticket.sha, status.txt, B-handoff.md and scan logs. The mutation fixture is `/tmp/run-worktrees.SAk3LE/repo`.
