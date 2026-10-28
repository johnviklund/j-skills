Command: workflow review run-worktrees
Created: 2026-10-27 · claude-opus-5-5
Base:    4e2d0b9
Inputs:  .workflow/run-worktrees/plan.md @ 743eb2e · .workflow/run-worktrees/patch_plan.md @ 68cbf30
Status:  complete

## Coverage
- [x] C3-T1 — 5/5: red `15d424a` fails all 4 subtests at its parent; fix `b1cd333` changes no test file; no `re.findall`; `README.md:115` and `worktrees.md:40-41` name the shell-fence rule
- [x] Class sweep — C3-1: `add_worktree` is still the only setup parser (`where` reaches it too); `doctor` checks presence only · C2-2: fence pairing is line by line and matches `Doc`'s own toggle (`check-run.py:112`)
- [x] Mutations M21–M28 on the new parser: 5 killed; M25 (`elif shell`), M27 (no `lstrip()`) and M28 (untagged not shell) survive the full suite (C4-1)
- [x] Full suite 72/72 · existing test methods unchanged (+1 method) · escape-hatch scan 0 · no new dependencies · `.workflow/` check: 2 hits, the same temp-repo fixtures as cycle 1
- [x] Outcome: probes on scratch repos at `4e2d0b9` (manual, no verify skill): prose after an `sh` fence, an untagged fence and an indented list fence all run `touch ready` and nothing else; unfenced setup stops before a checkout
Size: +208 code · +420 tests · ratio 2.02 · net +619 · over 1,000: none
Ratio waiver accepted: cycle 3's +26 test lines kill M21–M24 and M26
Reachability: no new file · guards shown failing: M1–M24, M26 · surviving: M25, M27, M28
Independence: cross-vendor (writer GPT-6.1 Sol, OpenAI · reviewer Opus 5.5, Anthropic)
Threats: `AGENTS.md` setup → shell — who: anyone who commits to the primary branch's `AGENTS.md` · reaches: a shell in the new checkout · logged: printed before it runs (`run-worktree.py:59`) · fails open: none found; text outside a shell fence never runs, and a block without one stops `open` (`run-worktree.py:42-43`) · worst case: the committed setup itself, same writers as before
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

## Cycle 2 verdict
Cycle 3 approved by human: 2026-10-27 — option 1b, one more cycle fixing C2-1, C2-2 and C2-3. Full text in git at `c6362bc`.

## Cycle 3 verdict
Cycle 4 approved by human: 2026-10-28 — 1a, one more cycle fixing C3-1 and C2-2; 2a, setup commands must sit in a shell fence. Full text in git at `68cbf30`.

## Cycle 4 findings
### P1 — C4-1 · Three conditions of the new setup parser survive mutation
- Evidence: a surviving mutation of code this cycle added (`run-worktree.py:33-40`). Full suite stays 72/72 with each change on its own: M25 `elif fenced and shell` → `elif shell` (prose after a closing `sh` fence would run as shell, against `worktrees.md:40` "text outside a shell fence never runs"); M27 `line.lstrip().startswith` → `line.startswith` (an indented fence, such as one under a list item, would stop `open`); M28 `not tag or` dropped (an untagged fence, which `worktrees.md:40` allows, would stop `open`). The code is right today: scratch-repo probes of all three shapes run `touch ready` and nothing else. The writer's receipt mutated only `elif fenced` (M26). Same class as C1-4.
- Remedy: three more `cases` rows in `test_Open_setup_reads_shell_fences_line_by_line` (`test_run_worktree.py:174`): ```` ```sh ```` `touch ready` ```` ``` ```` then `Then run the app.` → 0; an untagged fence → 0; `1. Install:` then a three-space-indented `sh` fence → 0. Test-only; no code change.
- Disposition: fix now
- Resolved: —
### P3 — C4-2 · Two minor notes
- Disposition: defer — P3s stay in review.md
- Resolved: —
- An empty `## Worktree setup` heading, which used to run nothing, now stops `open`. Decision 2a covers text without a fence, not an empty block.
- A four-backtick fence (```` ````sh ````) reads as tag `` `sh `` and stops `open`. This fails loudly, and `Doc` has the same limit.

## Pre-existing / environmental
- none

## Cycle 4 verdict
C3-1 and C2-2 are fixed and stamped @ `b1cd333`: every setup shape from cycles 2–3 now runs only shell fences or stops before a checkout exists, and 5 of 8 mutations of the new parser fail the suite. Open: C4-1 (P1): three of the parser's conditions have no test that fails when they break. The code is correct today, so B1 and the Outcome hold. The fix adds three test rows and no code. Cycle bound passed: C4-1 goes to the human. Wrap waits for the answer.
