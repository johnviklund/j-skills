# Plan — `workflow plan`

> ⚠️ Read through the `workflow` skill; the phase ends with its closing card.

Seat: **strict reviewer** (`ROUTING.md`) — a different vendor from the executor, so the audit
catches what the writer's model family would miss. Read-only sub-agents may gather facts.

Input: `.workflow/<slug>/brainstorm.md` — the brief — plus the code. Output: `plan.md`, a short
list of **tracer-bullet tickets**. Each ticket makes one or more behaviours work end to end and
proves it with tests, so the run is working software after every ticket instead of only at the end.

## 1. Audit the brief against the code

Open `plan.md` with `Status: drafting` now and append each part as it settles (shape in step 5).
Check every decision and seam in the brief against the real code: signatures, columns, config
keys, call sites, contract versions. Read `PRODUCT.md`/`DESIGN.md` by heading — only the
sections the brief and tickets touch — and, before a ticket that could contradict one, that section in full. Record what you learn as **findings** — one table row each:
`F# · what is true · what it changes`. A correction to the brief is a finding row and the correct
value is used in the tickets; the brief itself stays as written.

A question only the human can answer stops the phase before any ticket is written: ask it in the
decision shape from `SKILL.md` and wait. An older brief with no Behaviours section: derive the
behaviours from its scope, and include them in the step 4 round for the human to confirm.

## 2. Look for the prefactor

"Make the change easy, then make the easy change." If a small refactor (extract a function, move
a seam, add a missing test harness) would make the behaviour tickets simpler, it becomes the first
ticket — with its own tests proving behaviour is unchanged.

## 3. Slice into tickets

Every ticket is a **tracer bullet**:

- **Vertical.** It cuts a narrow, complete path through every layer the behaviour needs (schema,
  logic, API, UI, tests), so it is verifiable on its own. "All the models, then all the services,
  then all the endpoints" is horizontal slicing, and it hides integration errors until review.
- **Valuable.** It delivers at least one behaviour (B#) — or, for a prefactor, names the ticket it
  makes easy.
- **Small.** One seam, 1–4 acceptance lines, a diff the human can read in about five minutes, one
  fresh session to build. A ticket that needs a paragraph to describe is two tickets.
- **Testable.** Each acceptance line is one test (or, for an operator ticket, one receipt check)
  with a literal expected value, observed at the ticket's seam: "`parse_usage({'prompt_tokens': 12.0})` → `12`",
  not "handles token formats". Three rules keep the bar honest:
  - **One expected result.** A line with "or" passes on its weaker arm; if one arm is the failure
    an earlier ticket exists to exclude, the line is wrong. A later ticket never restates an
    earlier ticket's bar more loosely.
  - **Something positive.** Each ticket that delivers a behaviour has at least one line asserting
    the new answer is present — lineage, provenance or "old text gone" alone prove nothing.
  - **The reached surface.** The seam is where a user or consuming code actually sees the result:
    a UI line drives a rendered page or component with a live importer; a producer line validates
    the real output against the consumer's contract model, not the producer's own dict.
  - **Data that exists.** A `(live)` line observes a state the plan saw in the live data (a count,
    a named record from a read-only probe). A state with no live instance is checked at a non-live
    seam instead; the live line would otherwise end unverifiable.
  - **Inherited semantics.** A ticket adding a read surface over existing records asserts, per
    existing consumer, each state and label it honours (archived, knowledge/authority) and every
    error exit it must keep.

Give each ticket its **blocked-by** edges — the tickets that genuinely gate it — and its **lane**
(mechanical · logic · contract · operator), which picks the executor seat.

**Operator tickets** cover what the agent must not do itself: live or irreversible writes,
authorizations, paid runs above a ceiling, hosted consoles. The agent prepares the handoff (the
exact SQL or command, a dry-run first where one exists, and where the receipt goes). Each names its
**runner**: `agent after approval` when the repo's steering lets the agent run that step — the
human approves the exact bounded scope, the agent runs it and writes the receipt — otherwise
`human`, with a handoff short enough to paste as one block. Prefer `agent after approval` where
steering allows; a long human-run handoff is the signal to split the ticket. `Verify:` names the receipt file and the literal values it must show (`receipt: receipts/t4-ingest.txt —
rows_written 1,204 · errors 0`). A `(live)` behaviour is delivered by an operator ticket, blocked
by the tickets that build what it operates.

**Wide refactors are the exception.** A rename or retype that breaks every call site at once
cannot land green as one vertical slice. Sequence it as **expand–contract**: add the new form
beside the old; migrate call sites in batches (one ticket each, blocked by the expand); delete
the old form last, blocked by every batch.

Contracts move in lockstep, producer → validator → consumer; compatibility shims only when the
human asks.

## 4. Quiz the human on the breakdown

Show the tickets as a numbered list — `T# — <title> · delivers B# · blocked by T# · lane` — with
each ticket's acceptance lines indented under it, one line each. The acceptance lines are the bar
review will hold the code to, so the human sees them here; this is the one round where the chat
budget yields. Ask one decision: a) approve ➡️ · b) split T# · c) merge T# + T# · d) change an
acceptance line · e) other. Iterate until approved. The approval completes the phase.

