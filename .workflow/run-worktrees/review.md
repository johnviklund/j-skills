Command: workflow review run-worktrees
Created: 2026-10-28 · claude-opus-5-5
Base:    fa0e4c4
Inputs:  .workflow/run-worktrees/plan.md @ 743eb2e · .workflow/run-worktrees/patch_plan.md @ cf15502
Status:  complete

## Coverage
- [x] C5-T1 — 2/2: X4 and X5 each fail `test_Open_setup_reads_shell_fences_line_by_line` on their new row; all 25 parser mutations fail the suite; `00a4ae6` changes only `test_run_worktree.py`, +2 rows
- [x] C5-T2 — 5/5: each of the 18 C5-1 mutations fails the test written for it; `bbaa7a1` changes only `test_run_worktree.py`; no existing assertion removed, two loops gain cases and `run_branch` gains `push=True`
- [x] C5-T3 — 4/4: red `f77b468` fails at its parent because `main` moves; fix `59e842b` touches no test file; `moved on origin` has 1 hit in `worktrees.md`; L15 fails the suite
- [x] Class sweep, C5-2: three more mutations of the new check, outside `mutate.py`. L16 drops the fetch, L17 reverses the range, L18 never raises. All three fail the suite
- [x] Full named sweep at `fa0e4c4`: `mutate.py --jobs 8` reports 75 killed, 0 survived, 0 missing
- [x] Full suite 81/81, 72 plus 9 new methods · escape-hatch scan 0 · no new dependencies · `.workflow/` check: 4 hits, all temp-repo fixtures writing a fake run, 2 new at `test_run_worktree.py:116,137`
- [x] Outcome: probe on a scratch repo, manual, no verify skill. Another clone pushes `main`, `land B` exits 1, local `main` stays put and the worktree stays. A `git pull` after it, under `pull.rebase=true`, rewrites a run's unpushed ticket commit (C6-1)
Size: +212 code · +528 tests · ratio 2.49 · net +731 · over 1,000: none
Ratio waiver accepted: each of cycle 6's +105 test lines serves a named mutation, 21 kills plus one red test. The waiver in `plan.md` still quotes +423 tests (P3)
Reachability: no new skill file; `mutate.py` is a run script run by hand · guards shown failing: all 75 named, plus L16, L17, L18
Independence: cross-vendor (writer GPT-6.1 Sol, OpenAI · reviewer Opus 5.5, Anthropic)
Threats: `AGENTS.md` setup → shell — code unchanged in cycle 6; A4 and A5 are now pinned, so a failing setup stops `open` (`test_Open_stops_when_setup_fails`)
Threats: pushes → origin — `land` now fetches `origin <primary>` before any merge (`run-worktree.py:111`); a failed fetch stops `land` with nothing changed · fails open: none found
Threats: slug → paths and refs — code unchanged; MN1 and MN3 are now pinned · worst case: none found

## Resolved
| Finding | Sev | Title | Disposition | Resolved |
|---|---|---|---|---|
| C1-1 | P1 | Landing pushes other runs' unscanned primary commits | fix now | @ b890db3 (cycle 2) |
| C1-2 | P1 | A setup fence opening with a shell comment runs nothing | fix now | @ d75f8cd (cycle 2) |
| C1-3 | P1 | Every phase stops when origin cannot be fetched | fix now | @ c65c961 (cycle 2) |
| C1-4 | P1 | Seven guard mutations survive the suite | fix now | @ 59bfc5c (cycle 2) |
| C1-5 | P2 | `open` moves a run already on `main` into a worktree | fix now | @ 31b78b4 (cycle 2) |
| C1-6 | P3 | Four minor notes | defer — text in git at `42d00c4` | settled (cycle 2) |
| C2-1 | P1 | Setup ran shell fences from a later `# ` section | fix now | @ b0b55af (cycle 3) |
| C2-2 | P2 | A setup fence tagged other than `sh`/`bash`/`shell` is skipped without a word | fix now | @ b1cd333 (cycle 4) |
| C2-3 | P2 | `open_run` held two copies of the started-ticket test | fix now | @ f7a6658 (cycle 3) |
| C2-4 | P3 | Two minor notes | defer — text in git at `c6362bc` | settled (cycle 3) |
| C3-1 | P1 | An unfenced setup block stops at its first `# ` comment | fix now | @ b1cd333 (cycle 4) |
| C3-2 | P3 | Two minor notes | defer — the first is gone at `b1cd333`; text in git at `68cbf30` | settled (cycle 4) |
| C4-1 | P1 | Conditions of the new setup parser survive mutation | fix now | @ 00a4ae6 (cycle 6) |
| C4-2 | P3 | Two minor notes | defer — P3s stay in review.md; text in git at `5c28007` | settled (cycle 5) |
| C5-1 | P1 | Eighteen more conditions in this run's code survive mutation | fix now | @ bbaa7a1 (cycle 6) |
| C5-2 | P2 | `land` moves local `main` before it knows the push will succeed | fix now | @ 59e842b (cycle 6) |

