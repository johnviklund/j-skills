Command: workflow review run-worktrees
Created: 2026-10-28 · claude-opus-5-5
Base:    0066b00
Inputs:  .workflow/run-worktrees/plan.md @ 743eb2e · .workflow/run-worktrees/patch_plan.md @ 7740521
Status:  done

## Coverage
- [x] C6-T1 — 4/4: red `be47a91` adds one assertion to `test_run_worktree.py` alone and, run at its parent, fails on that assertion only (stderr still says "pull it into"). Fix `f61de07` touches no test file
- [x] Content checks: `pull` 1 hit in `worktrees.md`, the rebase warning · 0 in `run-worktree.py` · `moved on origin` 1 · `git merge --no-edit` on 1 line of `SKILL-IMPACT.md`
- [x] Class sweep, C6-1: every `pull`, `rebase` and `fast-forward` line in the workflow skill. The only other `pull` is `README.md:166`, about updating the skill folder. `open` uses `merge --ff-only` (`run-worktree.py:80`). No other advice rebases
- [x] Full suite 81/81 at `0066b00` · escape-hatch scan 0 · no new dependencies · `.workflow/` check unchanged from cycle 6
- [x] Outcome: probe on a scratch repo through the test harness, manual, no verify skill. With `pull.rebase=true`, run A's unpushed ticket on `main`, and another clone pushing `main`: `land B` exits 1. The printed `git merge --no-edit origin/main` exits 0 and keeps A's sha on `main`. `land B` then asks for the scan and push. After the push it exits 0, and A's sha and B's ticket sha are both on `origin/main`
Size: +212 code · +529 tests · ratio 2.50 · net +732 · over 1,000: none
Ratio waiver: cycle 7 adds 1 test line, the red assertion. The waiver's stale +423 is C6-2, deferred
Reachability: no new file · guards shown failing: the new advice assertion, by the red commit at its parent
Independence: cross-vendor (writer GPT-6.1 Sol, OpenAI · reviewer Opus 5.5, Anthropic)
Threats: `AGENTS.md` setup → shell — code unchanged in cycle 7
Threats: pushes → origin — cycle 7 changes only the refusal text at `run-worktree.py:114`; the fetch-then-refuse order stays · fails open: none found
Threats: slug → paths and refs — code unchanged in cycle 7 · worst case: none found

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
| C6-1 | P2 | The new "pull" advice rebases another run's unpushed commits | fix now | @ f61de07 (cycle 7) |
| C6-2 | P3 | One minor note | defer — P3s stay in review.md; text in git at `0066b00` | settled (cycle 7) |

## Cycle 2 verdict
Cycle 3 approved by human: 2026-10-27 — option 1b, one more cycle fixing C2-1, C2-2 and C2-3. Full text in git at `c6362bc`.

## Cycle 3 verdict
Cycle 4 approved by human: 2026-10-28 — 1a, one more cycle fixing C3-1 and C2-2; 2a, setup commands must sit in a shell fence. Full text in git at `68cbf30`.

## Cycle 4 verdict
Cycle 5 approved by human: 2026-10-28 — 1a, one more cycle adding the three test rows for C4-1. Full text in git at `5c28007`.

## Cycle 5 verdict
Cycle 6 approved by human: 2026-10-28 — 1b, one more cycle adding the two C4-1 test rows ("important we get this right"). Then 1a and 2a: C5-1 and C5-2 join cycle 6. Full text in git at `fa0e4c4`.

## Cycle 6 verdict
Cycle 7 approved by human: 2026-10-28 — 1a, one more cycle fixing C6-1. Full text in git at `0066b00`.

## Pre-existing / environmental
- `b42c2f0` is the human's own skill edit, written with Copilot, and no ticket of this run. It adds 3 lines to `SKILL.md`, which is now 218 lines against T4's cap of 215, and edits `wrap.md` and `phase-3-execute.md`. Not reviewed here.

## Cycle 7 findings
None. C6-1 is fixed at its only two sites, and the advice works on the probe.

## Cycle 7 verdict
Ship as-is. C6-T1 changes the refusal and `worktrees.md` to name `git merge --no-edit origin/<primary>`. Its red test failed first, and the fix left every test file alone. The suite passes 81/81. On a scratch repo with `pull.rebase=true`, following the new advice keeps another run's unpushed ticket sha, and `land` then finishes. C6-1 is resolved and C6-2 stays deferred. No finding is open. Next: `workflow wrap run-worktrees`.
