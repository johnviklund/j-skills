# An installed skill folder is a copy with no .git, not this repo
Applies when: a workflow run or skill edit executes from a loaded skill path such as `~/.agents/skills/workflow`.
Root cause: `npx skills` installs copies (README.md, Setup); a run inside one has no commits, diffs or `Base` shas, and an edit there never reaches the clone.
Fix: before committing or pushing a skill change, run `git -C <dir> rev-parse --is-inside-work-tree` on the folder being edited. If it is the copy, follow the clone rule in `memory.remember` (references/skill-edits.md): edit a push-able clone, or hand the edit off as a skill-edit prompt when the machine has none. A run that stays in the copy falls back to file-based verification and says so.
Evidence: 1da975d (workflow realign run, drafted in the disconnected snapshot and reconciled into the clone at wrap)
Occurrences: 1 · Last confirmed: 2026-08-26 · Status: active
Enforced by: judgement
<!-- memory.compact 2026-11-01: converted from the legacy workflow/MEMORY.md entry "A Copilot-loaded skill folder can be a disconnected snapshot"; generalized from Copilot to any CLI since all installs are copies; Source → commit sha (no run folder exists). -->
