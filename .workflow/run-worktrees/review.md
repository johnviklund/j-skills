Command: workflow review run-worktrees
Created: 2026-10-27 · claude-opus-5-5
Base:    5c28007
Inputs:  .workflow/run-worktrees/plan.md @ 743eb2e · .workflow/run-worktrees/patch_plan.md @ dda6fd2
Status:  complete

## Coverage
- [x] C4-T1 — 4/4: M25, M27 and M28 each fail exactly 1 subtest of `test_Open_setup_reads_shell_fences_line_by_line`; `5db97cd` changes only `test_run_worktree.py` (+3 tuple rows, no new method, no assertion changed)
- [x] Class sweep — C4-1: 17 mutations, one per condition and per tag in `run-worktree.py:33-43`. 15 fail the suite; X4 (`"shell"` dropped from the tag tuple) and X5 (`found |= shell` → `found = shell`) survive it (C4-1 reopened)
- [x] Whole-file sweep, after decision 1b: 50 more mutations over the rest of `run-worktree.py` and this run's `check-run.py` lines, with the two C4-1 rows applied. 31 fail the suite, 18 survive (C5-1), 1 is equivalent. With those rows, all 26 non-equivalent parser mutations fail; X22 (start `shell` as true) is equivalent, because `shell` is read only inside a fence and every fence opening sets it
- [x] Probes at `af1d147`: failing setup, dirty folder plus an unstarted run, slugs `a/b` and `a..b`, no slug, and an unpushed run branch all behave correctly; `land` after another clone pushed `main` leaves local `main` one merge ahead (C5-2)
- [x] Full suite 72/72 · existing test methods unchanged · escape-hatch scan 0 · no new dependencies · `.workflow/` check: 2 hits, the same temp-repo fixtures as cycle 1
- [x] Outcome: probes on scratch repos at `5c28007` (manual, no verify skill): a ```` ```shell ```` fence, and an `sh` fence followed by a `text` fence, both exit 0 and create `ready`
Size: +208 code · +423 tests · ratio 2.03 · net +622 · over 1,000: none
Ratio waiver accepted: cycle 5's +3 test lines kill M25, M27 and M28
Reachability: no new file · guards shown failing: M1–M28, X1–X3, X6–X21 · surviving: X4, X5 (C4-1); 18 listed in C5-1
Independence: cross-vendor (writer GPT-6.1 Sol, OpenAI · reviewer Opus 5.5, Anthropic)
Threats: `AGENTS.md` setup → shell — who: anyone who commits to the primary branch's `AGENTS.md` · reaches: a shell in the new checkout · logged: printed before it runs (`run-worktree.py:59`) · fails open: none found; text outside a shell fence never runs, and a block without one stops `open` (`run-worktree.py:42-43`) · worst case: the committed setup itself, same writers as before · unchanged in cycle 5 (test rows only)
Threats: pushes → origin — unchanged since cycle 2 · fails open: none found
Threats: slug → paths and refs — unchanged since cycle 1 · worst case: none found

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
| C4-2 | P3 | Two minor notes | defer — P3s stay in review.md; text in git at `5c28007` | settled (cycle 5) |

## Cycle 2 verdict
Cycle 3 approved by human: 2026-10-27 — option 1b, one more cycle fixing C2-1, C2-2 and C2-3. Full text in git at `c6362bc`.

## Cycle 3 verdict
Cycle 4 approved by human: 2026-10-28 — 1a, one more cycle fixing C3-1 and C2-2; 2a, setup commands must sit in a shell fence. Full text in git at `68cbf30`.

## Cycle 4 findings
### P1 — C4-1 · Conditions of the new setup parser survive mutation
- Evidence: original text in git at `5c28007`. The three named mutations, M25, M27 and M28, now fail the suite (`5db97cd`). Reopened in cycle 5: the class sweep mutated every condition and tag in `run-worktree.py:33-43`, and two more survive the full suite, 72/72 green. X4 drops `"shell"` from the tag tuple at `run-worktree.py:37`, so a ```` ```shell ```` fence would stop `open`, against `worktrees.md:40`. X5 changes `found |= shell` to `found = shell` at `run-worktree.py:38`, so an `sh` fence followed by a `text` fence would stop `open`. The code is right today: probes of both shapes exit 0 and create `ready`. The cycle 4 sweep gave the class as a line range and never mutated these two, breaking the rule to mutate every key a guard matches on.
- Remedy: two more `cases` rows in `test_Open_setup_reads_shell_fences_line_by_line` (`test_run_worktree.py:174`), each expecting 0: ```` ```shell ```` `touch ready` ```` ``` ````; and ```` ```sh ```` `touch ready` ```` ``` ```` then ```` ```text ```` `ok` ```` ``` ````. Test-only; no code change.
- Disposition: fix now
- Resolved: —

