Command: workflow review run-worktrees
Created: 2026-10-27 · claude-opus-5-5
Base:    5c28007
Inputs:  .workflow/run-worktrees/plan.md @ 743eb2e · .workflow/run-worktrees/patch_plan.md @ dda6fd2
Status:  complete

## Coverage
- [x] C4-T1 — 4/4: M25, M27 and M28 each fail exactly 1 subtest of `test_Open_setup_reads_shell_fences_line_by_line`; `5db97cd` changes only `test_run_worktree.py` (+3 tuple rows, no new method, no assertion changed)
- [x] Class sweep — C4-1: 17 mutations, one per condition and per tag in `run-worktree.py:33-43`. 15 fail the suite; X4 (`"shell"` dropped from the tag tuple) and X5 (`found |= shell` → `found = shell`) survive it (C4-1 reopened)
- [x] Full suite 72/72 · existing test methods unchanged · escape-hatch scan 0 · no new dependencies · `.workflow/` check: 2 hits, the same temp-repo fixtures as cycle 1
- [x] Outcome: probes on scratch repos at `5c28007` (manual, no verify skill): a ```` ```shell ```` fence, and an `sh` fence followed by a `text` fence, both exit 0 and create `ready`
Size: +208 code · +423 tests · ratio 2.03 · net +622 · over 1,000: none
Ratio waiver accepted: cycle 5's +3 test lines kill M25, M27 and M28
Reachability: no new file · guards shown failing: M1–M28, X1–X3, X6–X13 · surviving: X4, X5
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
- none new. C4-1 is reopened above: its class sweep found two more surviving mutations.

## Cycle 5 verdict
The three test rows work. M25, M27 and M28 each fail one subtest, and `5db97cd` touches only the test tuple. The class sweep mutated all 17 conditions and tags of the setup parser, and 15 fail the suite. Two survive: dropping the `shell` tag, and recording only the last fence's tag in `found`. The code handles both shapes correctly today, so B1 and the Outcome hold. C4-1 stays open at P1. Cycle bound passed: C4-1 goes to the human as one decision. ➡️ a) accept it as is, recorded here with no `TODO.md` line, since it breaks no behaviour · b) cycle 6 adds the two rows. Wrap waits for the answer.
