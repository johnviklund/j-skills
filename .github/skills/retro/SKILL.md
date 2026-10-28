---
name: retro
description: >
  Retrospective on one coding session or workflow run: finds where the agent lost time or built
  more than the work needed, and proposes the few environment fixes worth making (at most three),
  each with its measured cost and routed to the file or skill that owns it. Run only on an
  explicit "retro" or "/retro" message, optionally with a run slug or session id; never on casual
  mentions of retrospectives.
---

# retro

A **retrospective** improves the agent's **environment** — the files, checks and tools the next
session starts from — using one session as evidence. The code the session produced is evidence,
not the subject: the friction it hit and the overbuild it shipped are.

A retro returns **at most three fixes**, often fewer. Every proposed rule is one more line every
later agent reads, so a retro that proposes a fix for every friction point adds sediment instead
of removing waste. The human should be able to approve the whole list without weighing each item.

**Invocation:** `retro` (the current session) · `retro <slug>` (a `.workflow/<slug>/` run) ·
`retro <session id>`.

## Steps

1. **Load the writing guides.** Invoke the `agent-docs` skill: its vocabulary (context pointer,
   no-op, sprawl, cache, single source of truth) is how candidates are judged and worded. Invoke
   the `plain` skill too: the report to the human follows its Rules.

2. **Read the primary sources.** Done when every **friction point** is located with an evidence
   pointer (transcript turn, `file:line`, or sha) and a cost in minutes, tokens or review cycles:
   a retried or failed command, a search that took several tries, a re-read, an edit to the wrong
   file, a human correction, a deviation, a patch cycle, an overturned finding, a ticket or file
   later cut.
   - **Run slug:** `.workflow/<slug>/` — `plan.md` (`## Deviations`, `Writer:` lines), `review.md`
     (cycles, `## Resolved`, findings marked wrong), `learnings.md`, `wrap.md`; the slug's
     `WORKLOG.md` entry (`Run:` numbers); then the transcripts for the run's dates and cwd.
   - **Transcripts:** the session store when the CLI offers one; otherwise
     `~/.copilot/session-state/<id>/events.jsonl`, `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl`,
     `~/.claude/projects/<cwd-slug>/*.jsonl`. Grep large transcripts for tool errors and human
     turns before reading around them.
   - **Steering in force:** repo `AGENTS.md`/`CLAUDE.md`, the `MEMORY.md` index, the global
     files (`~/.copilot/copilot-instructions.md`, `~/.codex/AGENTS.md`, `~/.claude/CLAUDE.md`),
     and the trialing rows of `workflow/SKILL-IMPACT.md`.

