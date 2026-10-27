Command: workflow review run-worktrees
Created: 2026-10-27 · claude-opus-5-5
Base:    baa7476
Inputs:  .workflow/run-worktrees/plan.md @ 743eb2e · .workflow/run-worktrees/patch_plan.md @ bc15275
Status:  complete

## Coverage
- [x] C2-T1 — 3/3: red `832e12d` fails at the parent code; fix `b0b55af` changes only `check-run.py`; `check-run.py` output for all runs identical at `832e12d` and `b0b55af` (37 lines, `diff` empty); removing the `# ` reset fails it (M14)
- [x] C2-T2 — 3/3: red `3880941` fails 2 subtests at the parent; fix `791ff62` changes no test file; `worktrees.md:40-41`; removing the raise (M15), the `[ \t]*` (M16), the check (M17) or moving it after `worktree add` (M18) each fail
- [x] C2-T3 — 2/2: `not in (None, "todo")` once; `f7a6658` is +8/−8 in `run-worktree.py` only; `started()` ignoring `patch_plan.md` (M19) or counting `todo` (M20) fails
- [x] Class sweep — C2-1: every other `Doc.section` caller reads run artifacts (output unchanged), but the setup block can also be unfenced, where a `# ` shell comment is now a heading (C3-1) · C2-2: a non-shell fence before a shell fence still breaks fence pairing (C2-2 reopened) · C2-3: no third copy of the started test
- [x] Full suite 71/71 · `test_check_run.py` untouched · existing `test_run_worktree.py` assertions unchanged (only two new methods) · escape-hatch scan 0 · no new dependencies · `.workflow/` check: 2 hits, the same temp-repo fixtures as cycle 1
- [x] Outcome: probes on scratch repos at `baa7476` and `bc15275` (manual, no verify skill); B1 broken for two `AGENTS.md` shapes (C3-1, C2-2)
Size: +198 code · +394 tests · ratio 1.99 · net +583 · over 1,000: none
Ratio waiver accepted: cycle 2's +27 test lines each kill a mutation (M14–M18)
Reachability: no new file; `started()` has two callers in `open_run` · guards shown failing: M1–M20, all killed
Independence: cross-vendor (writer GPT-6.1 Sol, OpenAI · reviewer Opus 5.5, Anthropic)
Threats: `AGENTS.md` setup → shell — who: anyone who commits to the primary branch's `AGENTS.md` · reaches: a shell in the new checkout · logged: printed before it runs (`run-worktree.py:49`) · fails open: prose between a non-shell and a shell fence runs as shell (C2-2) · worst case: a prose line that is also a valid command runs during `open`; same writers as the setup itself, so no new privilege
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
| C2-3 | P2 | `open_run` held two copies of the started-ticket test | fix now | @ f7a6658 (cycle 3) |
| C2-4 | P3 | Two minor notes | defer — text in git at `c6362bc` | settled (cycle 3) |

## Cycle 2 findings
### P2 — C2-2 · A setup fence tagged other than `sh`/`bash`/`shell` is skipped without a word
- Evidence: original text in git at `c6362bc`. Reopened in cycle 3: `791ff62` raises only when no fence matches. When a non-shell fence comes first, the regex (`run-worktree.py:31`) takes that fence's closing ```` ``` ```` as an opener. Probes (same at `bc15275`): ```` ```zsh ```` fence, blank line, ```` ```sh ```` `touch ready` → exit 0, nothing runs, no `ready`; with `Then run:` between them → bash runs `Then run:` (exit 127) and the `sh` fence never runs.
- Disposition: fix now — the human chose to fix it (1b, 2026-10-27)
- Resolved: —


## Cycle 2 verdict
All five cycle 1 fix-now findings are fixed and stamped; 13 mutations of the new guards all fail the suite. New: 1 P1 (C2-1, a regression from C1-T2) and 1 small P2 (C2-3), both fix now; 1 P2 deferred to `TODO.md` (C2-2); 2 P3 deferred here (C2-4). Cycle bound reached: C2-1 and C2-3 go to the human as one decision, ➡️ a) one more cycle, since C2-1 breaks B1 · b) defer both to `TODO.md`. Wrap waits for the answer.

Cycle 3 approved by human: 2026-10-27 — option 1b, one more cycle fixing C2-1, C2-2 and C2-3. Patch cycle 2 (`patch_plan.md`): C2-T1 fixes C2-1, C2-T2 fixes C2-2, C2-T3 fixes C2-3.

## Cycle 3 findings
### P1 — C3-1 · An unfenced setup block stops at its first `# ` comment
- Evidence: regression from C2-T1 (`b0b55af`); breaks B1 ("the `## Worktree setup` commands ran"). `README.md:114-115` says to add shell commands under the heading and requires no fence; unfenced text runs as-is (`run-worktree.py:34`). `Doc` (`check-run.py:114`) now treats an unfenced `# ` line as a heading. Probe: `## Worktree setup` / `# install deps` / `touch ready` → `open B` exits 0, prints a blank line, no `ready`; at `bc15275` `ready` exists. A comment mid-block drops every line after it, again without a word.
- Disposition: fix now
- Resolved: —
### P3 — C3-2 · Two minor notes
- Disposition: defer — P3s stay in review.md
- Resolved: —
- ```` ```bash title="setup" ```` gets `requires sh, bash, shell or untagged fences`: the message names the tag it rejects as allowed.
- `assertIn("sh", result.stderr)` (`test_run_worktree.py:167`) also passes on `bash`/`shell`; it meets the acceptance literal but proves little.

## Pre-existing / environmental
- none

## Cycle 3 verdict
C2-1 and C2-3 are fixed and stamped; 7 new mutations (M14–M20) all fail the suite. Open: C3-1 (P1, a regression from the C2-1 fix) and C2-2 (P2, reopened at a second fence shape). Both silently skip setup commands, so both break B1. One fix ticket closes both: read the setup block line by line, take commands only from `sh`/`bash`/`shell`/untagged fences by their opening line, and stop `open` when the block has text but no shell fence. Cycle bound passed: both go to the human as one decision, ➡️ a) one more cycle · b) defer both to `TODO.md` (C3-1 needs `Approved by human:`). Wrap waits for the answer.