## Pre-existing / environmental
- none

## Cycle 4 verdict
Cycle 5 approved by human: 2026-10-28 — 1a, one more cycle adding the three test rows for C4-1. Full text in git at `5c28007`.

## Cycle 5 findings
C4-1 is reopened above: its class sweep found two more surviving mutations. C5-1 and C5-2 come from the whole-file sweep run after decision 1b, outside C4-1's class.
### P1 — C5-1 · Eighteen more conditions in this run's code survive mutation
- Evidence: each change on its own leaves the suite 72/72 green. Setup in `run-worktree.py`: A2 reuse a local `run/B` (`:52`); A4 `check=True` and A5 `bash -e` (`:60`), so "a failed setup stops execution" (`worktrees.md:43`) is unpinned. `where`: WH1 fetch only with an `origin` (`:66`); WH5 rebuild from a local `run/B` (`:73`). `open`: S1 a ticket with no `Status` (`:86`); O6 a parked run counted busy (`:101`); O8 `busy |=` → `busy =` (`:103`), which would keep B in a dirty folder when another live run has not started (B1). `land`: L2 no worktree (`:112`); L5 preflight changed (`:124`); L8 merge-tree error (`:132`); L11 delete only a pushed run branch (`:139`). `doctor`: D1 setup finding only with a worktree (`:150`). `main`: MN2 slug required (`:165`); MN1 slug pattern (`:167`), the path guard in Threats; MN3 ref format (`:172`); MN4 primary required (`:173`). Also C6b, the `main`/`master` fallback this run moved into `primary_branch` (`check-run.py:680`). Probes show the code is right; no test fails when it breaks. Same class as C1-4 and C4-1.
- Remedy: one test-only ticket, one case per survivor. L5 and L8 need a `git` wrapper first on `PATH` that forces `merge-tree`'s exit code.
- Disposition: fix now — proposed after decision 1b; the human decides
- Resolved: —
### P2 — C5-2 · `land` moves local `main` before it knows the push will succeed
- Evidence: `land` fetches only `run/*` (`run-worktree.py:68`), so a stale `origin/main` passes the unpushed check (`:134`). Probe: another clone pushes `main`, then `land B` merges into local `main` (`:137`), the push is rejected (`fetch first`), exit 1, local `main` 1 ahead, worktree kept. Loud and recoverable, but `worktrees.md` names no recovery, and the two-machine setup makes it likely.
- Remedy: before merging, fetch `origin <primary>` and stop with exit 1, `main` unmoved, when `<primary>..origin/<primary>` is not empty, naming the pull; one red test, one `worktrees.md` line.
- Disposition: fix now — proposed after decision 1b; the human decides
- Resolved: —

## Cycle 5 verdict
The three test rows work. M25, M27 and M28 each fail one subtest, and `5db97cd` touches only the test tuple. The class sweep mutated all 17 conditions and tags of the setup parser, and 15 fail the suite. Two survive: dropping the `shell` tag, and recording only the last fence's tag in `found`. The code handles both shapes correctly today, so B1 and the Outcome hold. C4-1 stays open at P1. Cycle bound passed: C4-1 goes to the human as one decision. ➡️ a) accept it as is, recorded here with no `TODO.md` line, since it breaks no behaviour · b) cycle 6 adds the two rows. Wrap waits for the answer.

Cycle 6 approved by human: 2026-10-28 — 1b, one more cycle adding the two C4-1 test rows ("important we get this right"). C5-1 and C5-2 wait on the human's next answer.
