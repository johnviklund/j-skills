# Execute — `workflow execute`

> ⚠️ Read through the `workflow` skill; the phase ends with its closing card.

Seat per ticket **lane**: mechanical → mechanical lane, logic → default executor, contract →
heavy executor, operator → default executor prepares (heavy if the handoff carries SQL or a
contract) and the human runs it (`ROUTING.md`). Execution writes, so it runs in the main session,
one ticket at a time.

**Which file:** `patch_plan.md` when it has a ticket not `done`; otherwise `plan.md`. That file is
the whole brief — the audit already happened, so execution builds what the tickets say.
Read `references/tests.md` once per session before the first test.

## Before the first ticket

1. **Ready:** the file's header says `Status: complete` (a `drafting` plan is unfinished — stop),
   and `python3 <skill>/scripts/check-run.py <slug>` (`<skill>` is the workflow skill's folder) reports no ERROR. An ERROR is a plan defect: stop and route to `workflow plan <slug>`
   (`workflow review <slug>` for a patch plan).
2. **Fresh:** `git diff --stat <its Base>..HEAD -- <every file its tickets name>` shows only commits
   listed as `T# @ <sha>` in `## Execution state`. Anything else → stop and route to
   `workflow plan <slug>` (or `workflow review <slug>` for a patch plan).
3. **Baseline:** run the build/test/lint commands from `AGENTS.md`'s *Verifying your work* block
   and note which failures already exist. No such block → ask for the commands.

## The ticket loop

Take the first ticket whose status is `todo` and whose blockers are all `done`. An `awaiting-human`
ticket with its receipt now present resumes at the receipt check (*Operator tickets* below);
without a receipt it is skipped.

1. **Read** its `Skills:` files — a precondition, not a hint. A path that doesn't resolve here →
   say so and ask.
2. **Red.** For each acceptance line, write the test at the ticket's seam and run `Verify:`;
   see it fail for the expected reason. (Mechanical and doc tickets skip red and verify by content.)
3. **Green.** Write the least code that passes, then run `Verify:`, the tests of every file you
   touched, and the typecheck/lint from the baseline.

   **UI tickets** — a ticket that changes what a user sees — also leave pictures. Before the first
   edit, screenshot each screen the ticket touches into `screens/<T#>-<screen>-before.jpg`; at
   green, the same view into `…-after.jpg`. Same route, viewport (1280×800) and data both times;
   crop to the changed region when the change is local; JPEG. When the repo has a verify skill
   (`.agents/skills/verify-*/`), take both with its control CLI (`doctor` first) and drive the
   screen by its feature file, so the shots are reproducible. Save them without opening them
   unless the ticket needs a visual check: an unopened image costs no context. Any visible change
   the ticket did not ask for is named in the report's `Noticed:` line, so it reaches review.
4. **Commit** the ticket, then persist before anything else: tick its acceptance lines, set
   `Status: done @ <sha>`, add `Writer: <model>` under it, and refresh `## Execution state`.
   **A UI ticket stops before its commit:** post the report below with `Commit: not yet` and one
   decision (a ➡️ looks right — commit · b change something: say what), and end the turn there with
   no closing card; on a it commits, persists and carries on at 6. No other ticket waits for approval — its tests and the
   cross-vendor review are the check, and the human doesn't read diffs.
5. **Report** in plain words, at most six lines:

   ```text
   T# · <title> · Commit: <sha | not yet>
   Changed: <what now works differently, in the user's terms — no code>
   Proof: <Verify pass/fail + the number that proves it>
   Mutation: <the line inverted> → red | none — doc or mechanical ticket
   Try it: none — nothing changes on screen; <the test or receipt that shows the change> | <start command (AGENTS.md), page or route, what to do, what to see> · screens/T#-…-after.jpg
   Noticed: none | <deviations, unrequested visible changes, an existing test's assertion changed, a helper written despite a reuse hit>
   ```
6. **Continue or stop.** A mechanical ticket rolls straight into the next ready ticket when that
   one is mechanical too. Every other ticket — and a mechanical run reaching a non-mechanical
   ticket — ends the turn with the closing card, `Reset: yes`, naming the next ticket's model: one
   ticket per session, so the context never fills and the human clears at every card. The state is
   on disk, so the reset costs nothing.

**Operator tickets** replace red → green with handoff → receipt, scaled to the ticket's `Risk:` class
(`phase-2-plan.md`): `cheap` is at most 20 lines with no dry-run and no script test; `costly` adds
the dry-run to run first and what it must show; `irreversible` adds a rollback line too. Write the
handoff into the run folder's `receipts/` — what to run, where (the console or CLI), and the receipt
path (also in `receipts/`) — commit it, set `Status: awaiting-human`, and close with the card routed to
the human: the one action, the handoff path, the receipt path. When the ticket's runner is `agent
after approval`, the card's one action is approving that exact scope; on approval the agent runs
it (dry-run first unless `cheap`, no paid retry without a new approval) and writes the receipt itself. On resume, read the receipt and
check every acceptance line against its literal values; a mismatch is a failed `Verify`, reported
like any other. A human-run step that failed gets a new receipt, never an edited one.
Receipts hold the numbers that prove an acceptance line (counts, checksums, the command and its
exit), not the data: bulk output stays outside the repo and the receipt names its path, row count
and checksum — later phases never read a receipt larger than a few KB.

**The ticket is the whole job.** Build what its acceptance lines describe, at its seam. Add a test
beyond the acceptance lines only when a mutation survives (`tests.md`). Everything else —
a nearby bug, a tempting refactor, a missing feature — is one line under `## Deviations` and the
ticket continues. **Existing tests keep their assertions:** changing or removing an assertion in a
test the ticket didn't create is a deviation, logged with the assertion count before and after,
and the report's `Noticed:` line names it.

**Acceptance lines are the contract.** When an acceptance line can't pass as written, or the plan
turns out wrong about the code, stop and report it: what the line says, what the code does, and
the conservative options. A test gets fixed only when the test itself is wrong, and that is a
deviation named in `Noticed:`. A `Verify` command that is not found (exit 127) is a failure.
A deviation that changes a number or assumption a plan Finding rests on (a worker count, a call
rate, a limit) means the plan is wrong about the code: stop and report the Finding and every later
target derived from it, so they are re-derived before an operator ticket spends money on them.
A one-item probe proves the path works, never the full run's runtime or cost.

## `## Execution state` (top of the live file, ≤ ~15 lines)

Current ticket and status · one `T# @ <sha>` line per committed ticket (the freshness check reads
these) · `writer: <model>` · baseline failures that pre-exist · exact
signatures, column names and contract versions in flight · uncommitted files · pending decision.
It is a re-ground block: after any reset or compaction, read it and the active ticket before
touching the next ticket. Re-open a skill or reference file only when its rules are gone from
context, and open only the `memory/` pages the ticket names rather than the whole `MEMORY.md`
index again.
A contract ticket mid-flight gets finished and committed before a reset.

**Name the running model from a record, not memory** — a model's recall of its own name lags its
version (GPT-6.1 Sol calls itself GPT-6). Read the exact ID the harness context states; else the
CLI config (Codex: `model` in `~/.codex/config.toml`; an in-session `/model` switch overrides it);
else ask. Write only the model, as `ROUTING.md`'s seat mapping names it (`GPT-6.1 Sol`,
`Opus 5.5`) — never the CLI, product or vendor. `Writer:` lines, worklog headings and the vendor
check in review all read it.

**Effort follows risk.** Before raising effort on a struggling ticket, sharpen its acceptance
lines — a clearer bar beats more thinking.

Append learnings to `learnings.md` as they happen (`references/learning-worklog.md`).

An autonomy loop (a CLI mode that drives every ticket without re-prompting) runs only when the
human asks for it, and UI and operator tickets still stop for the human inside it.

Close with the closing card from `SKILL.md`: the next ready ticket (`workflow execute <slug>`),
the human's action for an `awaiting-human` ticket (`**Model:** human · <the one action>`, **Reads:**
the handoff), or `workflow review <slug>` once every ticket is done.
