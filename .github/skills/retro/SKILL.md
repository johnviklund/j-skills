---
name: retro
description: >
  Retrospective on one coding session or workflow run: finds where the agent lost time and
  proposes environment fixes (navigation pointers, guardrails, review rules, steering weight,
  tool economy, information access, skill friction), ranked, each routed to the file or skill
  that owns it. Run only on an explicit "retro" or "/retro" message, optionally with a run slug
  or session id; never on casual mentions of retrospectives.
---

# retro

A **retrospective** improves the agent's **environment** — the files, checks and tools the next
session starts from — using one session as evidence. The code the session produced is out of
scope; the friction it hit is the subject.

**Invocation:** `retro` (the current session) · `retro <slug>` (a `.workflow/<slug>/` run) ·
`retro <session id>`.

## Steps

1. **Load the writing guide.** Invoke the `writing-for-agents` skill: its vocabulary (context
   pointer, no-op, sprawl, cache, single source of truth) is how candidates are judged and worded.
   If it isn't installed, open the report with that line and continue.

2. **Read the primary sources.** Done when every **friction point** is located with an evidence
   pointer (transcript turn, `file:line`, or sha): a retried or failed command, a search that took
   several tries, a re-read, an edit to the wrong file, a human correction, a deviation, a patch
   cycle, an overturned finding.
   - **Run slug:** `.workflow/<slug>/` — `plan.md` (`## Deviations`, `Writer:` lines), `review.md`
     (cycles, `## Resolved`, findings marked wrong), `learnings.md`, `wrap.md`; the slug's
     `WORKLOG.md` entry (`Run:` numbers); then the transcripts for the run's dates and cwd.
   - **Transcripts:** the session store when the CLI offers one; otherwise
     `~/.copilot/session-state/<id>/events.jsonl`, `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl`,
     `~/.claude/projects/<cwd-slug>/*.jsonl`. Grep large transcripts for tool errors and human
     turns before reading around them.
   - **Steering in force:** repo `AGENTS.md`/`CLAUDE.md`, the `MEMORY.md` index, and the global
     files (`~/.copilot/copilot-instructions.md`, `~/.codex/AGENTS.md`, `~/.claude/CLAUDE.md`).

3. **Turn friction into candidates.** Done when every category below has a candidate or a
   one-line `none — <why>`. Before proposing, grep `MEMORY.md`/`memory/` for the same claim: a
   match is a recurrence (route it as a repeat, rank it up). An existing check or rule that sat
   unwired or was ignored is itself the finding.

4. **Present** the candidates ranked by cost (time or tokens lost) × likelihood of recurrence,
   in the workflow's Decisions shape: one numbered item per candidate — category, evidence
   pointer, the change, its destination — with lettered options and a ➡️ recommended default.
   Stop and wait for the answer.

5. **Route what was approved** through the owner in *Destinations*. Done when every approved
   item is written by its owner and the receipt lists each with where it landed.

## Categories

- **Navigation** — finding the right file took several searches, or a hidden dependency between
  files surprised the agent. Fix: a **navigation pointer** where the agent was when it needed it.
- **Guardrails** — the agent made a mistake a deterministic check would catch (lint, types, tests,
  a filesystem or import rule). Read the repo's own check commands and CI first. A repo with no
  guardrail (no pre-commit hook and no CI job running lint/typecheck/test) is itself a finding.
- **Review rules** — the strict reviewer missed something, or flagged noise. Classify first: a
  **mechanical** violation (fixed pattern, banned API, import shape, file location) becomes a
  guardrail — review already treats lint-enforced issues as non-findings, so each check retires a
  class of findings for good. A **judgement call** (cross-file consistency, matching surrounding
  style) becomes a memory page the reviewer reaches.
- **Steering weight** — `AGENTS.md` (repo or global) or the `MEMORY.md` index carries rules that
  belong in a check or a memory page, or has grown large enough that its rules get skimmed.
- **No-ops** — a steering line that changed no behaviour this session versus the default.
- **Tool economy** — an expensive call that a narrower one would have answered: whole-file reads
  of archives, other runs' folders or a whole `PRODUCT.md` (outside the workflow's grounding
  tiers), verbose command output, a token-hungry custom tool.
- **Information access** — a crucial fact was out of the agent's reach: server logs, a read-only
  query against a third-party service, a doc behind auth.
- **Skill friction** — a skill's own contract caused the waste: a workflow phase that forced a
  reroute, a clarify gate that missed, a budget that split a run, a memory rule that misrouted.

## Destinations

| Change | Owner | How |
|---|---|---|
| Lesson, judgement-call review rule, memory-page pointer | `memory.remember` | In a live run: `[durable→memory]` lines in its `learnings.md`. Otherwise: hand it the approved items. A repeat bumps the page's occurrences. |
| Line added, moved or removed in repo `AGENTS.md` / `README.md` | `memory.remember` | Same routing; it owns canonical-doc edits. |
| Guardrail (new or rewired check) | `workflow` | `workflow todo <the check>` — a check is code and ships through a run. |
| Reviewer missed a P0/P1 | `workflow` | `[durable→eval] code-review` line in a live run's `learnings.md` (the reviewed run's while it is open); wrap deposits it. |
| Skill change | `memory.remember` | `[durable→skill]` line: applied in its own commit, logged in `SKILL-IMPACT.md`, trialed. |
| Global steering file edit | the human | Show the exact diff; global files sit outside every repo. |
| Workspace hygiene noticed in passing | `checkup` | Name it and recommend `checkup <scope>`. |

## Reference

**Context pressure.** The implementer carries the most: it explores, writes and debugs. The
reviewer receives a diff and carries the least. So a standard is enforced where pressure is
lowest — a guardrail first, a review-reachable memory page second — and `AGENTS.md`, read by
every agent every turn, holds navigation pointers and true invariants.

**Where candidates land:**

- `AGENTS.md` / `CLAUDE.md` — always loaded; every line is paid for on every turn.
- `MEMORY.md` — the index, one line per page, read every phase.
- `memory/<slug>.md` — one pattern per page; its `Applies when` line is the context pointer that
  decides when an agent opens it, so word it on the situation, not the topic.
- Skills — a description is always-loaded context; growth goes into a reference file the skill
  points at.
- Docs (`PRODUCT.md`, `DESIGN.md`, `docs/`) — reference reached through a pointer; extend an
  existing doc before proposing a new one.
