# Product-direction realignment — `workflow realign`

> ⚠️ **Invoke the `workflow` skill before acting on this file** — reading it raw bypasses the command's evidence and approval gates.

Seat: **strict reviewer** at high effort — mapping in `ROUTING.md`. This command re-derives
direction from shipped evidence and then argues against its own draft. The same seat owns that
skeptical reasoning and the resulting canonical-doc edits, but an edit is allowed only when it
matches an exact candidate redline the human approved.

`workflow realign` is a standalone, human-led alignment check. It does not advance or satisfy
any phase in the normal workflow state machine.

## Entry checks

Verify every precondition before creating or resuming the run artifact:

- The current directory is a Git repository and every tracked change **outside `.workflow/`**
  is committed. If not, refuse, name the condition or changed paths, and ask the human to run
  the command in the repository or finish that work first. `.workflow/` is excluded
  deliberately: it is this command's own scratch area, so a gate covering it would block the
  resume path below.
- `PRODUCT.md` exists. If it does not, refuse and point to `workflow bootstrap`; realignment
  needs an existing north-star document and shipped history to compare.
- No standard workflow run is active. Refuse when the phase-state artifacts would make
  `workflow status` recommend plan, execute, review, a patch cycle, or wrap. Completed
  historical artifacts that do not affect that calculation are harmless.
- An existing `.workflow/realign.md` with `Status: drafting` is resumable only when its recorded
  base is still an ancestor of `HEAD` and none of its in-scope canonical docs changed after the
  artifact was created. Otherwise set its status to `stale`, rename it to
  `.workflow/realign-stale-<YYYY-MM-DD>.md` so the fresh run's fixed path is free, tell the
  human what invalidated it, and begin a fresh run. `stale` is this command's own status value;
  the hub's `drafting` → `complete` vocabulary for phase artifacts is unchanged. A `complete`
  `realign.md` from an earlier run is spent — its durable value is already in Git and
  `WORKLOG.md` — so a fresh run overwrites it.

`DESIGN.md` is in scope only when it exists and describes a real UI. Treat a missing file or the
bootstrap two-line "no UI yet" stub as out of scope; do not create or expand it here. A
product-only run is complete in its own right.

## Open the receipt

Create `.workflow/realign.md` before mining evidence, with this five-line header:

```markdown
Command: workflow realign
Created: YYYY-MM-DD
Base:    <HEAD sha>
Inputs:  PRODUCT.md @ <HEAD sha>[; DESIGN.md @ <HEAD sha>]
Status:  drafting
```

The body records the in-scope docs, evidence baseline and commit range, sources inspected,
evidence-backed re-derivation, candidate queue, decisions, stress-test outcomes, accepted diff,
and final result. Keep it `drafting` until the queue has ended and the durable worklog receipt is
written; only then set it to `complete`.

## Mine a reproducible evidence window

Find the most recent commit touching each in-scope canonical doc. The baseline is the **oldest**
of those last-touch commits, and the evidence window runs from immediately after that commit
through `HEAD`. If an in-scope doc has no committed history, use the repository's root commit as
its baseline and record that the broader window was required.

Use only verifiable evidence:

- commits in the range, opening their diffs when subjects are not sufficient;
- relevant `WORKLOG.md` entries as leads, confirmed against a commit or shipped behavior;
- `TODO.md`'s Archived section as another lead, likewise confirmed;
- observable current behavior in source, tests, configuration, and user-facing documentation.

Every proposed statement or redline must cite a commit SHA, a worklog entry plus its confirming
SHA, or a precise shipped-behavior location. Omit claims with no evidence. Present contradictory
evidence as a conflict for the human instead of silently choosing a side.

## Re-derive and queue candidates

Re-derive the full shape of each in-scope document from that evidence:

- `PRODUCT.md`: current and desired end state, purpose, users, core objects, workflows,
  principles, vocabulary, and anti-goals.
- `DESIGN.md`: current UI behavior and durable UI/design-system direction.

Compare the result with the canonical text. Turn each meaningful delta into one independently
decidable candidate: add, remove, revise, or explicitly retain a contested claim. Each candidate
records its document and section, current text or an accurate absence marker, proposed exact
redline, evidence, and concise reason. Keep one semantic decision together; do not split it into
word-level cards or bundle unrelated decisions for convenience.

Write the entire initial candidate queue to the run artifact before review begins.

## Review one decision at a time

Present one candidate in plain language with its redline, evidence, reason, and the narrow choice:
**accept, edit, reject, or defer**. Wait for the answer before advancing. Restate an edited
redline and require a fresh accept-or-reject decision. Accepted text is only queued; do not alter
the canonical docs while any candidate remains undecided.

After the initial queue, run `references/direction-stress-tests.md` against the provisionally
accepted direction. If an answer would change that direction, create a new evidence-backed
redline card and put it through the same decision flow; never revise an earlier answer silently.

The human may stop at any point. Mark every unpresented or unresolved card deferred without
review, and give deferred cards no canonical-doc effect. The review ends only when every card is
accepted, rejected, or deferred.

## Apply, verify, and record

Apply only accepted exact redlines, as one coherent diff per in-scope document. Before each
canonical-doc commit, verify that every substantive change remains traceable to its cited
evidence in the run artifact, document ownership boundaries still hold, and the diff contains no
unrelated cleanup. Show the final diff and confirm it matches the approved cards. A new or
materially different edit must return to the human as a candidate.

Commit the canonical-doc changes first. Then append one bounded entry to `WORKLOG.md` using the
shape in `references/learning-worklog.md`; name `workflow realign`, the evidence range, the
approved directional change, and its commit SHA, then commit the worklog. When the completed
review accepts no redline, make no canonical-doc commit and use
`Commits: none — docs confirmed current` in the entry instead.

Scope both commits to their own paths; never sweep `.workflow/realign.md` into them. The worklog
must point into Git, never at that artifact, because wrap treats it as transient scratch. Once
the worklog receipt is committed, record the final outcome and set the artifact status to
`complete`.

## Boundaries and completion output

This command never writes `ROADMAP.md`, `TODO.md`, implementation code, or any workflow phase
artifact other than its own receipt. It neither invents direction nor turns deferred questions
into commitments.

Close by reporting the evidence range, decisions accepted/rejected/deferred, canonical-doc and
worklog commits, and whether the docs changed or were confirmed current. No next-step phase card
— this command doesn't change workflow state.
