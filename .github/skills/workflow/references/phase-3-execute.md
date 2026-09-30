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

1. **Ready:** the file's header says `Status: complete` (a `drafting` plan is unfinished — stop).
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
4. **Show** the diff where `ROUTING.md` requires approval for this lane, as one decision
   (a ➡️ approve — commit and continue · b request changes), and end the turn there with no
   closing card; the reply approves.
5. **Commit** the ticket, then persist before starting the next one: tick its acceptance lines,
   set `Status: done @ <sha>`, add `Writer: <model>` under it, and refresh
   `## Execution state`.
6. **Report** in three lines: `T# — <title>` · `Verify: <pass/fail + the number that proves it>` ·
   `Commit: <sha>`.

**Operator tickets** replace red → green with handoff → receipt. Write the handoff into the run
folder — what to run, where (the console or CLI), the dry-run to run first and what it must show,
and the receipt path — commit it, set `Status: awaiting-human`, and close with the card routed to
the human: the one action, the handoff path, the receipt path. On resume, read the receipt and
check every acceptance line against its literal values; a mismatch is a failed `Verify`, reported
like any other. A human-run step that failed gets a new receipt, never an edited one.

Then the next ready ticket, in the same session while the context meter is under about half and
the ticket's lane maps to the model already running. Otherwise close with the card naming that
ticket's model — the state is on disk, so a reset costs nothing.

**The ticket is the whole job.** Build what its acceptance lines describe, at its seam. Extra
tests are welcome where they pin behaviour the acceptance lines already imply. Everything else —
a nearby bug, a tempting refactor, a missing feature — is one line under `## Deviations` and the
ticket continues. **Existing tests keep their assertions:** changing or removing an assertion in a
test the ticket didn't create is a deviation, logged with the assertion count before and after,
and the diff shows it to the human.

**Acceptance lines are the contract.** When an acceptance line can't pass as written, or the plan
turns out wrong about the code, stop and report it: what the line says, what the code does, and
the conservative options. A test gets fixed only when the test itself is wrong, and that is a
deviation the human sees. A `Verify` command that is not found (exit 127) is a failure.

## `## Execution state` (top of the live file, ≤ ~15 lines)

Current ticket and status · one `T# @ <sha>` line per committed ticket (the freshness check reads
these) · `writer: <model>` · baseline failures that pre-exist · exact
signatures, column names and contract versions in flight · uncommitted files · pending decision.
It is a re-ground block: after any reset or compaction, read it before touching the next ticket.
A contract ticket mid-flight gets finished and committed before a reset. `<model>` is read, not
recalled (*Name the running model from a record* in `SKILL.md`).

Append learnings to `learnings.md` as they happen (`references/learning-worklog.md`).

An autonomy loop (a CLI mode that drives every ticket without re-prompting) runs only when the
human asks for it, and contract tickets still get their diff approved inside it.

Close with the closing card from `SKILL.md`: the next ready ticket (`workflow execute <slug>`),
the human's action for an `awaiting-human` ticket, or `workflow review <slug>` once every ticket is done.
