Command: workflow execute lean-skill-hubs
Created: 2026-10-28 · GPT-6.1 Sol
Base: 076e032
Inputs: .workflow/lean-skill-hubs/plan.md @ 2bc4427
Status: complete

T8 runs in `~/j-skills` after the verified commits reach `origin/main`.
Authorization: plan T8 records standing approval to run `npx skills update -g` after every push.
The execution ledger also records the human's push approval, choice 1a.
Run `npx skills update -g` in the background, saving its exit and log under `/tmp`.
Then compare workflow, memory.remember, memory.compact, checkup, understand, verify and agent-docs
against `~/.agents/skills/` with `diff -rq -x __pycache__`.
Run workflow and checkup's unittest suites, `check-run.py --all`, and the agent-docs Base diff.
Write commands, exits, diff results and test counts to `receipts/t8-install.txt`.
Pass means zero diff lines, 81 and 8 tests OK, zero checker errors and agent-docs exit 0.
