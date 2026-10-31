# Skill edits need a push-able clone

Read before editing a shared skill (*Scope* in `SKILL.md`). The skill-edit prompt steps apply only when
no push-able clone exists.

**A skill edit lands only in a push-able clone.** Before editing a shared skill, find a
`johnviklund/j-skills` checkout on this machine (`git -C <dir> remote get-url origin`) and confirm
it with `git -C <dir> rev-parse --is-inside-work-tree`. Installed copies under `~/.agents/skills/`
are snapshots and do not count. With no clone, hand each approved skill edit to the human as a
**skill-edit prompt**, pasted into a session on the skills server, and leave `j-skills` itself
alone: no clone into `/tmp`, no borrowed token, no push, no edit to the installed copy. A work
machine's git identity cannot push to `j-skills`, and a borrowed token publishes under the wrong
author. Repo-local fixes (`TODO.md`, `memory/` pages, the repo's own skills) still land in this
repo. The prompt (default shape) goes in your report:

```text
In the j-skills clone, edit `.github/skills/<skill>/<file>`: <exact old text> → <exact new text>
Add to `.github/skills/workflow/SKILL-IMPACT.md`: | <date> | <skill> | <change. Judge: …> | <generic from> | 3 runs | trialing |
Apply per the log's `Mode:` line, commit only these files, push, then run `npx skills update -g`.
```

After the human pushes, each machine that runs the skills refreshes with `npx skills update -g`.
