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
`.agents/skills/verify-cx-intelligence` exists and `.claude/` is absent: ask whether Claude Code
is used here before calling its missing verify link 🔴.

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

Use the `ROUTING.md` read for the seat checks. This table selects a seat, never a model.
Read its model, effort, context and fallback from the seat and phase rows. A trial replaces
the primary, is marked `(trial)`, and uses the primary as fallback. Follow the fallback chain
when a model is unavailable and name the switch.

| Skill or command | Seat |
|---|---|
| `memory.*` | Brainstorm partner |
| `evals.run reviewer` | Strict reviewer |
| `verify.maintain`, `verify.create` | Default executor |
| `workflow brainstorm`, `workflow improve`, `workflow todo`, `workflow park`, `workflow wrap` | Brainstorm partner |
| `workflow plan`, `workflow review`, `workflow realign` | Strict reviewer |
| `workflow execute` | The next ticket's lane seat |

For `memory.*`, use the brainstorm phase row; for verify commands, use the execute logic row;
the reviewer exam uses the review row. Human-only decisions use the human card rule above.

## Safe-fix line

End with the safe-fix status. If fixes were requested, offer only the next allowed fix and
wait for its approval. Otherwise say "Safe fixes: none applied." The allow-list in `SKILL.md`
still governs every fix.