## 5. Finish `plan.md` (≤ ~120 lines, ≤ 8 tickets)

Before setting `complete`, run every `Verify:` command as it stands and record its current result as
`pre:` — the command must execute. A test file the ticket will create doesn't exist yet: point the
command at it anyway and record `pre: new file` (the runner's "file or tests not found" exit is
expected here and only here); the runner itself must be found. A runner that is not found (exit 127)
is a plan defect. Operator tickets record `pre: no receipt`.

```markdown
Command: workflow plan <slug>
Created: <date>
Base:    <git sha>
Inputs:  .workflow/<slug>/brainstorm.md @ <its Base>
Status:  complete

Docs read: <PRODUCT.md §…, DESIGN.md §… — sections opened for this audit, or "none in scope">

## Execution state
<filled by execute>

## Findings
| # | What is true | What it changes |
|---|---|---|

## Tickets

### T1 — <title: the behaviour it makes work>
Delivers: B1, B3 · Blocked by: none · Lane: logic
Seam: <public interface the tests drive>
Accept:
- [ ] <input/situation> → <literal expected result> (B1)
- [ ] <input/situation> → <literal expected result> (B3)
Verify: `<test command scoped to the seam>` (pre: <e.g. 14 passed | new file>)
Skills: <path/to/SKILL.md> | none
Status: todo                              (todo · awaiting-human · done @ <sha>)

## Coverage
- Outcome → T# (the ticket whose acceptance observes it on the named surface)
- B1 → T1 · B2 → T2, T3 · …            (every behaviour; one with no ticket is a gap to fix)
- Out of scope: <item> → untouched      (every item)

## Risks
<≤3 lines: the riskiest ticket and why · what could break outside its files · the option not taken>

## TODO impacts
<the TODO.md items the brief names or seeded from → completed / partial / obsolete / conflicts; or
"none". A cheap adjacent item touching the same files is mentioned here as optional — never added
as a ticket. Plan does not open `TODO.md` or `ROADMAP.md`; wrap re-derives the rest.>

## Product doc impacts
<per PRODUCT.md, DESIGN.md, ROADMAP.md that exists: "no changes", or the statement this makes
untrue and its replacement; a settled principle this contradicts is marked ESCALATE>
```

Ticket order: prefactor first, then tickets whose outcome the human is most likely to want to
tweak (data model, interfaces, user-facing behaviour), mechanical tickets last. `Skills:` lists
resolved paths to skills that genuinely match the ticket (enumerate repo and installed skills by
frontmatter; most tickets need none) — the executor opens them by path on any CLI. A doc or
config ticket with no test runner verifies by content: assert that the new text is present and
count occurrences with `grep -o <pattern> <file> | wc -l`.

In chat: findings count (and any that changed scope), the ticket list line by line, ESCALATE
items, decisions needed — then the closing card. Next: `workflow execute <slug>`.
