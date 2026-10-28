---
name: verify
description: >
  The verify.create and verify.maintain commands; load this skill to run either. Builds and
  maintains a repo's own verification skill: a project-local verify-APP skill with a small
  control CLI that launches, health-checks, drives and screenshots the real app, plus a feature
  map saying how a user reaches each feature and what proves it works. "verify.create"
  generates it and proves it on one feature; "verify.maintain" re-checks every mapped feature
  from source and live, then commits only proven corrections. Run only on an explicit
  "verify.create" or "verify.maintain" message, or a workflow ticket that names one; never on
  casual mentions of verifying, testing or checking a change.
---

# verify

Agents can only close the loop on their own work when they can drive the real app the way a
user does. This skill gives a repo that ability once, as a **lever** (a tool every later agent
runs instead of improvising): a project-local skill named `verify-APP` with a control CLI and a
**feature map**. `workflow` execute and review use it when it exists; `checkup` flags it when it
goes stale.

Two commands:

| Command | Does |
|---|---|
| `verify.create` | Interviews the repo, builds the control CLI, writes `verify-APP`, seeds the feature map, proves it on one feature, wires it up |
| `verify.maintain` | Re-checks every mapped feature from source and live, fixes drift in the skill's own folder, commits the proven corrections |

Every message to the human follows the Rules of the `plain` skill: invoke it once before the
first report. Questions use one decision each, options lettered, a ➡️ recommended default.

## Where the generated skill lives

Measured 2026-10-03 (Claude Code, Codex CLI 0.160.0, Copilot CLI 1.0.91): Claude Code reads
repo skills only from `.claude/skills/`, Codex only from `.agents/skills/`, and Copilot from
`.github/skills/`, `.agents/skills/` and `.claude/skills/`, listing a symlinked skill once. So:

- The real folder is `.agents/skills/verify-APP/`, where `APP` is the repo's short name in
  kebab-case.
- `.claude/skills/verify-APP` is a relative symlink to it:
  `ln -s ../../.agents/skills/verify-APP .claude/skills/verify-APP`.

```text
.agents/skills/verify-APP/
  SKILL.md              launch · doctor · drive · evidence · cleanup · helpers
  scripts/control       the control CLI (executable)
  features/README.md    the map: baseline, conventions, proof rules, feature index, Last maintained
  features/<feature>.md one file per user-facing feature
```

The generated skill is for anyone who works in the repo, with or without j-skills, so it names
no j-skill and needs nothing outside the repo.

## Command instructions

Read only the reference for the command being run:

- `verify.create`: [references/create.md](references/create.md).
- `verify.maintain`: [references/maintain.md](references/maintain.md).
