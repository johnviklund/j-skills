Command: workflow review run-worktrees · patch cycle 3
Created: 2026-10-28 · claude-opus-5-5
Base:    68cbf30
Inputs:  .workflow/run-worktrees/review.md @ 68cbf30
Status:  complete

## Execution state
Current: C3-T1 done; next review · writer: GPT-6.1 Sol · baseline failures: none
C3-T1 @ b1cd333
Red: 15d424a · proof: receipts/c3-execution.md

## Tickets

### C3-T1 — Setup runs only shell fences, read line by line
Delivers: B1 · Blocked by: none · Lane: logic
Fixes: C3-1 (P1), C2-2 (P2, reopened)
Budget: code +6 · tests +25 · why: four `AGENTS.md` shapes, one temp repo each
Seam: `run-worktree.py open` as a subprocess on temp repos; `add_worktree` (`run-worktree.py:28-51`); `README.md:114-115`; `references/worktrees.md:39-42`
Change: replace the fence regex (`run-worktree.py:31-34`) with a loop over the block's lines. A line whose `lstrip()` starts with ```` ``` ```` opens or closes a fence; the first word of the opening line's info string is the tag. Lines inside an `sh`, `bash`, `shell` or untagged fence are the commands. A block with no such fence, unfenced text included (human decision 2a, 2026-10-28), raises naming `## Worktree setup` and `sh` fence, before any checkout exists. `README.md` says the commands go in an `sh` fence; `worktrees.md` says text outside a shell fence never runs. Red commit first: the new Open test, run and seen failing, committed alone; the fix commit changes no test file. Class sites, searched at planning time: `add_worktree` is the only setup parser; `doctor` (`run-worktree.py:140`) checks only that the block exists, so its unfenced-body tests (`test_run_worktree.py:372-385`) keep passing.
Accept:
- [x] Unfenced `## Worktree setup` / `# install deps` / `touch ready` → `open B` exits 1, stderr names `## Worktree setup` and `fence`, and neither `.worktrees/B` nor a `run/B` branch exists (C3-1, B1)
- [x] ```` ```zsh ```` `touch zsh_ran`, a blank line, then ```` ```sh ```` `touch ready` → `open B` exits 0, `.worktrees/B/ready` exists, `.worktrees/B/zsh_ran` does not (C2-2, B1)
- [x] ```` ```console ```` `$ make`, then the line `Then run:`, then ```` ```sh ```` `touch ready` → `open B` exits 0, `ready` exists, stderr lacks `Then run:` (C2-2, B1)
- [x] ```` ```bash title="setup" ```` `touch ready` → `open B` exits 0 and `ready` exists (C3-2 note, B1)
- [x] `run-worktree.py` holds no `re.findall`; the fix commit changes no test file; the full suite passes; `README.md` and `worktrees.md` each name the shell-fence rule (B1)
Verify: `python3 -m unittest discover -s .github/skills/workflow/scripts/tests && ! grep -n 're.findall' .github/skills/workflow/scripts/run-worktree.py && grep -c 'fence' .github/skills/workflow/README.md` (pre: 71 pass; `re.findall` at `:31`; README `fence` 0)
Skills: .github/skills/agent-docs/SKILL.md
Status: done @ b1cd333
Writer: GPT-6.1 Sol

## Deviations
- Parser net +10 code lines against +6 planned; the explicit fence state keeps opening, closing and language selection separate. Regression net +26 test lines against +25 planned. Acceptance scope and existing assertions are unchanged.