## Cycle 2 verdict
Cycle 3 approved by human: 2026-10-27 — option 1b, one more cycle fixing C2-1, C2-2 and C2-3. Full text in git at `c6362bc`.

## Cycle 3 verdict
Cycle 4 approved by human: 2026-10-28 — 1a, one more cycle fixing C3-1 and C2-2; 2a, setup commands must sit in a shell fence. Full text in git at `68cbf30`.

## Cycle 4 verdict
Cycle 5 approved by human: 2026-10-28 — 1a, one more cycle adding the three test rows for C4-1. Full text in git at `5c28007`.

## Cycle 5 verdict
Cycle 6 approved by human: 2026-10-28 — 1b, one more cycle adding the two C4-1 test rows ("important we get this right"). Then 1a and 2a: C5-1 and C5-2 join cycle 6. Full text in git at `fa0e4c4`.

## Cycle 6 findings
### P2 — C6-1 · The new "pull" advice rebases another run's unpushed commits
- Evidence: `worktrees.md:67` and the error at `run-worktree.py:114` both say to pull. This machine sets `pull.rebase=true` globally. Probe on a scratch repo: run A commits a ticket on `main` and has not pushed it; another clone pushes `main`; `land B` exits 1 as designed. Then `git pull origin main` rebases A's commit, and its old sha is no longer an ancestor of `main`. A's `done @` line now cites a commit no other clone will ever have, against D5's "every cited sha stays valid". This run's own C5 session left 7 commits unpushed on `main`, so the state is real. No B# breaks, since B5 names only B's shas, and the Outcome holds.
- Remedy: both sites name a merge instead of a pull, for example `git merge --no-edit origin/<primary>`, since `land` has just fetched it. That fast-forwards when the primary has no local commits and merges when it has, whatever the pull config says. About 2 changed lines; the test asserts only `origin/main`, so it stays as it is.
- Disposition: fix now
- Resolved: —
### P3 — C6-2 · One minor note
- `plan.md`'s `Ratio waived: run` line quotes +423 tests against +246 code. Cycle 6 added 105 test lines, which the waiver does not mention.
- Disposition: defer — P3s stay in review.md

## Pre-existing / environmental
- `b42c2f0` is the human's own skill edit, written with Copilot, and no ticket of this run. It adds 3 lines to `SKILL.md`, which is now 218 lines against T4's cap of 215, and edits `wrap.md` and `phase-3-execute.md`. Not reviewed here.

## Cycle 6 verdict
The three fix tickets work. X4, X5 and the 18 C5-1 conditions now each fail the suite, and the full named sweep reads 75 killed, 0 survived. The new land check stops before `main` moves. Its red test failed first, the fix touched no test file, and three more mutations of the new lines fail too. C4-1, C5-1 and C5-2 are resolved. One new P2, C6-1, sits in the fix's own advice text: under this machine's `pull.rebase=true`, "pull" rewrites another run's unpushed commits. Cycle bound passed, so C6-1 goes to the human as one decision. ➡️ a) cycle 7, one ticket changing the two lines · b) defer to `TODO.md`, since it breaks no behaviour. Wrap waits for the answer.