3. **Turn friction into candidates.** Done when every friction point is a candidate or marked
   expected (a deliberate failing-test run, a planned human gate). The *Categories* below are a
   lens for spotting causes, not a quota: name each root cause once, and merge friction points
   that share one. A human turn that redirected the work ("is this the simple solution?", "what
   goes in this file?") marks the costliest friction: the environment should have done that work.

4. **Apply the bar.** Done when every candidate is kept or dropped with a one-word reason. A kept
   candidate clears all five:
   - **Costly** — a number from the evidence: minutes, review cycles, tokens, human
     interventions, or records a check or trial needs and could not read. No number → `no cost`.
   - **Recurring** — its root cause, not the incident, was seen at least twice (this run, a memory
     page's occurrences, `WORKLOG.md`, `SKILL-IMPACT.md`, an earlier retro), or a step every run
     takes causes it. A judgement slip with no earlier sign is a `one-off`: `memory.remember`
     promotes a judgement call to a skill at 3 occurrences, and a retro does not jump that ladder.
   - **Decision-changing** — names which agent does what differently, at which step. A change
     that only adds reading is a `no-op`.
   - **Uncovered** — read the target file and `SKILL-IMPACT.md` first. A clear rule that exists
     and went unfollowed is an execution slip: when its trial is open, record the run as trial
     evidence for or against it; when the rule is buried or weakly worded, the fix is rewording or
     moving it, never a second copy. Otherwise `covered`.
   - **Smallest form** — deleting or rewording a line beats adding one; a check beats prose; a
     clause in an existing rule beats a new rule. State the net words the fix adds or removes.

   Keep the top three by cost × recurrence. Zero is a valid result: report "no fix worth making".

5. **Present** the kept fixes in the workflow's Decisions shape, one numbered item each, then the
   rest, and stop for the answer. Exact layout:

   ```
   **1. <the problem in one line>** <Category>.
   Cost: <number> · Seen: <count and where> · Evidence: <pointer>
   - ➡️ a) <the change> → <destination> (<±N words>). <why it wins>
   - b) <alternative>. <why weaker>

   **Trial evidence:** <SKILL-IMPACT row> — <for | against>: <one line>   (omit when none)
   **Dropped:** <finding> — <reason> · <finding> — <reason>
   **Housekeeping:** <one line, or omit>
   ```

6. **Route what was approved** through the owner in *Destinations*. Done when every approved
   item is written by its owner and the receipt lists each with where it landed.

## Categories

- **Overbuild** — the run built more than its Outcome needed: a ticket, abstraction or file
  that review or the human later cut, a helper with one caller, a wrapper that adds nothing,
  tests far over the ticket's Budget, a design the human had to ask to simplify. The fix is the
  rule or check that would have stopped it at brainstorm or plan; overbuild still in the code is a
  `workflow todo Simplify:` line naming what to delete.
- **Navigation** — finding the right file took several searches, or a hidden dependency between
  files surprised the agent. Fix: a **navigation pointer** where the agent was when it needed it.
- **Guardrails** — the agent made a mistake a deterministic check would catch (lint, types, tests,
  a filesystem or import rule). Read the repo's own check commands and CI first. A repo with no
  guardrail (no pre-commit hook and no CI job running lint/typecheck/test) is itself a finding.
  Pick the rung by the *Repeats escalate to enforcement* ladder in `memory.remember` (structure,
  types, a check whose error names the fix, a test) and say why each higher rung does not work.
  The candidate names the past mistake (sha or transcript turn) the check must fail on.
- **Review rules** — the strict reviewer missed something, or flagged noise. Classify first: a
  **mechanical** violation (fixed pattern, banned API, import shape, file location) becomes a
  guardrail — review already treats lint-enforced issues as non-findings, so each check retires a
  class of findings for good. A **judgement call** (cross-file consistency, matching surrounding
  style) becomes a memory page the reviewer reaches.
- **Steering weight** — `AGENTS.md` (repo or global) or the `MEMORY.md` index carries rules that
  belong in a check or a memory page, or has grown large enough that its rules get skimmed.
- **No-ops** — a steering line or skill rule that changed no behaviour this session, or cost time
  and saved none. The fix is deleting it; a retro that removes a line is the cheapest kind.
- **Tool economy** — an expensive call that a narrower one would have answered: whole-file reads
  of archives, other runs' folders or a whole `PRODUCT.md` (outside the workflow's grounding
  tiers), verbose command output, a token-hungry custom tool, a slow command rerun on unchanged
  input.
- **Information access** — a crucial fact was out of the agent's reach: server logs, a read-only
  query against a third-party service, a doc behind auth.
- **Skill friction** — a skill's own contract caused the waste: a workflow phase that forced a
  reroute, a clarify gate that missed, a budget that split a run, a memory rule that misrouted.

## Destinations

| Change | Owner | How |
|---|---|---|
| Lesson, judgement-call review rule, memory-page pointer | `memory.remember` | In a live run: `[durable→memory]` lines in its `learnings.md`. Otherwise: hand it the approved items. A repeat bumps the page's occurrences. |
| Line added, moved or removed in repo `AGENTS.md` / `README.md` | `memory.remember` | Same routing; it owns canonical-doc edits. |
| Guardrail (new or rewired check) | `workflow` | `workflow todo Guardrail: <rung> — <the check> · must fail on <sha>` — a check is code and ships through a run. A matching memory page gets `Enforced by: pending — <that line>` via `memory.remember`. |
| Overbuild still in the code | `workflow` | `workflow todo Simplify: <what to delete or inline> · <evidence>` — behaviour unchanged, tests unchanged. |
| Reviewer missed a P0/P1 | `workflow` | `[durable→eval] code-review` line in a live run's `learnings.md` (the reviewed run's while it is open); wrap deposits it. |
| Skill change | `memory.remember` | `[durable→skill]` line: applied in its own commit, logged in `SKILL-IMPACT.md`, trialed. On a machine with no push-able `j-skills` clone it comes back as a skill-edit prompt for the human (`memory.remember` *Scope*); the receipt carries the prompt. |
| Trial evidence | `memory.remember` | Append the run and its for/against line to the trialing `SKILL-IMPACT.md` row. |
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
