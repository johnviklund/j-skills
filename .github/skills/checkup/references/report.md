# Checkup report

Print `## Workspace checkup — <repo> (<date>)`, then Skills, Memory, Docs, Workspace, Config
and Seats. Each ⚠️/🔴 finding is one line with evidence and a fix. A section with no such finding
is one ✅ line. If everything is healthy, say "✅ Workspace is healthy — nothing to act on".

Close in this order: numbered questions, at most three action cards, then the safe-fix line.
Omit questions or cards when there are none.

## Questions

Ask at most five questions, covering human-only decisions and facts no file establishes.
When severity or a fix depends on intent, tool use or whether a parked run is still wanted,
cite the evidence and ask; settle that finding after the answer. For example,
`.agents/skills/verify-APP` exists and `.claude/` is absent: ask whether Claude Code
is used here before calling its missing verify link 🔴.
Each question cites every path its finding rests on. Until answered, the section line says
"see Question N" with those paths; state the consequence only after the answer.

Use workflow `SKILL.md` §Talking to the human as the source for this default shape.
Put the ➡️ recommended option first and give every option a reason:

**1. <title>** <question and evidence, at most two sentences>
- ➡️ **a) <option>** — recommended: <why it wins>
- b) <option> — <cost or risk>

A seat promotion candidate or exam-set pruning is a human decision. Ask it above the cards.
Its card uses `Model: human · <the one edit>`, `Reset: no` and `Fallback: none`.
For a promotion, quote the exact new `ROUTING.md` row in the prompt; checkup never applies it.

## Action cards

An action
earns a row only when it names the cost of leaving it: what breaks (a skill silently not loaded,
a trial that cannot be judged, a check that never runs) or what every run pays (KB read per phase,
minutes per run). Findings that share one fix are one row (`memory.compact` for five stale pages).
A ⚠️ with no such cost, or a "worth a human skim", stays a line in its section and is never an
action.

A finding with a stated cost earns a card even when its fix needs a human call.
Its prompt tells the agent to propose the change and wait for approval.
For example, `TODO.md` over ~15 KB gets a `workflow todo` card that proposes what to archive.
Say "No action earns a card" only when no ⚠️/🔴 finding names a cost.

Group warnings that share one fix into one card and one prompt. For example, leftover
`## Execution state` blocks, tracked `.DS_Store` and loose files in finished runs get one
"tidy finished runs" card. Prioritize by the cost of leaving the finding; stop at three cards.

Default card shape, adapted from workflow `SKILL.md` §The closing card:

**▶ Next: <action>**

- **Why:** <finding, evidence and cost of leaving it>
- **Reset:** yes
- **Model:** <model> · <effort> · <context>
- **Fallback:** <model> · <effort>

**Run:**

```text
<command, repo, evidence paths/slugs/lines, and the result to produce>
```

Every agent action uses `Reset: yes`. The fenced prompt must work in a fresh session:
name the repo and the work, including the paths and evidence it needs, rather than referring
to "the findings above". For finished-run cleanup, name the runs and route unsaved value first.

## Skill to seat

Run `python3 <workflow>/scripts/next-step.py --key <key>` and copy its Model and Fallback lines
unchanged. `<workflow>` is the sibling workflow skill's absolute folder. The script reads its
`ROUTING.md`, including trial models and explicit fallback efforts; an error stops the action
card until resolved. This table selects the key:

| Skill or command | Key |
|---|---|
| `memory.*`, `workflow improve`, `workflow park` | `brainstorm` |
| `evals.run reviewer` | `review` |
| `verify.maintain`, `verify.create` | `execute:logic` |
| Other workflow commands except execute | The command, such as `todo`, `wrap`, `plan`, `review` or `realign` |
| `workflow execute` | Use the run's JSON `key`, including the patch severity override |

For execute, resolve the run per workflow `references/worktrees.md`, then run
`next-step.py <slug> --repo <checkout> --json` to read its key and blocker.
Human-only decisions use the human card rule above. A blocked run uses its `blocker.action`.
Follow the configured fallback chain when a model is unavailable and name the switch.

## Safe-fix line

End with the safe-fix status. If fixes were requested, offer only the next allowed fix and
wait for its approval. Otherwise print exactly `Safe fixes: none applied.` The allow-list in `SKILL.md`
still governs every fix.
Nothing follows the safe-fix line. It is the final line of the report.
