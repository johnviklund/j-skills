Command: workflow review run-worktrees
Created: 2026-10-27 · claude-opus-5-5
Base:    bc15275
Inputs:  .workflow/run-worktrees/plan.md @ 743eb2e · .workflow/run-worktrees/patch_plan.md @ f445741
Status:  complete

## Coverage
- [x] C1-T1 — 3/3: red `3c2b19f` fails without the guard (M1); fix `b890db3` changes no test file; `worktrees.md:65-66` and `wrap.md:156-157` name the scan range
- [x] C1-T2 — 2/2: comment-fence test passes, section-regex grep 0, the old regex back fails it (M5); but see C2-1
- [x] C1-T3 — 3/3: both offline subcases pass, re-raising fails them (M2); a fetch that always fails breaks the second-clone test (M8), so the catch-all hides no working path
- [x] C1-T4 — 3/3: four subcases; own `patch_plan.md` ignored (M3), `todo` counted (M4), check skipped (M9) each fail
- [x] C1-T5 — 5/5; receipt holds 7 `KILLED`; I re-ran 6 of them (M6, M7, M10–M13), all killed
- [x] Class sweep — C1-1: the other pushes are the scanned card push (`worktrees.md:44-48`) and `push --delete`; exit 3/4 merges reach origin only by a scanned card push or a later land · C1-2: no other section regex in either script · C1-3: land's push and `ls-remote` need origin by nature; `status`'s own fetch line has no failure rule (P3) · C1-5: `where` still wins for a run with a worktree or `run/<slug>` ref
- [x] Full suite 69/69 · `test_check_run.py` untouched · existing `test_run_worktree.py` assertions unchanged (only C1-T1's `git push` fixture lines) · escape-hatch scan 0 · no new dependencies · `.workflow/` check: 2 hits, both temp-repo fixtures in `test_run_worktree.py`, as in cycle 1
- [x] Outcome: probes on scratch repos (manual, no verify skill); B1 broken for one `AGENTS.md` shape (C2-1)
Size: +192 code · +367 tests · ratio 1.91 · net +550 · over 1,000: none
Ratio waiver accepted: every test the patch cycle added kills at least one mutation (its own count, +230 code and 1.60, differs from numstat; the reasoning holds)
Reachability: no new file; new branches are reached through `open`, `where`, `land` · guards shown failing: M1–M13, all killed
Independence: cross-vendor (writer GPT-6.1 Sol, OpenAI · reviewer Opus 5.5, Anthropic)
Threats: `AGENTS.md` setup → shell — who: anyone who commits to the primary branch's `AGENTS.md` · reaches: a shell in the new checkout · logged: printed before it runs (`run-worktree.py:45`) · fails open: fences from a later `# ` section run (C2-1); a non-`sh` fence is skipped silently (C2-2) · worst case: a deploy or release snippet in a later top-level section runs during `open`
Threats: pushes → origin — `land` refuses unpushed primary commits before merging (`run-worktree.py:120-122`, `test_Land_refuses_unpushed_primary_commits`) · fails open: none found
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

## Cycle 2 findings
### P1 — C2-1 · Setup now also runs shell fences from a later `# ` section
- Evidence: regression from C1-T2 (`d75f8cd`); breaks B1 ("the `## Worktree setup` commands ran"). `Doc` (`check-run.py:111`) ends a section only at `## `, while the old regex also ended it at `# `. Probe: `AGENTS.md` = `## Worktree setup` + ```` ```sh ```` `touch ready`, then `# Appendix` + ```` ```sh ```` `touch appendix_ran` → `open B` exits 0 and `.worktrees/B/appendix_ran` exists; at `f445741` it does not. Any shell fence in a later top-level section (a deploy or release snippet) runs as setup when no `## ` heading comes between. Real shape: `~/cx-intelligence/AGENTS.md` has a `# Repo Context` preamble (lines 31–39) right after an `## ` section.
- Disposition: fix now
- Resolved: —
### P2 — C2-2 · A setup fence tagged other than `sh`/`bash`/`shell` is skipped without a word
- Evidence: `run-worktree.py:44`, from T1, not touched by the fix. Probes: ```` ```zsh ````, ```` ```console ```` and ```` ```sh ```` with a trailing space each print a blank line, exit 0, and leave no `ready`. The old code does the same (pre-existing in this run, outside the C1-2 fix). Small remedy: when the block has a fence but no shell fence matched, exit 1 naming the block.
- Disposition: fix now — new and outside the cycle 2 scope, so deferred by default; the human chose to fix it (1b, 2026-10-27)
- Resolved: —
### P2 — C2-3 · `open_run` now holds two copies of the started-ticket test
- Evidence: C1-T4 added `run-worktree.py:75-77`, the same `any(field(t, "Status")[1] not in (None, "todo") …)` over `plan.md`/`patch_plan.md` as the busy loop at `:85-89`. Same-run waste in the fix diff. Small remedy: one `started(run_dir)` helper with both as callers (net about −3 lines).
- Disposition: fix now
- Resolved: —
### P3 — C2-4 · Two minor notes
- Disposition: defer — P3s stay in review.md
- Resolved: —
- `worktrees.md:22`: `status`'s own `git fetch` line gives no rule for a failed fetch, unlike `where` (C1-3's class, prose only).
- `where`'s fetch runs with git's terminal prompt allowed; `GIT_TERMINAL_PROMPT=0` would make an expired HTTPS credential fail fast instead of waiting for input in a terminal session.

## Pre-existing / environmental
- none

## Cycle 2 verdict
All five cycle 1 fix-now findings are fixed and stamped; 13 mutations of the new guards all fail the suite. New: 1 P1 (C2-1, a regression from C1-T2) and 1 small P2 (C2-3), both fix now; 1 P2 deferred to `TODO.md` (C2-2); 2 P3 deferred here (C2-4). Cycle bound reached: C2-1 and C2-3 go to the human as one decision, ➡️ a) one more cycle, since C2-1 breaks B1 · b) defer both to `TODO.md`. Wrap waits for the answer.

Cycle 3 approved by human: 2026-10-27 — option 1b, one more cycle fixing C2-1, C2-2 and C2-3. Patch cycle 2 (`patch_plan.md`): C2-T1 fixes C2-1, C2-T2 fixes C2-2, C2-T3 fixes C2-3.
